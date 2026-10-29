# codeshape

Minimal CLI version of CodeShape for analyzing codebase file-size distribution and Code Shape Score.

## Install

```bash
uv tool install .
# or
pip install -e .
```

Or run directly without installing:

```bash
python3 -m codeshape
```

## Usage

```bash
# Analyze current directory (default threshold: 100 lines)
codeshape

# Analyze a target directory with a custom threshold
codeshape /path/to/repo -t 150

# Add ignore patterns (repeatable)
codeshape /path/to/repo -i "tests/" -i "*.gen.py"

# Show all files instead of top 20
codeshape -n 0

# Output JSON
codeshape --json
```

## Code Shape Score

Lower is better:
- `10` points per file
- `0.1` points per line of code
- `((lines - threshold) ** 2) * 0.01` for each file above threshold
