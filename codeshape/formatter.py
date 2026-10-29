"""Human-readable terminal and JSON output formatters."""

import json

from codeshape.analyzer import AnalysisResult
from codeshape.chart import render_shape_chart

_BOLD = "\033[1m"
_DIM = "\033[2m"
_RED = "\033[31m"
_GREEN = "\033[32m"
_YELLOW = "\033[33m"
_RESET = "\033[0m"


def _paint(text: str, code: str, enabled: bool) -> str:
    return f"{code}{text}{_RESET}" if enabled else text


def _score_color(score: float) -> str:
    if score < 500:
        return _GREEN
    if score < 1500:
        return _YELLOW
    return _RED


def format_json(result: AnalysisResult, top: int | None = None) -> str:
    """Serialize analysis result as formatted JSON."""
    shown = result.files if top in (None, 0) else result.files[:top]
    payload = {
        "name": result.name,
        "path": result.path,
        "threshold": result.threshold,
        "code_shape_score": result.code_shape_score,
        "total_files": result.total_files,
        "total_lines": result.total_lines,
        "average_lines": result.average_lines,
        "over_threshold_count": result.over_threshold_count,
        "files": [
            {"path": f.path, "name": f.name, "lines": f.lines} for f in shown
        ],
    }
    return json.dumps(payload, indent=2)


def format_report(
    result: AnalysisResult,
    top: int = 20,
    use_color: bool = True,
) -> str:
    """Format analysis summary, shape chart, and file table for terminal output."""
    lines: list[str] = []
    title = _paint(result.name, _BOLD, use_color)
    loc = _paint(result.path, _DIM, use_color)
    lines.append(f"{title}  {loc}")

    score_txt = _paint(
        f"{result.code_shape_score:,.2f}",
        _BOLD + _score_color(result.code_shape_score),
        use_color,
    )
    hint = _paint("(lower is better)", _DIM, use_color)
    lines.append(f"Score: {score_txt} {hint}")
    lines.append(
        f"Files: {result.total_files:,}  |  Lines: {result.total_lines:,}  |  "
        f"Avg: {result.average_lines}  |  Over {result.threshold}: {result.over_threshold_count}"
    )

    if not result.files:
        lines.append("\nNo matching source files found.")
        return "\n".join(lines)

    chart_count = min(len(result.files), 50)
    lines.append(f"\nShape (top {chart_count} files)")
    lines.extend(render_shape_chart(result.files, result.threshold, use_color))

    shown = result.files if top == 0 else result.files[:top]
    lines.append(f"\nFiles ({len(shown)} of {result.total_files})")
    lines.append(_paint("    LINES    OVER  FILE", _DIM, use_color))
    for item in shown:
        excess = item.lines - result.threshold
        if excess > 0:
            over_color = _RED if item.lines > result.threshold * 2 else _YELLOW
            over_col = _paint(f"{f'+{excess}':>7}", over_color, use_color)
        else:
            over_col = _paint(f"{'-':>7}", _DIM, use_color)
        lines.append(f"  {item.lines:>7} {over_col}  {item.path}")

    remaining = result.total_files - len(shown)
    if remaining > 0:
        lines.append(
            _paint(f"  ... and {remaining} more (use --top 0 to show all)", _DIM, use_color)
        )
    return "\n".join(lines)
