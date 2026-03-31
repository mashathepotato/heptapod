"""
# run_wolfram_tool.py is a part of the HEPTAPOD package.
# Copyright (C) 2026 HEPTAPOD authors (see AUTHORS for details).
# HEPTAPOD is licensed under the GNU GPL v3 or later, see LICENSE for details.
# Please respect the MCnet Guidelines, see GUIDELINES for details.
"""
"""
RunWolframScript / RunWolframScriptBatch — BaseTools for executing
Mathematica/FeynCalc code.

RunWolframScript runs a single script. RunWolframScriptBatch runs multiple
scripts concurrently via a thread pool, returning all results in one call.
"""

import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Optional, List

from orchestral.tools.base.tool import BaseTool
from orchestral.tools.base.field_utils import RuntimeField, StateField

from .wolfram_runner import WolframRunner, WolframResult
from tools.logging.findings import append_finding


def _sanity_check_results(parsed: dict) -> list:
    """Check parsed Wolfram results for common issues.

    Returns a list of warning strings (empty if all looks good).
    """
    warnings = []
    numerical = parsed.get("numerical", {})
    symbolic = parsed.get("symbolic", {})

    for key, val in numerical.items():
        if not isinstance(val, (int, float)):
            continue
        # Negative width or cross section
        if any(tag in key.lower() for tag in ("width", "gamma", "sigma")):
            if val < 0:
                warnings.append(
                    f"{key} = {val:.6g} is negative — check signs or kinematics"
                )
        # NaN / Inf
        if val != val:  # NaN
            warnings.append(f"{key} is NaN — likely a division by zero or undefined limit")
        elif abs(val) == float("inf"):
            warnings.append(f"{key} is infinite — check for massless divergences or missing regulators")

    # Check symbolic results for unevaluated expressions
    for key, val in symbolic.items():
        if isinstance(val, str):
            if val.strip() == "$Failed" or "$Failed" in val:
                warnings.append(
                    f"SYMBOLIC_RESULT[{key}] is $Failed — the expression could not "
                    f"be evaluated (likely a failed Import or missing definition)"
                )
            if "Indeterminate" in val:
                warnings.append(f"SYMBOLIC_RESULT[{key}] contains Indeterminate")
            if "ComplexInfinity" in val:
                warnings.append(f"SYMBOLIC_RESULT[{key}] contains ComplexInfinity")
            if "$Aborted" in val:
                warnings.append(f"SYMBOLIC_RESULT[{key}] was aborted — consider increasing timeout")

    return warnings


def _build_result_output(result: WolframResult, base_directory: str = "",
                         script_label: str = "script") -> dict:
    """Build the lean JSON output dict from a WolframResult.

    Shared by RunWolframScript and RunWolframScriptBatch.
    """
    has_parsed = bool(result.parsed_results and (
        result.parsed_results.get("symbolic")
        or result.parsed_results.get("numerical")
        or result.parsed_results.get("latex")
    ))

    output = {
        "success": result.success,
        "script_path": result.script_path,
    }

    if result.results_path:
        output["results_path"] = result.results_path

    if result.parsed_results:
        pr = result.parsed_results
        # Keys match the sidecar JSON schema: "symbolic", "numerical", "latex"
        if pr.get("symbolic"):
            output["symbolic"] = pr["symbolic"]
        if pr.get("numerical"):
            output["numerical"] = pr["numerical"]
        if pr.get("latex"):
            output["latex"] = pr["latex"]

    if not has_parsed or not result.success:
        output["stdout"] = result.stdout

    if result.stderr and result.stderr.strip():
        output["stderr"] = result.stderr

    if not result.success:
        stderr_lines = (result.stderr or "").strip().splitlines()
        hint = None
        for line in reversed(stderr_lines[-20:]):
            if any(kw in line for kw in ("Error", "error", "Syntax", "failed")):
                hint = line.strip()
                break
        if hint:
            output["error_hint"] = hint
        elif stderr_lines:
            output["error_hint"] = stderr_lines[-1].strip()
        else:
            output["error_hint"] = (
                f"wolframscript exited with code {result.return_code} "
                f"(empty stdout/stderr — possible crash or timeout)"
            )

    if result.success and has_parsed:
        warnings = _sanity_check_results(result.parsed_results)
        if warnings:
            output["warnings"] = warnings

    if result.success and has_parsed and base_directory:
        try:
            entries = [f"Script: {script_label}"]
            pr = result.parsed_results
            sym_keys = list((pr.get("symbolic") or {}).keys())
            if sym_keys:
                entries.append(f"Results: {', '.join(sym_keys)}")
            if result.results_path:
                entries.append(f"Sidecar: {result.results_path}")
            append_finding(base_directory, f"FeynCalc: {script_label}", entries)
        except Exception:
            pass

    return output


class RunWolframScript(BaseTool):
    """
    Execute Mathematica/FeynCalc code via wolframscript.

    Saves the script as a standalone .wl file for reproducibility.
    Returns stdout with any structured results.

    The LLM can embed markers in Print[] statements for structured output:
        Print["SYMBOLIC_RESULT[name]: ", expr]
        Print["NUMERICAL_RESULT[name]: ", N[expr]]
        Print["STATUS: complete"]

    Inputs (runtime):
        code: Mathematica code to execute (string)
        script_name: Optional name for the saved .wl file (default: auto-generated)
        timeout: Timeout in seconds (default: 120)

    Returns:
        JSON with: success, stdout, stderr, script_path, execution_time_s,
        and parsed structured results if present.
    """

    # --- Runtime fields (from LLM at call time) ---
    code: Optional[str] = RuntimeField(
        default=None,
        description="Mathematica/FeynCalc code to execute. Provide this OR script_path, not both."
    )
    script_path: Optional[str] = RuntimeField(
        default=None,
        description="Path to an existing .wl script file to execute. Provide this OR code, not both."
    )
    script_name: Optional[str] = RuntimeField(
        default=None,
        description="Name for saved .wl script (without extension)"
    )
    timeout: int = RuntimeField(
        default=120,
        description="Timeout in seconds"
    )

    # --- State fields (configured at tool creation) ---
    base_directory: str = StateField(
        description="Working directory for script output"
    )
    wolframscript_path: str = StateField(
        description="Path to wolframscript executable"
    )

    def _run(self) -> str:
        """Execute Mathematica code from a string or an existing .wl file."""
        has_code = self.code and self.code.strip()
        has_path = self.script_path and self.script_path.strip()

        if not has_code and not has_path:
            return self.format_error(
                error="Missing Parameter",
                reason="Provide either 'code' (inline Mathematica) or 'script_path' (path to .wl file)"
            )

        runner = WolframRunner(
            wolframscript_path=self.wolframscript_path,
            timeout_sec=self.timeout,
        )

        # Run existing script file
        if has_path:
            result = runner.run_script(
                self.script_path,
                working_dir=self.base_directory,
            )
        else:
            # Determine save path for inline code
            save_path = None
            if self.script_name:
                from pathlib import Path
                name = self.script_name
                if not name.endswith(".wl"):
                    name += ".wl"
                save_path = str(
                    Path(self.base_directory) / "scripts" / name
                )

            result = runner.run_code(
                code=self.code,
                save_path=save_path,
                working_dir=self.base_directory,
            )

        output = _build_result_output(result, base_directory=self.base_directory,
                                       script_label=self.script_name or (
                                           self.script_path.rsplit("/", 1)[-1] if self.script_path else "script"
                                       ))
        return json.dumps(output, indent=2)


class RunWolframScriptBatch(BaseTool):
    """
    Execute multiple Mathematica/FeynCalc scripts concurrently.

    Runs all scripts in parallel via a thread pool and returns all results
    in a single response. Use this instead of multiple sequential
    RunWolframScript calls for systematic sweeps.

    Inputs (runtime):
        script_paths: List of paths to .wl script files to execute
        max_concurrent: Maximum number of concurrent wolframscript processes (default: 4)
        timeout: Timeout in seconds per script (default: 120)

    Returns:
        JSON with: total_scripts, succeeded, failed, total_time_s,
        and a results list (one entry per script, in input order).
    """

    # --- Runtime fields ---
    script_paths: List[str] = RuntimeField(
        description="List of paths to .wl script files to execute concurrently"
    )
    max_concurrent: int = RuntimeField(
        default=4,
        description="Maximum number of concurrent wolframscript processes"
    )
    timeout: int = RuntimeField(
        default=120,
        description="Timeout in seconds per script"
    )

    # --- State fields ---
    base_directory: str = StateField(
        description="Working directory for script output"
    )
    wolframscript_path: str = StateField(
        description="Path to wolframscript executable"
    )

    def _run(self) -> str:
        """Execute multiple scripts concurrently."""
        if not self.script_paths:
            return self.format_error(
                error="Missing Parameter",
                reason="Provide 'script_paths' with at least one .wl script path"
            )

        import time
        t0 = time.monotonic()

        # Run all scripts concurrently
        results_by_index: dict[int, WolframResult] = {}

        def _run_one(idx: int, path: str) -> tuple[int, WolframResult]:
            runner = WolframRunner(
                wolframscript_path=self.wolframscript_path,
                timeout_sec=self.timeout,
            )
            return idx, runner.run_script(path, working_dir=self.base_directory)

        with ThreadPoolExecutor(max_workers=self.max_concurrent) as pool:
            futures = {
                pool.submit(_run_one, i, p): i
                for i, p in enumerate(self.script_paths)
            }
            for future in as_completed(futures):
                idx, result = future.result()
                results_by_index[idx] = result

        total_time = time.monotonic() - t0

        # Build output in input order
        result_list = []
        succeeded = 0
        failed = 0
        for i in range(len(self.script_paths)):
            result = results_by_index[i]
            label = Path(self.script_paths[i]).name
            entry = _build_result_output(
                result,
                base_directory=self.base_directory,
                script_label=label,
            )
            result_list.append(entry)
            if result.success:
                succeeded += 1
            else:
                failed += 1

        output = {
            "total_scripts": len(self.script_paths),
            "succeeded": succeeded,
            "failed": failed,
            "total_time_s": round(total_time, 1),
            "results": result_list,
        }
        return json.dumps(output, indent=2)
