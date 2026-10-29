"""Terminal vertical bar chart renderer for file-size distribution."""

from codeshape.analyzer import FileStat

_BLOCKS = " ▁▂▃▄▅▆▇█"
_RED = "\033[31m"
_GREEN = "\033[32m"
_DIM = "\033[2m"
_RESET = "\033[0m"


def _paint(text: str, code: str, enabled: bool) -> str:
    return f"{code}{text}{_RESET}" if enabled else text


def render_shape_chart(
    files: list[FileStat],
    threshold: int,
    use_color: bool = True,
    max_bars: int = 50,
    height: int = 8,
) -> list[str]:
    """Render a sorted vertical file-size silhouette chart."""
    if not files:
        return []

    sample = files[:max_bars]
    top_lines = max(sample[0].lines, 1)
    label_width = max(len(str(top_lines)), len(str(threshold)), 3)

    threshold_row = -1
    if 0 < threshold <= top_lines:
        threshold_row = min(
            height - 1, max(0, int(((threshold - 1) / top_lines) * height))
        )

    rows: list[str] = []
    for row in range(height - 1, -1, -1):
        cells: list[str] = []
        for item in sample:
            fill = (item.lines / top_lines) * height - row
            if fill <= 0:
                cells.append(" ")
            else:
                idx = min(8, max(1, round(fill * 8)))
                color = _RED if item.lines > threshold else _GREEN
                cells.append(_paint(_BLOCKS[idx], color, use_color))

        if row == height - 1:
            axis_label = f"{top_lines:>{label_width}} │ "
        elif row == threshold_row:
            axis_label = f"{threshold:>{label_width}} ┤ "
        elif row == 0:
            axis_label = f"{0:>{label_width}} │ "
        else:
            axis_label = f"{'':>{label_width}} │ "

        suffix = ""
        if row == threshold_row:
            suffix = _paint(f"  <- threshold ({threshold})", _DIM, use_color)

        rows.append(f"  {axis_label}{''.join(cells)}{suffix}")

    rows.append(f"  {'':>{label_width}} └{'─' * (len(sample) + 1)}")
    return rows
