# Dev Infrastructure — python-blackjack

## Language & Runtime

- **Python 3.14.5**
- Virtual environment: `venv` (standard library)

---

## Tooling

| Tool | Purpose | Version |
|---|---|---|
| pytest | Test runner | 8.3.5 |
| pytest-cov | Coverage reporting | 6.1.0 |
| Ruff | Linter and formatter | 0.9.10 |
| pre-commit | Pre-commit hooks | 4.2.0 |

---

## Local Setup

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt -r requirements-dev.txt
pre-commit install
```

---

## Common Commands

| Command | What it does |
|---|---|
| `pytest` | Run all tests |
| `pytest --cov=src --cov-fail-under=80` | Run tests with coverage gate |
| `ruff check src/` | Lint |
| `ruff format src/` | Format |
| `pre-commit run --all-files` | Run all pre-commit hooks manually |

---

## CI Pipeline

GitHub Actions runs on every push and every PR to `main`.

Pipeline steps:
1. Checkout code
2. Set up Python 3.14.5
3. Install `requirements.txt` and `requirements-dev.txt`
4. `ruff check src/` — lint
5. `ruff format --check src/` — format check
6. `pytest --cov=src --cov-fail-under=80` — tests + coverage

All steps must pass. A failing CI blocks merge.

---

## VS Code

Recommended extensions: Ruff, Python, Pylance, GitHub Copilot.
Settings are pre-configured in `.vscode/settings.json` — format on save is enabled using Ruff.
