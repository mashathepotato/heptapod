"""
# jsonl_to_latex_CC.py is a part of the HEPTAPOD package.
# Copyright (C) 2026 HEPTAPOD authors (see AUTHORS for details).
# HEPTAPOD is licensed under the GNU GPL v3 or later, see LICENSE for details.
# Please respect the MCnet Guidelines, see GUIDELINES for details.
"""
#!/usr/bin/env python3
"""Convert Claude Code JSONL conversation logs to LaTeX transcripts.

Emits LaTeX using the tcolorbox environments defined in agentic_diagrammatica.tex:
  agentuser, agentresponse, agenttool
with lstlisting code blocks (pythonstyle, mathematicastyle, jsonstyle).

Usage:
    python scripts/jsonl_to_latex.py INPUT.jsonl [options]

Options:
    --output FILE             Output .tex file (default: stdout)
    --max-tool-output N       Truncate tool output to N lines (default: 30)
    --skip-tools T1,T2,...    Skip tool calls with these names
    --keep-tools T1,T2,...    Only keep tool calls with these names (inverse of --skip-tools)
    --include-thinking        Include extended thinking blocks
    --excerpt START:END       Block index range START:END (0-based, after filtering)
    --strip-paths             Replace absolute paths with basenames
    --brief                   Show full detail only for first call of each tool
    --brief-context T1,T2,... Pre-populate seen tools (for multi-excerpt brief mode)
    --list-blocks             Print block index map and exit (no LaTeX output)
    --flowchart               Print compact tool-call sequence for flowchart scaffolding and exit
    --raw-user                Pass user messages through as raw LaTeX (no markdown conversion)
"""

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class ConversationBlock:
    kind: str  # "user", "assistant_text", "tool_call", "thinking"
    content: str = ""
    tool_name: str | None = None
    tool_input: dict | None = None
    tool_result: str | None = None
    tool_use_id: str | None = None


# ---------------------------------------------------------------------------
# JSONL parsing
# ---------------------------------------------------------------------------

SKIP_TYPES = {"system", "file-history-snapshot", "progress", "queue-operation"}


def parse_jsonl(path: str) -> list[dict]:
    entries = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            entries.append(json.loads(line))
    return entries


def extract_tool_result_text(content) -> str:
    """Extract plain text from a tool_result content field."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                parts.append(block["text"])
            elif isinstance(block, str):
                parts.append(block)
        return "\n".join(parts)
    return str(content)


def build_tool_results_index(entries: list[dict]) -> dict[str, str]:
    """First pass: index tool_result blocks by tool_use_id."""
    index = {}
    for entry in entries:
        if entry.get("type") != "user":
            continue
        msg = entry.get("message", {})
        content = msg.get("content", "") if isinstance(msg, dict) else ""
        if not isinstance(content, list):
            continue
        for block in content:
            if isinstance(block, dict) and block.get("type") == "tool_result":
                uid = block.get("tool_use_id", "")
                if uid:
                    index[uid] = extract_tool_result_text(block.get("content", ""))
    return index


def build_conversation(entries: list[dict], tool_results: dict[str, str],
                       include_thinking: bool = False) -> list[ConversationBlock]:
    """Second pass: build ordered conversation blocks."""
    blocks = []
    for entry in entries:
        etype = entry.get("type", "")
        if etype in SKIP_TYPES:
            continue

        msg = entry.get("message", {})
        if not isinstance(msg, dict):
            continue

        role = msg.get("role", "")
        content = msg.get("content", "")

        # --- User messages with string content ---
        if etype == "user" and role == "user" and isinstance(content, str) and content.strip():
            blocks.append(ConversationBlock(kind="user", content=content.strip()))
            continue

        # --- User messages with tool_result list → skip (already indexed) ---
        if etype == "user" and isinstance(content, list):
            continue

        # --- Assistant messages ---
        if etype == "assistant" and isinstance(content, list):
            for block in content:
                if not isinstance(block, dict):
                    continue
                btype = block.get("type", "")

                if btype == "thinking" and include_thinking:
                    text = block.get("thinking", "")
                    if text.strip():
                        blocks.append(ConversationBlock(kind="thinking", content=text.strip()))

                elif btype == "text":
                    text = block.get("text", "")
                    if text.strip():
                        blocks.append(ConversationBlock(
                            kind="assistant_text", content=text.strip()))

                elif btype == "tool_use":
                    uid = block.get("id", "")
                    blocks.append(ConversationBlock(
                        kind="tool_call",
                        tool_name=block.get("name", ""),
                        tool_input=block.get("input", {}),
                        tool_result=tool_results.get(uid, ""),
                        tool_use_id=uid,
                    ))

    return blocks


def merge_consecutive_text(blocks: list[ConversationBlock]) -> list[ConversationBlock]:
    """Merge consecutive assistant_text blocks."""
    merged = []
    for b in blocks:
        if (b.kind == "assistant_text" and merged
                and merged[-1].kind == "assistant_text"):
            merged[-1].content += "\n\n" + b.content
        else:
            merged.append(b)
    return merged


def apply_filters(blocks: list[ConversationBlock],
                  skip_tools: set[str],
                  keep_tools: set[str],
                  excerpt: tuple[int, int] | None) -> list[ConversationBlock]:
    """Filter blocks by tool skip/keep list and excerpt range."""
    # Filter tools (skip_tools and keep_tools are mutually exclusive)
    if skip_tools:
        filtered = []
        for b in blocks:
            if b.kind == "tool_call":
                name = clean_tool_name(b.tool_name or "")
                if name in skip_tools:
                    continue
            filtered.append(b)
        blocks = filtered

    if keep_tools:
        filtered = []
        for b in blocks:
            if b.kind == "tool_call":
                name = clean_tool_name(b.tool_name or "")
                if name not in keep_tools:
                    continue
            filtered.append(b)
        blocks = filtered

    # Apply excerpt range
    if excerpt is not None:
        start, end = excerpt
        blocks = blocks[start:end]

    return blocks


# ---------------------------------------------------------------------------
# Block listing (--list-blocks)
# ---------------------------------------------------------------------------

def print_block_list(blocks: list[ConversationBlock]) -> None:
    """Print a human-readable block index map to stderr."""
    for i, b in enumerate(blocks):
        if b.kind == "tool_call":
            name = clean_tool_name(b.tool_name or "")
            print(f"{i:4d}  {b.kind:15s}  {name}", file=sys.stderr)
        else:
            preview = b.content[:70].replace('\n', ' ')
            print(f"{i:4d}  {b.kind:15s}  {preview}", file=sys.stderr)
    print(f"\nTotal: {len(blocks)} blocks", file=sys.stderr)


def print_flowchart(blocks: list[ConversationBlock], jsonl_path: str | None = None) -> None:
    """Print a compact tool-call sequence for flowchart scaffolding.

    Groups consecutive tool calls as parallel (same assistant turn).
    Shows who acted (user/agent/tools) without content.
    Subagent tool calls shown indented beneath the Agent call.

    If jsonl_path is provided, subagent JSONL files are parsed to
    show their tool calls inline.
    """
    # Pre-parse subagent tool summaries if available
    subagent_summaries: dict[str, str] = {}
    if jsonl_path:
        import glob
        session_dir = os.path.splitext(jsonl_path)[0]
        subagent_dir = os.path.join(session_dir, "subagents")
        if os.path.isdir(subagent_dir):
            for sub_jsonl in sorted(glob.glob(os.path.join(subagent_dir, "*.jsonl"))):
                sub_entries = parse_jsonl(sub_jsonl)
                sub_stats = collect_session_stats(sub_entries, _find_subagents=False)
                sub_tools = sub_stats.get("tool_call_breakdown", {})
                parts = []
                for name, count in sub_tools.items():
                    if count > 1:
                        parts.append(f"{name} (x{count})")
                    else:
                        parts.append(name)
                subagent_summaries["Agent"] = " | ".join(parts)

    turn = 0
    i = 0
    while i < len(blocks):
        b = blocks[i]
        turn += 1

        if b.kind == "user":
            print(f"Turn {turn:3d}:  [user]", file=sys.stderr)
            i += 1

        elif b.kind == "assistant_text":
            print(f"Turn {turn:3d}:  [agent]", file=sys.stderr)
            i += 1

        elif b.kind == "tool_call":
            # Collect all consecutive tool calls (parallel dispatch)
            tool_counts: dict[str, int] = {}
            tool_order: list[str] = []
            while i < len(blocks) and blocks[i].kind == "tool_call":
                name = clean_tool_name(blocks[i].tool_name or "")
                if name not in tool_counts:
                    tool_order.append(name)
                    tool_counts[name] = 0
                tool_counts[name] += 1
                i += 1
            parts = []
            has_subagent = False
            for name in tool_order:
                count = tool_counts[name]
                if count > 1:
                    parts.append(f"{name} (x{count})")
                else:
                    parts.append(name)
                if name == "Agent":
                    has_subagent = True
            print(f"Turn {turn:3d}:  {' | '.join(parts)}", file=sys.stderr)
            # Show subagent tools indented
            if has_subagent and "Agent" in subagent_summaries:
                print(f"              └─ [subagent] {subagent_summaries['Agent']}", file=sys.stderr)

        else:
            i += 1


# ---------------------------------------------------------------------------
# Tool name cleaning
# ---------------------------------------------------------------------------

_MCP_PREFIX_RE = re.compile(r'^mcp__\w+__')


def clean_tool_name(name: str) -> str:
    """Strip any mcp__<server>__ prefix (e.g. mcp__heptapod__Tool → Tool)."""
    return _MCP_PREFIX_RE.sub('', name)


# ---------------------------------------------------------------------------
# Session statistics (--stats)
# ---------------------------------------------------------------------------

def collect_subagent_stats(jsonl_path: str) -> list[dict]:
    """Find and collect stats for any subagent JSONL files."""
    import glob

    # Subagents live in {session_id}/subagents/*.jsonl
    session_dir = os.path.splitext(jsonl_path)[0]
    subagent_dir = os.path.join(session_dir, "subagents")
    if not os.path.isdir(subagent_dir):
        return []

    subagent_stats = []
    for sub_jsonl in sorted(glob.glob(os.path.join(subagent_dir, "*.jsonl"))):
        sub_entries = parse_jsonl(sub_jsonl)
        stats = collect_session_stats(sub_entries, _find_subagents=False)

        # Try to find the subagent description from the parent
        agent_id = os.path.splitext(os.path.basename(sub_jsonl))[0]
        stats["agent_id"] = agent_id
        stats["jsonl_path"] = sub_jsonl
        subagent_stats.append(stats)

    return subagent_stats


def collect_session_stats(entries: list[dict], _find_subagents: bool = True) -> dict:
    """Collect session-level statistics from JSONL entries."""
    from datetime import datetime

    tool_calls: dict[str, int] = {}
    total_duration_ms = 0
    timestamps: list[str] = []
    n_assistant = 0
    n_user_prompts = 0
    total_input_tokens = 0
    total_output_tokens = 0
    total_cache_creation = 0
    total_cache_read = 0
    model_name = None
    cc_version = None
    session_id = None
    service_tier = None
    cwd = None

    for entry in entries:
        etype = entry.get("type", "")
        ts = entry.get("timestamp")
        if ts:
            timestamps.append(ts)
        dur = entry.get("durationMs")
        if dur and isinstance(dur, (int, float)):
            total_duration_ms += dur

        # Extract session metadata from early entries
        if cc_version is None and entry.get("version"):
            cc_version = entry["version"]
        if session_id is None and entry.get("sessionId"):
            session_id = entry["sessionId"]
        if cwd is None and entry.get("cwd"):
            cwd = entry["cwd"]

        if etype == "assistant":
            n_assistant += 1
            msg = entry.get("message", {})
            if isinstance(msg, dict):
                # Model and service tier (from first assistant message)
                if model_name is None and msg.get("model"):
                    model_name = msg["model"]
                usage = msg.get("usage", {})
                if usage:
                    total_input_tokens += usage.get("input_tokens", 0)
                    total_output_tokens += usage.get("output_tokens", 0)
                    total_cache_creation += usage.get("cache_creation_input_tokens", 0)
                    total_cache_read += usage.get("cache_read_input_tokens", 0)
                    if service_tier is None:
                        service_tier = usage.get("service_tier")

                content = msg.get("content", [])
                if isinstance(content, list):
                    for c in content:
                        if isinstance(c, dict) and c.get("type") == "tool_use":
                            name = clean_tool_name(c.get("name", "unknown"))
                            tool_calls[name] = tool_calls.get(name, 0) + 1

        if etype == "user":
            msg = entry.get("message", {})
            if isinstance(msg, dict) and msg.get("role") == "user":
                content = msg.get("content", "")
                if isinstance(content, str) and content.strip():
                    n_user_prompts += 1

    # Session wall-clock time
    session_wall_clock_min = 0.0
    session_start = None
    session_end = None
    if timestamps:
        try:
            t0 = datetime.fromisoformat(timestamps[0].replace("Z", "+00:00"))
            t1 = datetime.fromisoformat(timestamps[-1].replace("Z", "+00:00"))
            session_wall_clock_min = (t1 - t0).total_seconds() / 60
            session_start = timestamps[0]
            session_end = timestamps[-1]
        except (ValueError, TypeError):
            pass

    effective_input = total_input_tokens + total_cache_creation + total_cache_read

    return {
        "model": model_name,
        "claude_code_version": cc_version,
        "session_id": session_id,
        "service_tier": service_tier,
        "working_directory": cwd,
        "session_wall_clock_min": round(session_wall_clock_min, 1),
        "llm_inference_time_s": round(total_duration_ms / 1000, 1),
        "llm_inference_time_min": round(total_duration_ms / 60000, 1),
        "user_prompts": n_user_prompts,
        "assistant_turns": n_assistant,
        "total_tool_calls": sum(tool_calls.values()),
        "tool_call_breakdown": dict(
            sorted(tool_calls.items(), key=lambda x: -x[1])),
        "session_start": session_start,
        "session_end": session_end,
        "total_messages": len(entries),
        "output_tokens": total_output_tokens,
        "input_tokens_uncached": total_input_tokens,
        "cache_creation_tokens": total_cache_creation,
        "cache_read_tokens": total_cache_read,
        "effective_input_tokens": effective_input,
        "total_tokens": effective_input + total_output_tokens,
    }


def print_session_stats(entries: list[dict], output_prefix: str | None = None,
                        jsonl_path: str | None = None) -> None:
    """Print session statistics to stderr and optionally save to files.

    If output_prefix is given, saves:
      - {prefix}_stats.json  (machine-readable)
      - {prefix}_stats.txt   (human-readable)
    """
    stats = collect_session_stats(entries)

    # Find subagents if jsonl_path provided
    subagent_stats_list = []
    if jsonl_path:
        subagent_stats_list = collect_subagent_stats(jsonl_path)
        if subagent_stats_list:
            stats["subagents"] = subagent_stats_list

    # Human-readable summary
    lines = []
    if stats.get("model"):
        lines.append(f"Model:                   {stats['model']}")
    if stats.get("claude_code_version"):
        lines.append(f"Claude Code version:     {stats['claude_code_version']}")
    if stats.get("service_tier"):
        lines.append(f"Service tier:            {stats['service_tier']}")
    if stats.get("session_id"):
        lines.append(f"Session ID:              {stats['session_id']}")
    if stats.get("working_directory"):
        lines.append(f"Working directory:       {stats['working_directory']}")
    if any(stats.get(k) for k in ["model", "claude_code_version", "session_id"]):
        lines.append("")
    lines.append(f"Session wall-clock time: {stats['session_wall_clock_min']} min")
    lines.append(f"LLM inference time:      {stats['llm_inference_time_s']} s "
                 f"({stats['llm_inference_time_min']} min)")
    lines.append(f"User prompts:            {stats['user_prompts']}")
    lines.append(f"Assistant turns:          {stats['assistant_turns']}")
    lines.append(f"Total tool calls:         {stats['total_tool_calls']}")
    lines.append("")
    lines.append("Token usage:")
    lines.append(f"  Output tokens:           {stats['output_tokens']:>12,}")
    lines.append(f"  Cache creation tokens:   {stats['cache_creation_tokens']:>12,}")
    lines.append(f"  Cache read tokens:       {stats['cache_read_tokens']:>12,}")
    lines.append(f"  Uncached input tokens:   {stats['input_tokens_uncached']:>12,}")
    lines.append(f"  Effective input tokens:  {stats['effective_input_tokens']:>12,}")
    lines.append(f"  Total tokens:            {stats['total_tokens']:>12,}")
    lines.append("")
    lines.append("Tool call breakdown:")
    for name, count in stats["tool_call_breakdown"].items():
        lines.append(f"  {name:40s} {count:3d}")

    # Subagent summary
    if subagent_stats_list:
        lines.append("")
        lines.append(f"Subagents: {len(subagent_stats_list)}")
        for i, sub in enumerate(subagent_stats_list):
            lines.append(f"  Subagent {i+1} ({sub.get('agent_id', 'unknown')[:20]}...):")
            if sub.get("model"):
                lines.append(f"    Model:         {sub['model']}")
            lines.append(f"    Tool calls:    {sub['total_tool_calls']}")
            lines.append(f"    Turns:         {sub['assistant_turns']}")
            lines.append(f"    Output tokens: {sub['output_tokens']:,}")
            lines.append(f"    Wall clock:    {sub['session_wall_clock_min']} min")
            sub_tools = sub.get("tool_call_breakdown", {})
            if sub_tools:
                lines.append(f"    Tools: {', '.join(f'{n} (x{c})' for n, c in sub_tools.items())}")

    summary = "\n".join(lines)
    print(summary, file=sys.stderr)

    # Save files if prefix given
    if output_prefix:
        json_path = f"{output_prefix}_stats.json"
        txt_path = f"{output_prefix}_stats.txt"

        with open(json_path, "w") as f:
            json.dump(stats, f, indent=2)
        print(f"\nSaved: {json_path}", file=sys.stderr)

        with open(txt_path, "w") as f:
            f.write(summary + "\n")
        print(f"Saved: {txt_path}", file=sys.stderr)


# ---------------------------------------------------------------------------
# LaTeX escaping & Markdown→LaTeX conversion
# ---------------------------------------------------------------------------

# Math-mode-only LaTeX commands that need $...$ wrapping when found outside math
_MATH_ONLY_CMDS = {
    'to', 'sim', 'approx', 'times', 'pm', 'mp', 'leq', 'geq',
    'll', 'gg', 'propto', 'equiv', 'neq', 'infty', 'rightarrow',
    'leftarrow', 'Rightarrow', 'Leftarrow', 'cdot', 'ldots', 'cdots',
    # Greek letters (common in HEP)
    'alpha', 'beta', 'gamma', 'delta', 'epsilon', 'varepsilon',
    'zeta', 'eta', 'theta', 'vartheta', 'iota', 'kappa', 'lambda',
    'mu', 'nu', 'xi', 'pi', 'varpi', 'rho', 'varrho', 'sigma',
    'varsigma', 'tau', 'upsilon', 'phi', 'varphi', 'chi', 'psi', 'omega',
    'Gamma', 'Delta', 'Theta', 'Lambda', 'Xi', 'Pi', 'Sigma',
    'Upsilon', 'Phi', 'Psi', 'Omega',
    # Common math operators
    'partial', 'nabla', 'sqrt', 'int', 'sum', 'prod', 'otimes', 'oplus',
    'dagger', 'bar', 'hat', 'tilde', 'vec', 'dot', 'ddot',
}

# Commands that take a brace argument and should be absorbed into math mode
_MATH_ARG_CMDS = {'bar', 'hat', 'tilde', 'vec', 'dot', 'ddot', 'sqrt', 'frac',
                   'overline', 'underline', 'mathbf', 'mathrm', 'mathcal'}


def _strip_markdown_escapes(text: str) -> str:
    """Remove markdown backslash escapes (e.g. \\_ → _, \\* → *)."""
    return re.sub(r'\\([_*#|`\[\](){}])', r'\1', text)


def _scan_math_extent(text: str, start: int) -> int:
    """From position start (at a \\cmd in _MATH_ONLY_CMDS), scan forward to find
    the end of a contiguous math expression.

    This handles patterns like \\Gamma(A \\to BC), \\mu^+, \\bar{\\nu}_\\mu, etc.
    Returns end position (exclusive).
    """
    i = start
    # Skip the initial \cmd
    i += 1  # skip backslash
    while i < len(text) and text[i].isalpha():
        i += 1

    # Now greedily extend the math expression
    while i < len(text):
        ch = text[i]

        # Brace group: absorb entirely (e.g. \bar{f}, \frac{a}{b})
        if ch == '{':
            depth = 1
            i += 1
            while i < len(text) and depth > 0:
                if text[i] == '{':
                    depth += 1
                elif text[i] == '}':
                    depth -= 1
                i += 1
            continue

        # Parenthesized expression containing \commands → math parens
        if ch == '(':
            close = text.find(')', i + 1)
            if close != -1 and '\\' in text[i + 1:close]:
                i = close + 1
                continue
            break

        # Sub/superscript
        if ch in '^_':
            i += 1
            if i < len(text) and text[i] == '{':
                depth = 1
                i += 1
                while i < len(text) and depth > 0:
                    if text[i] == '{':
                        depth += 1
                    elif text[i] == '}':
                        depth -= 1
                    i += 1
            elif i < len(text) and text[i] == '\\':
                j = i + 1
                while j < len(text) and text[j].isalpha():
                    j += 1
                i = j
            elif i < len(text):
                i += 1  # single char sub/super
            continue

        # Another LaTeX command
        if ch == '\\' and i + 1 < len(text) and text[i + 1].isalpha():
            j = i + 1
            while j < len(text) and text[j].isalpha():
                j += 1
            i = j
            continue

        # Single letter variable (not start of a multi-letter word)
        if ch.isalpha() and (i + 1 >= len(text) or not text[i + 1].isalpha()):
            i += 1
            continue

        # Math operators, digits, punctuation within expressions
        if ch in '+-=*/,.!\'':
            i += 1
            continue

        # Space: only continue if followed by math-like content
        if ch == ' ':
            j = i + 1
            while j < len(text) and text[j] == ' ':
                j += 1
            if j < len(text) and text[j] in '\\(^_{+-=':
                i = j
                continue
            if j < len(text) and text[j].isalpha() and (j + 1 >= len(text) or not text[j + 1].isalpha()):
                i = j
                continue
            break

        # Anything else ends the math expression
        break

    return i


def escape_latex(text: str) -> str:
    """Escape LaTeX special characters in non-math text.

    Preserves LaTeX commands (backslash + alpha sequence) like \\to, \\gamma, etc.
    Wraps math-only commands (and their adjacent math content) in $...$.
    """
    result = []
    i = 0
    while i < len(text):
        ch = text[i]
        if ch == '\\' and i + 1 < len(text) and text[i + 1].isalpha():
            # LaTeX command — preserve backslash + command name
            j = i + 1
            while j < len(text) and text[j].isalpha():
                j += 1
            cmd_name = text[i + 1:j]
            if cmd_name in _MATH_ONLY_CMDS or cmd_name in _MATH_ARG_CMDS:
                # Scan forward to find the full math expression extent
                extent = _scan_math_extent(text, i)
                math_content = text[i:extent]
                result.append('$' + math_content + '$')
                i = extent
            else:
                result.append(text[i:j])
                i = j
        elif ch == '\\':
            result.append(r'\textbackslash{}')
            i += 1
        elif ch == '&':
            result.append(r'\&')
            i += 1
        elif ch == '%':
            result.append(r'\%')
            i += 1
        elif ch == '$':
            result.append(r'\$')
            i += 1
        elif ch == '#':
            result.append(r'\#')
            i += 1
        elif ch == '_':
            result.append(r'\_')
            i += 1
        elif ch == '{':
            result.append(r'\{')
            i += 1
        elif ch == '}':
            result.append(r'\}')
            i += 1
        elif ch == '~':
            # Already handled by pre-pass for "approximately" cases.
            # Remaining ~ chars are non-breaking spaces — keep as LaTeX ~.
            result.append('~')
            i += 1
        elif ch == '^':
            result.append(r'\textasciicircum{}')
            i += 1
        else:
            result.append(ch)
            i += 1
    return ''.join(result)


def _split_math_regions(text: str) -> list[tuple[str, bool]]:
    """Split text into (fragment, is_math) tuples.

    Handles $...$ and $$...$$ (but not \\( \\) since those are already LaTeX).
    """
    parts = []
    # Match $$...$$ or $...$  (non-greedy, no newlines inside single $)
    pattern = re.compile(r'(\$\$[\s\S]*?\$\$|\$[^\n$]+?\$)')
    last = 0
    for m in pattern.finditer(text):
        if m.start() > last:
            parts.append((text[last:m.start()], False))
        parts.append((m.group(0), True))
        last = m.end()
    if last < len(text):
        parts.append((text[last:], False))
    return parts


def _convert_inline_code(text: str) -> str:
    """Convert `code` to \\texttt{code}.

    Called after escape_latex, so content is already escaped.
    """
    def _repl(m):
        code = m.group(1)
        return r'\texttt{' + code + '}'
    return re.sub(r'`([^`\n]+?)`', _repl, text)


def _convert_bold(text: str) -> str:
    """Convert **bold** to \\textbf{bold}."""
    def _repl(m):
        return r'\textbf{' + m.group(1) + '}'
    return re.sub(r'\*\*(.+?)\*\*', _repl, text)


def _convert_italic(text: str) -> str:
    """Convert *italic* to \\textit{italic} (but not inside bold).

    Skips conversion if the matched content contains '\\&' (escaped table
    separator — would break tabular) or spans across math regions.
    """
    def _repl(m):
        inner = m.group(1)
        # Don't wrap if content contains table separator — breaks tabular
        # At this point & is already escaped to \&
        if r'\&' in inner or '&' in inner:
            return m.group(0)
        # Don't wrap if it spans a math region ($...$)
        if inner.count('$') >= 2:
            return m.group(0)
        return r'\textit{' + inner + '}'
    return re.sub(r'(?<!\*)\*([^*\n]+?)\*(?!\*)', _repl, text)


def _detect_lstlisting_style(lang: str) -> str:
    """Map fenced code block language to lstlisting style."""
    lang = lang.lower().strip()
    if lang in ("python", "py"):
        return "pythonstyle"
    if lang in ("mathematica", "wolfram", "wl"):
        return "mathematicastyle"
    if lang in ("json", "jsonc"):
        return "jsonstyle"
    return "pythonstyle"  # default


def _convert_markdown_table(text: str) -> str:
    """Convert markdown tables to LaTeX tabular."""
    lines = text.split('\n')
    result_lines = []
    i = 0
    while i < len(lines):
        # Detect table: line with | ... | followed by separator |---|
        if (i + 1 < len(lines)
                and '|' in lines[i]
                and re.match(r'\s*\|[\s\-:|]+\|\s*$', lines[i + 1])):
            # Parse header
            header_cells = [c.strip() for c in lines[i].split('|')[1:-1]]
            ncols = len(header_cells)
            col_spec = '|' + 'l|' * ncols

            table_lines = []
            table_lines.append(f'\\begin{{tabular}}{{{col_spec}}}')
            table_lines.append('\\hline')
            table_lines.append(' & '.join(header_cells) + ' \\\\')
            table_lines.append('\\hline')

            # Skip separator
            i += 2
            # Parse data rows
            while i < len(lines) and '|' in lines[i] and lines[i].strip().startswith('|'):
                cells = [c.strip() for c in lines[i].split('|')[1:-1]]
                # Pad or trim to ncols
                cells = (cells + [''] * ncols)[:ncols]
                table_lines.append(' & '.join(cells) + ' \\\\')
                i += 1
            table_lines.append('\\hline')
            table_lines.append('\\end{tabular}')
            result_lines.append('\n'.join(table_lines))
        else:
            result_lines.append(lines[i])
            i += 1
    return '\n'.join(result_lines)


def _convert_lists(text: str) -> str:
    """Convert markdown lists to itemize/enumerate.

    Handles "loose" markdown lists (blank lines between items) by looking
    ahead to see if the next non-blank line is still a list item.
    """
    lines = text.split('\n')
    result = []
    in_list = None  # "itemize" or "enumerate"

    def _is_list_item(line):
        return (re.match(r'^(\s*)[-*]\s+(.+)$', line) or
                re.match(r'^(\s*)\d+\.\s+(.+)$', line))

    def _next_nonblank(idx):
        """Return next non-blank line after idx, or None."""
        for j in range(idx + 1, len(lines)):
            if lines[j].strip():
                return lines[j]
        return None

    for i, line in enumerate(lines):
        ul_match = re.match(r'^(\s*)[-*]\s+(.+)$', line)
        ol_match = re.match(r'^(\s*)\d+\.\s+(.+)$', line)

        if ul_match:
            if in_list != "itemize":
                if in_list:
                    result.append(f'\\end{{{in_list}}}')
                result.append('\\begin{itemize}')
                in_list = "itemize"
            result.append(f'  \\item {ul_match.group(2)}')
        elif ol_match:
            if in_list != "enumerate":
                if in_list:
                    result.append(f'\\end{{{in_list}}}')
                result.append('\\begin{enumerate}')
                in_list = "enumerate"
            result.append(f'  \\item {ol_match.group(2)}')
        else:
            if in_list and line.strip() == '':
                # Blank line — check if list continues after it
                nxt = _next_nonblank(i)
                if nxt and _is_list_item(nxt):
                    continue  # skip blank line, list continues
                else:
                    result.append(f'\\end{{{in_list}}}')
                    in_list = None
            elif in_list and line.strip():
                result.append(f'\\end{{{in_list}}}')
                in_list = None
                result.append(line)
            else:
                result.append(line)

    if in_list:
        result.append(f'\\end{{{in_list}}}')

    return '\n'.join(result)


def markdown_to_latex(text: str) -> str:
    """Convert markdown text to LaTeX, preserving math regions."""
    # Step 0a: Sanitize Unicode for LaTeX text
    text = sanitize_for_text(text)
    # Step 0b: Strip markdown backslash escapes (\_  →  _, \*  →  *, etc.)
    text = _strip_markdown_escapes(text)

    # Step 1: Handle fenced code blocks FIRST (before escaping)
    code_blocks = []

    def _save_code_block(m):
        lang = m.group(1) or ""
        code = m.group(2)
        style = _detect_lstlisting_style(lang)
        placeholder = f"%%CODEBLOCK{len(code_blocks)}%%"
        code_blocks.append(
            f"\\begin{{lstlisting}}[style={style}]\n{code}\n\\end{{lstlisting}}")
        return placeholder

    text = re.sub(r'```(\w*)\n([\s\S]*?)```', _save_code_block, text)

    # Step 1.5: Replace ~ meaning "approximately" with $\sim$ before splitting.
    # Patterns: "~500", "~$10^5$", "~ 500", "~ $10^5$" after space/( or at SOL.
    # word~$n$ is a non-breaking space — handled by escape_latex as LaTeX ~.
    text = re.sub(r'(?<=[\s(])~\s*(?=\$|\d)', r'$\\sim$', text)
    text = re.sub(r'^~\s*(?=\$|\d)', r'$\\sim$', text, flags=re.MULTILINE)

    # Step 2: Split into math and non-math regions, escape only non-math
    parts = _split_math_regions(text)

    converted_parts = []
    for fragment, is_math in parts:
        if is_math:
            converted_parts.append(fragment)
        else:
            converted_parts.append(escape_latex(fragment))

    text = ''.join(converted_parts)

    # Step 3: Convert markdown formatting on full text (spans math regions OK)
    text = _convert_bold(text)
    text = _convert_italic(text)
    text = _convert_inline_code(text)

    # Step 4: Convert tables
    text = _convert_markdown_table(text)

    # Step 5: Convert lists
    text = _convert_lists(text)

    # Step 6: Restore code blocks
    for i, block in enumerate(code_blocks):
        text = text.replace(f"%%CODEBLOCK{i}%%", block)

    # Step 7: Convert markdown headings
    text = re.sub(r'^####\s+(.+)$', r'\\paragraph{\1}', text, flags=re.MULTILINE)
    text = re.sub(r'^###\s+(.+)$', r'\\subsubsection*{\1}', text, flags=re.MULTILINE)
    text = re.sub(r'^##\s+(.+)$', r'\\subsection*{\1}', text, flags=re.MULTILINE)
    text = re.sub(r'^#\s+(.+)$', r'\\section*{\1}', text, flags=re.MULTILINE)

    return text


# ---------------------------------------------------------------------------
# Path stripping
# ---------------------------------------------------------------------------

_PATH_RE = re.compile(r'/(?:Users|home|tmp)/\S+')


def strip_paths(text: str) -> str:
    """Replace absolute paths with basenames."""
    def _repl(m):
        return os.path.basename(m.group(0))
    return _PATH_RE.sub(_repl, text)


# Unicode replacements for LaTeX text contexts
_UNICODE_TEXT_MAP = {
    '\u0304': '',           # combining macron (handled with preceding char below)
    '\u2192': '$\\to$',     # →
    '\u2190': '$\\leftarrow$',  # ←
    '\u21d2': '$\\Rightarrow$', # ⇒
    '\u2264': '$\\leq$',    # ≤
    '\u2265': '$\\geq$',    # ≥
    '\u2260': '$\\neq$',    # ≠
    '\u00d7': '$\\times$',  # ×
    '\u2248': '$\\approx$', # ≈
    '\u223c': '$\\sim$',    # ∼
    '\u221d': '$\\propto$', # ∝
    '\u221e': '$\\infty$',  # ∞
    '\u00b1': '$\\pm$',     # ±
    '\u2213': '$\\mp$',     # ∓
    '\u00b7': '$\\cdot$',   # ·
    '\u2014': '---',        # em dash
    '\u2013': '--',         # en dash
    '\u2018': '`',          # left single quote
    '\u2019': "'",          # right single quote
    '\u201c': '``',         # left double quote
    '\u201d': "''",         # right double quote
    '\u2026': '\\ldots{}',  # …
    # Greek letters
    '\u0393': '$\\Gamma$',  # Γ
    '\u0394': '$\\Delta$',  # Δ
    '\u039b': '$\\Lambda$', # Λ
    '\u03a3': '$\\Sigma$',  # Σ
    '\u03a6': '$\\Phi$',    # Φ
    '\u03a9': '$\\Omega$',  # Ω
    '\u03b1': '$\\alpha$',  # α
    '\u03b2': '$\\beta$',   # β
    '\u03b3': '$\\gamma$',  # γ
    '\u03b4': '$\\delta$',  # δ
    '\u03b5': '$\\epsilon$',# ε
    '\u03b7': '$\\eta$',    # η
    '\u03b8': '$\\theta$',  # θ
    '\u03ba': '$\\kappa$',  # κ
    '\u03bb': '$\\lambda$', # λ
    '\u03bc': '$\\mu$',     # μ
    '\u03bd': '$\\nu$',     # ν
    '\u03c0': '$\\pi$',     # π
    '\u03c1': '$\\rho$',    # ρ
    '\u03c3': '$\\sigma$',  # σ
    '\u03c4': '$\\tau$',    # τ
    '\u03c6': '$\\phi$',    # φ
    '\u03c8': '$\\psi$',    # ψ
    '\u03c9': '$\\omega$',  # ω
    # Superscripts / subscripts
    '\u207b': '$^{-}$',     # ⁻
    '\u207a': '$^{+}$',     # ⁺
    '\u2070': '$^{0}$',     # ⁰
    '\u00b9': '$^{1}$',     # ¹
    '\u00b2': '$^{2}$',     # ²
    '\u00b3': '$^{3}$',     # ³
    '\u2074': '$^{4}$',     # ⁴
    '\u2075': '$^{5}$',     # ⁵
    '\u2076': '$^{6}$',     # ⁶
    '\u2077': '$^{7}$',     # ⁷
    '\u2078': '$^{8}$',     # ⁸
    '\u2079': '$^{9}$',     # ⁹
    '\u2080': '$_{0}$',     # ₀
    '\u2081': '$_{1}$',     # ₁
    '\u2082': '$_{2}$',     # ₂
    '\u2083': '$_{3}$',     # ₃
    '\u2084': '$_{4}$',     # ₄
    '\u2085': '$_{5}$',     # ₅
    # Miscellaneous
    '\u2113': '$\\ell$',    # ℓ
    '\u210f': '$\\hbar$',   # ℏ
    '\u2202': '$\\partial$',# ∂
    '\u2211': '$\\sum$',    # ∑
    '\u220f': '$\\prod$',   # ∏
    '\u221a': '$\\sqrt{}$', # √
    '\u222b': '$\\int$',    # ∫
    '\u2229': '$\\cap$',    # ∩
    '\u222a': '$\\cup$',    # ∪
    '\u2208': '$\\in$',     # ∈
    '\u2282': '$\\subset$', # ⊂
    '\u2205': '$\\emptyset$', # ∅
}

# Combined character sequences → LaTeX
_COMBINED_CHAR_TEXT = {
    'f\u0304': '$\\bar{f}$',
    'b\u0304': '$\\bar{b}$',
    'f̄': '$\\bar{f}$',
    'b̄': '$\\bar{b}$',
}

# For lstlisting/verbatim contexts: replace to ASCII
_UNICODE_VERB_MAP = {
    # Arrows and math operators
    '\u2192': '->',     # →
    '\u2190': '<-',     # ←
    '\u21d2': '=>',     # ⇒
    '\u2264': '<=',     # ≤
    '\u2265': '>=',     # ≥
    '\u2260': '!=',     # ≠
    '\u00d7': 'x',      # ×
    '\u2248': '~=',     # ≈
    '\u223c': '~',      # ∼
    '\u221d': '~',      # ∝
    '\u221e': 'inf',    # ∞
    '\u00b1': '+-',     # ±
    '\u2213': '-+',     # ∓
    '\u00b7': '*',      # ·
    # Punctuation
    '\u2014': '--',     # em dash
    '\u2013': '-',      # en dash
    '\u2018': "'",      # left single quote
    '\u2019': "'",      # right single quote
    '\u201c': '"',      # left double quote
    '\u201d': '"',      # right double quote
    '\u2026': '...',    # …
    # Greek letters
    '\u0393': 'Gamma',  '\u0394': 'Delta',  '\u039b': 'Lambda',
    '\u03a3': 'Sigma',  '\u03a6': 'Phi',    '\u03a9': 'Omega',
    '\u03b1': 'alpha',  '\u03b2': 'beta',   '\u03b3': 'gamma',
    '\u03b4': 'delta',  '\u03b5': 'epsilon', '\u03b7': 'eta',
    '\u03b8': 'theta',  '\u03ba': 'kappa',  '\u03bb': 'lambda',
    '\u03bc': 'mu',     '\u03bd': 'nu',     '\u03c0': 'pi',
    '\u03c1': 'rho',    '\u03c3': 'sigma',  '\u03c4': 'tau',
    '\u03c6': 'phi',    '\u03c8': 'psi',    '\u03c9': 'omega',
    # Superscripts / subscripts
    '\u207b': '-',      '\u207a': '+',      '\u2070': '0',
    '\u00b9': '1',      '\u00b2': '2',      '\u00b3': '3',
    '\u2074': '4',      '\u2075': '5',      '\u2076': '6',
    '\u2077': '7',      '\u2078': '8',      '\u2079': '9',
    '\u2080': '0',      '\u2081': '1',      '\u2082': '2',
    '\u2083': '3',      '\u2084': '4',      '\u2085': '5',
    # Miscellaneous
    '\u2113': 'l',      '\u210f': 'hbar',   '\u2202': 'd',
}

_COMBINED_CHAR_VERB = {
    'f\u0304': 'fbar',
    'b\u0304': 'bbar',
    'f̄': 'fbar',
    'b̄': 'bbar',
}


# Superscript / subscript Unicode → digit mappings for grouping
_SUPERSCRIPT_CHARS = {
    '\u2070': '0', '\u00b9': '1', '\u00b2': '2', '\u00b3': '3',
    '\u2074': '4', '\u2075': '5', '\u2076': '6', '\u2077': '7',
    '\u2078': '8', '\u2079': '9', '\u207b': '-', '\u207a': '+',
}
_SUBSCRIPT_CHARS = {
    '\u2080': '0', '\u2081': '1', '\u2082': '2', '\u2083': '3',
    '\u2084': '4', '\u2085': '5',
}

# Regex patterns for runs of consecutive superscript/subscript chars
_SUPERSCRIPT_RE = re.compile(
    '[' + re.escape(''.join(_SUPERSCRIPT_CHARS.keys())) + ']{2,}')
_SUBSCRIPT_RE = re.compile(
    '[' + re.escape(''.join(_SUBSCRIPT_CHARS.keys())) + ']{2,}')


def _group_unicode_scripts(text: str) -> str:
    """Group consecutive unicode super/subscript chars into single $^{...}$/$_{...}$.

    E.g. ⁻¹³ → $^{-13}$ instead of $^{-}$$^{1}$$^{3}$.
    """
    def _sup_repl(m):
        digits = ''.join(_SUPERSCRIPT_CHARS[c] for c in m.group(0))
        return f'$^{{{digits}}}$'

    def _sub_repl(m):
        digits = ''.join(_SUBSCRIPT_CHARS[c] for c in m.group(0))
        return f'$_{{{digits}}}$'

    text = _SUPERSCRIPT_RE.sub(_sup_repl, text)
    text = _SUBSCRIPT_RE.sub(_sub_repl, text)
    return text


def sanitize_for_text(text: str) -> str:
    """Replace Unicode characters with LaTeX equivalents for text contexts."""
    for seq, repl in _COMBINED_CHAR_TEXT.items():
        text = text.replace(seq, repl)
    # Group consecutive super/subscript chars before individual replacement
    text = _group_unicode_scripts(text)
    for ch, repl in _UNICODE_TEXT_MAP.items():
        text = text.replace(ch, repl)
    return text


def sanitize_for_verbatim(text: str) -> str:
    """Replace Unicode characters with ASCII for lstlisting contexts."""
    # Combined sequences first (multi-char before single-char)
    for seq, repl in _COMBINED_CHAR_VERB.items():
        text = text.replace(seq, repl)
    # Known single-char replacements
    for ch, repl in _UNICODE_VERB_MAP.items():
        text = text.replace(ch, repl)
    # Strip any remaining combining characters
    text = re.sub(r'[\u0300-\u036f]', '', text)
    # Catch-all: replace any remaining non-ASCII with '?'
    text = text.encode('ascii', errors='replace').decode('ascii')
    return text


# ---------------------------------------------------------------------------
# Brief mode: tool-specific shorthand
# ---------------------------------------------------------------------------

# For each tool, define which input keys to show and how to summarize results.
# Keys listed first are shown first; all values are truncated to fit one line.
BRIEF_INPUT_KEYS = {
    "ComputeSymbolicAmplitude": ["script_name"],
    "RunWolframScript":         ["script_path"],
    "SimplifyResult":           ["script_path", "result_name"],
    "ConvertToPython":          ["script_path", "result_name", "function_name"],
    "EstimateDecayWidthNDA":    ["process_label"],
    "EstimatePhaseSpace":       ["process_label"],
    "EnumerateDiagrams":        ["initial_state", "final_state"],
    "VisualizeDiagrams":        ["diagrams"],
}


def _brief_input_summary(tool_name: str, tool_input: dict,
                         do_strip_paths: bool) -> str:
    """One-line summary of tool input for brief mode."""
    keys = BRIEF_INPUT_KEYS.get(tool_name)
    if not keys:
        # Fallback: show first 2 string-valued keys
        keys = [k for k, v in tool_input.items()
                if isinstance(v, (str, int, float, bool))][:2]
    parts = []
    for k in keys:
        v = tool_input.get(k)
        if v is None:
            continue
        if isinstance(v, str):
            if do_strip_paths:
                v = strip_paths(v)
            # Truncate long values
            if len(v) > 60:
                v = v[:57] + "..."
        else:
            v = json.dumps(v, ensure_ascii=False)
            if len(v) > 60:
                v = v[:57] + "..."
        parts.append(f"{k}={v}")
    return ", ".join(parts) if parts else json.dumps(tool_input, ensure_ascii=False)[:80]


def _brief_result_summary(tool_name: str, result_text: str,
                          do_strip_paths: bool) -> str:
    """One-line summary of tool result for brief mode."""
    if not result_text:
        return "(no output)"
    if do_strip_paths:
        result_text = strip_paths(result_text)

    # Try to parse as JSON and extract status/key fields
    try:
        obj = json.loads(result_text)
        if isinstance(obj, dict):
            status = obj.get("status", obj.get("success", ""))
            if status:
                return str(status)
    except (json.JSONDecodeError, TypeError):
        pass

    # Plain text: first line, truncated
    first_line = result_text.split('\n')[0]
    if len(first_line) > 60:
        first_line = first_line[:57] + "..."
    return first_line


def escape_latex_literal(text: str) -> str:
    """Escape ALL special chars for use inside \\texttt{}, treating everything as literal.

    Unlike escape_latex(), this does NOT preserve LaTeX commands — every
    backslash becomes \\textbackslash{}.  Use this for tool I/O content
    that may contain literal \\documentclass, \\usepackage, \\begin, etc.
    """
    result = []
    for ch in text:
        if ch == '\\':
            result.append(r'\textbackslash{}')
        elif ch == '&':
            result.append(r'\&')
        elif ch == '%':
            result.append(r'\%')
        elif ch == '$':
            result.append(r'\$')
        elif ch == '#':
            result.append(r'\#')
        elif ch == '_':
            result.append(r'\_')
        elif ch == '{':
            result.append(r'\{')
        elif ch == '}':
            result.append(r'\}')
        elif ch == '~':
            result.append(r'\textasciitilde{}')
        elif ch == '^':
            result.append(r'\textasciicircum{}')
        else:
            result.append(ch)
    return ''.join(result)


def _brief_one_liner(block: ConversationBlock, do_strip_paths: bool) -> str:
    """Return a single-line summary string for one brief tool call."""
    name = clean_tool_name(block.tool_name or "unknown")
    inp = _brief_input_summary(name, block.tool_input or {}, do_strip_paths)
    res = _brief_result_summary(name, block.tool_result or "", do_strip_paths)
    inp = sanitize_for_verbatim(inp)
    res = sanitize_for_verbatim(res)
    inp_escaped = escape_latex_literal(inp)
    # Omit arrow and result for generic success statuses
    _GENERIC_SUCCESS = {"", "(no output)", "ok", "true", "True", "success"}
    if res in _GENERIC_SUCCESS:
        return f"\\texttt{{{inp_escaped}}}"
    # Highlight errors in red
    res_escaped = escape_latex_literal(res)
    if 'error' in res.lower() or 'failed' in res.lower():
        return f"\\texttt{{{inp_escaped}}} $\\to$ \\textcolor{{red}}{{\\texttt{{{res_escaped}}}}}"
    return f"\\texttt{{{inp_escaped}}} $\\to$ \\texttt{{{res_escaped}}}"


def _render_parallel_brief(blocks: list[ConversationBlock],
                           do_strip_paths: bool) -> str:
    """Render a mixed parallel dispatch as a single compact box.

    Groups by tool name and produces a header like:
      EstimateBranchingRatioNDA (×3) | EnumerateDiagrams | Write (×2)
    with one-liner summaries for each call.
    """
    # Count by tool name, preserving first-seen order
    tool_counts: dict[str, int] = {}
    tool_order: list[str] = []
    for blk in blocks:
        name = clean_tool_name(blk.tool_name or "")
        if name not in tool_counts:
            tool_order.append(name)
            tool_counts[name] = 0
        tool_counts[name] += 1

    # Build header
    header_parts = []
    for name in tool_order:
        count = tool_counts[name]
        if count > 1:
            header_parts.append(f"{escape_latex(name)} $(\\times {count})$")
        else:
            header_parts.append(escape_latex(name))
    header = " | ".join(header_parts)

    parts = []
    if len(blocks) <= 2:
        # 1-2 calls: individual one-liner boxes (no grouping overhead)
        for blk in blocks:
            name = clean_tool_name(blk.tool_name or "unknown")
            parts.append(f"\\begin{{agenttool}}{{{escape_latex(name)}}}")
            parts.append(f"\\small {_brief_one_liner(blk, do_strip_paths)}")
            parts.append("\\end{agenttool}")
            parts.append("")
    else:
        # 3+ calls: single grouped box
        parts.append(f"\\begin{{agenttool}}{{{header}}}")
        parts.append("\\begin{enumerate}[leftmargin=1.5em, itemsep=1pt, parsep=0pt]")
        for blk in blocks:
            parts.append(f"  \\item \\small {_brief_one_liner(blk, do_strip_paths)}")
        parts.append("\\end{enumerate}")
        parts.append("\\end{agenttool}")

    return '\n'.join(parts)


def render_tool_brief_group(tool_blocks: list[ConversationBlock],
                            do_strip_paths: bool) -> str:
    """Render a group of repeated brief tool calls.

    If 1-2 calls: individual one-liner boxes.
    If 3+: single box with ×N header and enumerated list.
    """
    name = clean_tool_name(tool_blocks[0].tool_name or "unknown")
    n = len(tool_blocks)

    if n <= 2:
        # Individual boxes
        parts = []
        for blk in tool_blocks:
            parts.append(f"\\begin{{agenttool}}{{{escape_latex(name)}}}")
            parts.append(f"\\small {_brief_one_liner(blk, do_strip_paths)}")
            parts.append("\\end{agenttool}")
            parts.append("")
        return '\n'.join(parts)

    # Grouped box with ×N
    parts = []
    parts.append(f"\\begin{{agenttool}}{{{escape_latex(name)} $(\\times {n})$}}")
    parts.append("\\begin{enumerate}[leftmargin=1.5em, itemsep=1pt, parsep=0pt]")
    for blk in tool_blocks:
        parts.append(f"  \\item \\small {_brief_one_liner(blk, do_strip_paths)}")
    parts.append("\\end{enumerate}")
    parts.append("\\end{agenttool}")
    return '\n'.join(parts)


# ---------------------------------------------------------------------------
# JSON result pruning
# ---------------------------------------------------------------------------

# Keys to remove from tool result JSON (verbose/infrastructure fields)
_PRUNE_KEYS = {
    # Inline markdown summaries (also saved to files)
    "diagram_summary_markdown", "summary_markdown", "summary_table",
    # File paths and infrastructure
    "results_path", "script_path", "summary_file", "log_file", "lhe_file",
    "output_directory", "data_dir",
    # Verbose metadata
    "saved_files", "formula_note", "formula_type",
    "scan_detected", "note",
    # Query echoes
    "query_info", "schema",
}


def _prune_verbose_keys(obj: dict) -> dict:
    """Remove known verbose keys from tool result dicts (recursive)."""
    pruned = {}
    for k, v in obj.items():
        if k in _PRUNE_KEYS:
            continue
        if isinstance(v, dict):
            v = _prune_verbose_keys(v)
        pruned[k] = v
    return pruned


# ---------------------------------------------------------------------------
# LaTeX rendering
# ---------------------------------------------------------------------------

def _strip_outer_braces(text: str) -> str:
    """Strip the outermost { } from a JSON string and dedent by 2 spaces.

    Turns:
        {
          "key": "value",
          "key2": 42
        }
    into:
        "key": "value",
        "key2": 42
    """
    lines = text.split('\n')
    # Check if first and last non-empty lines are just { and }
    if (len(lines) >= 2
            and lines[0].strip() == '{'
            and lines[-1].strip() == '}'):
        inner = lines[1:-1]
        # Dedent by 2 spaces
        dedented = []
        for line in inner:
            if line.startswith('  '):
                dedented.append(line[2:])
            else:
                dedented.append(line)
        return '\n'.join(dedented)
    return text


def render_tool_block(block: ConversationBlock, max_tool_output: int,
                      do_strip_paths: bool,
                      compact_json: bool = False) -> str:
    """Render a tool_call block as an agenttool environment."""
    name = clean_tool_name(block.tool_name or "unknown")

    parts = []
    parts.append(f"\\begin{{agenttool}}{{{escape_latex(name)}}}")

    # Input
    if block.tool_input:
        # Truncate very long string values (e.g. Write "content" field)
        truncated_input = {}
        for k, v in block.tool_input.items():
            if isinstance(v, str) and len(v) > 200:
                truncated_input[k] = v[:200] + f"... ({len(v)} chars)"
            else:
                truncated_input[k] = v
        input_json = json.dumps(truncated_input, indent=2, ensure_ascii=False)
        if compact_json:
            input_json = _strip_outer_braces(input_json)
        if do_strip_paths:
            input_json = strip_paths(input_json)
        input_json = sanitize_for_verbatim(input_json)
        parts.append("\\small\\textbf{Input:}")
        parts.append(f"\\begin{{lstlisting}}[style=jsonstyle]\n{input_json}\n\\end{{lstlisting}}")

    # Result
    if block.tool_result:
        result_text = block.tool_result

        # Try to parse JSON, prune verbose keys, then pretty-print.
        # Path stripping happens AFTER pretty-print to avoid breaking JSON.
        try:
            result_obj = json.loads(result_text)
            if isinstance(result_obj, dict):
                result_obj = _prune_verbose_keys(result_obj)
            result_text = json.dumps(result_obj, indent=2, ensure_ascii=False)
        except (json.JSONDecodeError, TypeError):
            pass

        if compact_json:
            result_text = _strip_outer_braces(result_text)

        if do_strip_paths:
            result_text = strip_paths(result_text)

        # Truncate
        result_lines = result_text.split('\n')
        if len(result_lines) > max_tool_output:
            result_lines = result_lines[:max_tool_output]
            result_lines.append(f"  ... ({len(result_text.split(chr(10))) - max_tool_output} more lines)")

        result_text = '\n'.join(result_lines)
        result_text = sanitize_for_verbatim(result_text)
        parts.append("\\small\\textbf{Result:}")
        parts.append(f"\\begin{{lstlisting}}[style=jsonstyle]\n{result_text}\n\\end{{lstlisting}}")

    parts.append("\\end{agenttool}")
    return '\n'.join(parts)


def render_latex(blocks: list[ConversationBlock],
                 max_tool_output: int = 30,
                 do_strip_paths: bool = False,
                 brief: bool = False,
                 raw_user: bool = False,
                 compact_json: bool = False,
                 brief_context: set[str] | None = None) -> str:
    """Render conversation blocks as LaTeX."""
    parts = []
    parts.append("% Auto-generated by scripts/jsonl_to_latex.py")
    parts.append("% Do not edit manually.\n")

    # Track which tools have been shown in full (for brief mode)
    seen_tools: set[str] = set(brief_context or [])

    i = 0
    while i < len(blocks):
        b = blocks[i]

        if b.kind == "user":
            parts.append("\\begin{agentuser}")
            if raw_user:
                # User prompt is already LaTeX — pass through with unicode sanitization only
                parts.append(sanitize_for_text(b.content))
            else:
                parts.append(markdown_to_latex(b.content))
            parts.append("\\end{agentuser}\n")

        elif b.kind == "assistant_text":
            parts.append("\\begin{agentresponse}")
            parts.append(markdown_to_latex(b.content))
            parts.append("\\end{agentresponse}\n")

        elif b.kind == "thinking":
            parts.append("\\begin{agentsystem}")
            parts.append("\\small\\textit{(Extended thinking)}\n")
            parts.append(markdown_to_latex(b.content))
            parts.append("\\end{agentsystem}\n")

        elif b.kind == "tool_call":
            # Collect consecutive tool_call blocks
            j = i + 1
            while j < len(blocks) and blocks[j].kind == "tool_call":
                j += 1
            run = blocks[i:j]  # all consecutive tool calls
            n_parallel = len(run)
            if n_parallel > 1:
                parts.append(f"% --- {n_parallel} parallel tool calls ---")

            if not brief:
                for blk in run:
                    parts.append(render_tool_block(blk, max_tool_output, do_strip_paths, compact_json))
                    parts.append("")
            else:
                # In brief mode: render first-seen tools fully, then group
                # all remaining brief calls into a single compact box.
                full_blocks = []
                brief_blocks = []
                for blk in run:
                    name = clean_tool_name(blk.tool_name or "")
                    if name not in seen_tools:
                        full_blocks.append(blk)
                        seen_tools.add(name)
                    else:
                        brief_blocks.append(blk)

                # Render full blocks first
                for blk in full_blocks:
                    parts.append(render_tool_block(blk, max_tool_output, do_strip_paths, compact_json))
                    parts.append("")

                # Group ALL brief blocks into a unified parallel dispatch box
                if brief_blocks:
                    parts.append(_render_parallel_brief(brief_blocks, do_strip_paths))
                    parts.append("")

            i = j
            continue

        i += 1

    return '\n'.join(parts)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Convert Claude Code JSONL conversation logs to LaTeX transcripts.")
    parser.add_argument("input", help="Path to the JSONL file")
    parser.add_argument("--output", "-o", help="Output .tex file (default: stdout)")
    parser.add_argument("--max-tool-output", type=int, default=30,
                        help="Truncate tool output to N lines (default: 30)")
    parser.add_argument("--skip-tools", default="",
                        help="Comma-separated list of tool names to skip")
    parser.add_argument("--keep-tools", default="",
                        help="Comma-separated list of tool names to keep (inverse of --skip-tools)")
    parser.add_argument("--include-thinking", action="store_true",
                        help="Include extended thinking blocks")
    parser.add_argument("--excerpt", default=None,
                        help="Block index range START:END (0-based, after filtering/merging)")
    parser.add_argument("--strip-paths", action="store_true",
                        help="Replace absolute paths with basenames")
    parser.add_argument("--brief", action="store_true",
                        help="Show full detail only for first call of each tool")
    parser.add_argument("--brief-context", default="",
                        help="Comma-separated tool names to pre-populate as 'already seen' in brief mode")
    parser.add_argument("--raw-user", action="store_true",
                        help="Pass user messages through as raw LaTeX (no markdown conversion)")
    parser.add_argument("--compact-json", action="store_true",
                        help="Strip outer { } braces from JSON in tool I/O blocks")
    parser.add_argument("--list-blocks", action="store_true",
                        help="Print block index map to stderr and exit (no LaTeX output)")
    parser.add_argument("--flowchart", action="store_true",
                        help="Print compact tool-call sequence for flowchart scaffolding and exit")
    parser.add_argument("--stats", nargs="?", const="", default=None,
                        metavar="PREFIX",
                        help="Print session statistics and exit. Optionally save to PREFIX_stats.json and PREFIX_stats.txt")

    args = parser.parse_args()

    # Parse skip-tools / keep-tools (mutually exclusive)
    skip_tools = set()
    if args.skip_tools:
        skip_tools = {t.strip() for t in args.skip_tools.split(",")}
    keep_tools = set()
    if args.keep_tools:
        keep_tools = {t.strip() for t in args.keep_tools.split(",")}
    if skip_tools and keep_tools:
        parser.error("--skip-tools and --keep-tools are mutually exclusive")

    # Parse brief-context
    brief_context = set()
    if args.brief_context:
        brief_context = {t.strip() for t in args.brief_context.split(",")}

    # Parse excerpt
    excerpt = None
    if args.excerpt:
        parts = args.excerpt.split(":")
        start = int(parts[0]) if parts[0] else 0
        end = int(parts[1]) if len(parts) > 1 and parts[1] else None
        excerpt = (start, end)

    # Pipeline
    entries = parse_jsonl(args.input)
    tool_results = build_tool_results_index(entries)
    blocks = build_conversation(entries, tool_results,
                                include_thinking=args.include_thinking)
    blocks = merge_consecutive_text(blocks)

    # --stats: print session statistics and exit
    if args.stats is not None:
        prefix = args.stats if args.stats else None
        print_session_stats(entries, output_prefix=prefix, jsonl_path=args.input)
        return

    # --list-blocks: show block map before excerpt but after tool filtering
    if args.list_blocks:
        filtered = apply_filters(blocks, skip_tools, keep_tools, excerpt=None)
        print_block_list(filtered)
        return

    # --flowchart: compact tool-call sequence
    if args.flowchart:
        filtered = apply_filters(blocks, skip_tools, keep_tools, excerpt=None)
        print_flowchart(filtered, jsonl_path=args.input)
        return

    blocks = apply_filters(blocks, skip_tools, keep_tools, excerpt)

    latex = render_latex(blocks,
                         max_tool_output=args.max_tool_output,
                         do_strip_paths=args.strip_paths,
                         brief=args.brief,
                         raw_user=args.raw_user,
                         compact_json=args.compact_json,
                         brief_context=brief_context)

    if args.output:
        with open(args.output, 'w') as f:
            f.write(latex)
        print(f"Wrote {len(blocks)} blocks to {args.output}", file=sys.stderr)
    else:
        print(latex)


if __name__ == "__main__":
    main()
