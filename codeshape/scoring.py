"""Code Shape Score calculation."""

from collections.abc import Iterable


def calculate_code_shape_score(
    line_counts: Iterable[int],
    total_files: int,
    total_lines: int,
    threshold: int = 100,
) -> float:
    """Calculate Code Shape Score (lower is better).

    Formula matches code-shape-analyser:
    - 10 points per file
    - 0.1 points per line of code
    - (excess ** 2) * 0.01 quadratic penalty for each file exceeding threshold
    """
    file_penalty = total_files * 10
    line_penalty = total_lines * 0.1
    large_file_penalty = sum(
        ((lines - threshold) ** 2) * 0.01
        for lines in line_counts
        if lines > threshold
    )
    return round(file_penalty + line_penalty + large_file_penalty, 2)
