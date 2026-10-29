"""Codebase directory scanner and analysis model."""

from dataclasses import dataclass
import os
from pathlib import Path

from codeshape.patterns import DEFAULT_IGNORE_PATTERNS, is_ignored_dir, should_ignore
from codeshape.scoring import calculate_code_shape_score


@dataclass(frozen=True)
class FileStat:
    path: str
    name: str
    lines: int


@dataclass(frozen=True)
class AnalysisResult:
    name: str
    path: str
    threshold: int
    total_files: int
    total_lines: int
    average_lines: float
    over_threshold_count: int
    code_shape_score: float
    files: list[FileStat]


def _count_lines(file_path: Path) -> int:
    """Count lines in a text file; return 0 for unreadable or binary files."""
    try:
        with open(file_path, "rb") as raw:
            sample = raw.read(4096)
            if not sample or b"\x00" in sample:
                return 0
        with open(file_path, "r", encoding="utf-8", errors="ignore") as text:
            return sum(1 for _ in text)
    except OSError:
        return 0


def analyze_codebase(
    target: Path,
    threshold: int = 100,
    extra_ignores: list[str] | None = None,
) -> AnalysisResult:
    """Scan target directory and compute Code Shape metrics."""
    root = target.resolve()
    patterns = DEFAULT_IGNORE_PATTERNS + (extra_ignores or [])
    files: list[FileStat] = []

    for current_root, dirs, filenames in os.walk(root, followlinks=False):
        current_path = Path(current_root)
        rel_dir = current_path.relative_to(root)
        rel_dir_posix = "" if rel_dir == Path(".") else rel_dir.as_posix()

        dirs[:] = sorted(
            d for d in dirs
            if not is_ignored_dir(
                d, f"{rel_dir_posix}/{d}".lstrip("/"), patterns
            )
        )

        for filename in filenames:
            full_path = current_path / filename
            if full_path.is_symlink():
                continue
            rel_path = full_path.relative_to(root).as_posix()
            if should_ignore(rel_path, patterns):
                continue
            lines = _count_lines(full_path)
            if lines > 0:
                files.append(FileStat(path=rel_path, name=filename, lines=lines))

    files.sort(key=lambda f: (-f.lines, f.path))
    total_files = len(files)
    total_lines = sum(f.lines for f in files)
    avg_lines = round(total_lines / total_files, 1) if total_files else 0.0
    over_count = sum(1 for f in files if f.lines > threshold)
    score = calculate_code_shape_score(
        (f.lines for f in files), total_files, total_lines, threshold
    )

    return AnalysisResult(
        name=root.name or str(root),
        path=str(root),
        threshold=threshold,
        total_files=total_files,
        total_lines=total_lines,
        average_lines=avg_lines,
        over_threshold_count=over_count,
        code_shape_score=score,
        files=files,
    )
