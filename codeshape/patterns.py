"""Ignore pattern definitions and path matching logic."""

from fnmatch import fnmatch
import os

DEFAULT_IGNORE_PATTERNS: list[str] = [
    # Package managers & virtualenvs
    "node_modules/", "venv/", ".venv/", "env/", ".env",
    "__pycache__/", ".pytest_cache/", "*.egg-info/",
    "dist/", "build/", ".next/", "out/", "coverage/", ".nyc_output/",
    # Lock & package metadata files
    "package.json", "package-lock.json", "yarn.lock", "pnpm-lock.yaml",
    "Cargo.lock", "Gemfile.lock", "poetry.lock", "composer.lock",
    # IDE and system
    ".git/", ".vscode/", ".idea/", ".DS_Store", "Thumbs.db",
    "*.pyc", "*.pyo", "*.pyd", ".Python", "*.so", "*.dylib", "*.dll",
    # Build artifacts
    "*.min.js", "*.min.css", "*.map", "*.d.ts",
    # Documentation
    "LICENSE", "README.md", "CHANGELOG.md", "*.md",
    # Media & archives
    "*.jpg", "*.jpeg", "*.png", "*.gif", "*.svg", "*.ico",
    "*.mp4", "*.mp3", "*.wav", "*.pdf", "*.zip", "*.tar", "*.gz",
    # Databases & logs
    "*.log", "*.sql", "*.sqlite", "*.db",
]


def _has_glob(pattern: str) -> bool:
    return any(ch in pattern for ch in ("*", "?", "["))


def is_ignored_dir(dir_name: str, rel_posix: str, patterns: list[str]) -> bool:
    """Return True if a directory should be skipped during traversal."""
    for raw in patterns:
        pattern = raw.strip()
        if not pattern:
            continue
        clean = pattern.rstrip("/")
        if _has_glob(clean):
            if fnmatch(dir_name, clean) or fnmatch(rel_posix, clean):
                return True
        elif dir_name == clean or rel_posix == clean:
            return True
    return False


def should_ignore(rel_path: str, patterns: list[str]) -> bool:
    """Return True if a relative file path matches any ignore pattern."""
    rel_posix = rel_path.replace(os.sep, "/")
    parts = rel_posix.split("/")
    basename = parts[-1]

    for raw in patterns:
        pattern = raw.strip()
        if not pattern:
            continue
        if pattern.endswith("/"):
            target = pattern[:-1]
            if target in parts[:-1] or rel_posix.startswith(pattern):
                return True
        elif pattern == ".env":
            if basename == ".env" or basename.startswith(".env."):
                return True
        elif _has_glob(pattern):
            if fnmatch(basename, pattern) or fnmatch(rel_posix, pattern):
                return True
        elif basename == pattern or rel_posix == pattern or pattern in parts[:-1]:
            return True
    return False
