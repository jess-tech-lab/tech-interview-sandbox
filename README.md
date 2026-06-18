## Development Setup

Requires Python 3.12+.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install ruff pre-commit mypy

# Install pre-commit hooks (runs automatically on every commit)
pre-commit install
```

Run linting and formatting manually:

```bash
ruff check --fix .
ruff format .
```

Note as this repo is for tech interview, code isn't expected to be perfect. However, if `mypy` check is preferred, run type checking manually (not enforced on commit):

```bash
mypy <file_or_dir>
```
