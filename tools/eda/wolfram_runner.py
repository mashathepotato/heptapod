"""
# wolfram_runner.py is a part of the HEPTAPOD package.
# Copyright (C) 2026 HEPTAPOD authors (see AUTHORS for details).
# HEPTAPOD is licensed under the GNU GPL v3 or later, see LICENSE for details.
# Please respect the MCnet Guidelines, see GUIDELINES for details.
"""
"""
Subprocess manager for wolframscript execution.

Handles running Mathematica code via wolframscript, capturing output,
and saving scripts for reproducibility.
"""

import json
import os
import re
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Dict, Any


@dataclass
class WolframResult:
    """Result from a wolframscript execution."""
    success: bool
    return_code: int
    stdout: str
    stderr: str
    execution_time_s: float
    script_path: str
    parsed_results: Dict[str, Any] = field(default_factory=dict)
    results_path: Optional[str] = None


# Markers the LLM can use in Print[] statements for structured output
RESULT_MARKERS = {
    "SYMBOLIC_RESULT": re.compile(r"SYMBOLIC_RESULT\[(.+?)\]:\s*(.+)"),
    "NUMERICAL_RESULT": re.compile(r"NUMERICAL_RESULT\[(.+?)\]:\s*(.+)"),
    "LATEX_RESULT": re.compile(r"LATEX_RESULT\[(.+?)\]:\s*(.+)"),
    "STATUS": re.compile(r"STATUS:\s*(.+)"),
}


def _clean_latex_symbols(tex: str) -> str:
    r"""Post-process TeXForm output to produce cleaner LaTeX.

    Mathematica's TeXForm wraps bare symbols in \text{}, e.g.
    \text{mf} for the mass of fermion f.  This function converts
    common patterns to proper LaTeX subscript notation.
    """
    # Specific known symbols (order matters: longer patterns first)
    _SYMBOL_MAP = {
        # Masses
        r"\text{mfbar}": r"m_{\bar{f}}",
        r"\text{mf1}": r"m_{f_1}",
        r"\text{mf2}": r"m_{f_2}",
        r"\text{mf}": r"m_f",
        r"\text{mS}": r"m_S",
        r"\text{mV}": r"m_V",
        r"\text{mH}": r"m_H",
        r"\text{mW}": r"m_W",
        r"\text{mZ}": r"m_Z",
        r"\text{mProp0}": r"m_{\text{prop}}",
        # Couplings
        r"\text{gS}": r"g_S",
        r"\text{gP}": r"g_P",
        r"\text{gV}": r"g_V",
        r"\text{gA}": r"g_A",
        r"\text{gL}": r"g_L",
        r"\text{gR}": r"g_R",
        # Generic coupling
        r"\text{yb}": r"y_b",
        r"\text{yt}": r"y_t",
        r"\text{ye}": r"y_e",
    }

    for pattern, replacement in _SYMBOL_MAP.items():
        tex = tex.replace(pattern, replacement)

    # Generic fallback: \text{XY} where X is a letter and Y is a letter/digit
    # e.g. \text{mX} → m_X, \text{gX} → g_X
    import re
    tex = re.sub(
        r"\\text\{([a-zA-Z])([a-zA-Z0-9]+)\}",
        lambda m: f"{m.group(1)}_{{{m.group(2)}}}" if len(m.group(2)) > 1 else f"{m.group(1)}_{m.group(2)}",
        tex,
    )

    return tex


def _parse_structured_output(stdout: str) -> Dict[str, Any]:
    """Extract structured results from wolframscript stdout.

    The LLM can embed markers in Print[] statements:
        Print["SYMBOLIC_RESULT[ampSquared]: ", result]
        Print["NUMERICAL_RESULT[width_GeV]: ", N[width]]
        Print["LATEX_RESULT[width]: ", TeXForm[width]]
        Print["STATUS: complete"]
    """
    parsed = {"symbolic": {}, "numerical": {}, "latex": {}, "status": None}

    for line in stdout.splitlines():
        line = line.strip()

        m = RESULT_MARKERS["SYMBOLIC_RESULT"].match(line)
        if m:
            parsed["symbolic"][m.group(1)] = m.group(2)
            continue

        m = RESULT_MARKERS["NUMERICAL_RESULT"].match(line)
        if m:
            try:
                parsed["numerical"][m.group(1)] = float(m.group(2))
            except ValueError:
                parsed["numerical"][m.group(1)] = m.group(2)
            continue

        m = RESULT_MARKERS["LATEX_RESULT"].match(line)
        if m:
            parsed["latex"][m.group(1)] = _clean_latex_symbols(m.group(2))
            continue

        m = RESULT_MARKERS["STATUS"].match(line)
        if m:
            parsed["status"] = m.group(1)

    return parsed


def _save_results_sidecar(script_path: str, parsed: Dict[str, Any]) -> Optional[str]:
    """Save parsed results as a JSON sidecar next to the .wl script.

    File is named ``{stem}_results.json`` in the same directory as the script.
    Returns the sidecar path on success, None on failure.
    """
    try:
        sp = Path(script_path)
        sidecar = sp.parent / f"{sp.stem}_results.json"
        # Only include non-empty result categories
        data = {}
        for key in ("symbolic", "numerical", "latex"):
            if parsed.get(key):
                data[key] = parsed[key]
        if parsed.get("status"):
            data["status"] = parsed["status"]
        data["script_path"] = str(sp)
        sidecar.write_text(json.dumps(data, indent=2))
        return str(sidecar)
    except Exception:
        return None


class WolframRunner:
    """Runs Mathematica code via wolframscript subprocess."""

    def __init__(
        self,
        wolframscript_path: str = None,
        timeout_sec: int = 120,
    ):
        if wolframscript_path is None:
            try:
                import config
                wolframscript_path = config.wolframscript_path
            except (ImportError, AttributeError):
                wolframscript_path = "wolframscript"

        self.wolframscript_path = wolframscript_path
        self.timeout_sec = timeout_sec

    def check_available(self) -> tuple:
        """Verify wolframscript is installed and FeynCalc is loadable.

        Returns:
            (available: bool, message: str)
        """
        # Check wolframscript exists
        try:
            proc = subprocess.run(
                [self.wolframscript_path, "-code", "Print[42]"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=30,
                check=False,
                text=True,
            )
            if proc.returncode != 0 or "42" not in proc.stdout:
                return (False, f"wolframscript failed: {proc.stderr.strip()}")
        except FileNotFoundError:
            return (False, f"wolframscript not found at: {self.wolframscript_path}")
        except subprocess.TimeoutExpired:
            return (False, "wolframscript timed out on basic test")

        # Check FeynCalc is loadable
        try:
            proc = subprocess.run(
                [self.wolframscript_path, "-code",
                 '<< FeynCalc`; Print["FeynCalc " <> $FeynCalcVersion]'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=60,
                check=False,
                text=True,
            )
            if proc.returncode != 0:
                return (False, f"FeynCalc failed to load: {proc.stderr.strip()}")
            return (True, proc.stdout.strip())
        except subprocess.TimeoutExpired:
            return (False, "FeynCalc loading timed out (60s)")

    def run_script(
        self,
        script_path: str,
        working_dir: str = None,
    ) -> WolframResult:
        """Run a .wl script file via wolframscript.

        Args:
            script_path: Path to the .wl file.
            working_dir: Working directory for the subprocess.

        Returns:
            WolframResult with execution details.
        """
        script_path = str(Path(script_path).resolve())
        if not Path(script_path).exists():
            return WolframResult(
                success=False,
                return_code=-1,
                stdout="",
                stderr=f"Script not found: {script_path}",
                execution_time_s=0.0,
                script_path=script_path,
            )

        cmd = [self.wolframscript_path, "-f", script_path]
        t0 = time.monotonic()

        try:
            proc = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=working_dir,
                timeout=self.timeout_sec,
                check=False,
                text=True,
            )
        except subprocess.TimeoutExpired:
            return WolframResult(
                success=False,
                return_code=-1,
                stdout="",
                stderr=f"Timeout after {self.timeout_sec}s",
                execution_time_s=time.monotonic() - t0,
                script_path=script_path,
            )
        except FileNotFoundError:
            return WolframResult(
                success=False,
                return_code=-1,
                stdout="",
                stderr=f"wolframscript not found: {self.wolframscript_path}",
                execution_time_s=time.monotonic() - t0,
                script_path=script_path,
            )

        elapsed = time.monotonic() - t0
        parsed = _parse_structured_output(proc.stdout or "")

        # Save results sidecar JSON alongside the .wl script
        results_path = None
        has_parsed = bool(
            parsed.get("symbolic") or parsed.get("numerical") or parsed.get("latex")
        )
        if proc.returncode == 0 and has_parsed:
            results_path = _save_results_sidecar(script_path, parsed)

        return WolframResult(
            success=(proc.returncode == 0),
            return_code=proc.returncode,
            stdout=proc.stdout or "",
            stderr=proc.stderr or "",
            execution_time_s=elapsed,
            script_path=script_path,
            parsed_results=parsed,
            results_path=results_path,
        )

    def run_code(
        self,
        code: str,
        save_path: str = None,
        working_dir: str = None,
    ) -> WolframResult:
        """Write code to a .wl file and run it.

        Args:
            code: Mathematica code to execute.
            save_path: Where to save the .wl file. If None, auto-generates
                       a path in working_dir/scripts/.
            working_dir: Base directory for script output.

        Returns:
            WolframResult with execution details.
        """
        if save_path is None:
            scripts_dir = Path(working_dir or ".") / "scripts"
            scripts_dir.mkdir(parents=True, exist_ok=True)
            # Generate unique name
            import hashlib
            code_hash = hashlib.md5(code.encode()).hexdigest()[:8]
            ts = int(time.time())
            save_path = str(scripts_dir / f"feyncalc_{ts}_{code_hash}.wl")

        save_path = str(Path(save_path).resolve())
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        Path(save_path).write_text(code)

        return self.run_script(save_path, working_dir=working_dir)
