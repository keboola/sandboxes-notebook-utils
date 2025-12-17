# Contributing

## Development Setup

- Python 3.8+
- Install dependencies: `pip install -r requirements.txt`

## Testing & Linting

```bash
# Run all tests
pytest tests/*

# Linting - critical errors (must pass)
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics

# Linting - full check (max-line-length: 120)
flake8 . --count --exit-zero --max-complexity=10 --max-line-length=120 --statistics
```

## Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` new feature
- `fix:` bug fix
- `refactor:` code restructuring
- `docs:` documentation changes
- `test:` test changes
- `chore:` maintenance tasks

## Versioning

[PEP 440](https://peps.python.org/pep-0440/) compliant:

- **Release**: `X.Y.Z` (e.g., `2.2.0`)
- **Development**: `X.Y.Z.devN` (e.g., `2.2.0.dev1`)

The version in `setup.py` must match the git tag.