# Contributing to GeoSnap

Thank you for your interest in contributing to GeoSnap! We welcome contributions from everyone.

## Getting Started

1.  **Fork the repository** on GitHub.
2.  **Clone your fork** locally:
    ```bash
    git clone https://github.com/meinKommandant/GeoSnap.git
    cd GeoSnap
    ```
3.  **Create a virtual environment** and install dependencies:
    ```bash
    python -m venv venv
    # Activate venv (Windows: .\venv\Scripts\activate, Unix: source venv/bin/activate)
    pip install -r requirements.txt
    pip install -r requirements-dev.txt
    ```

## Development Workflow

1.  Create a new branch for your feature or fix:
    ```bash
    git checkout -b feature/amazing-feature
    ```
2.  Make your changes.
3.  Run tests to ensure nothing is broken:
    ```bash
    pytest tests/ -v
    ```
4.  Format your code:
    ```bash
    ruff format src/ tests/
    ruff check src/
    ```
5.  Commit your changes following [Conventional Commits](https://www.conventionalcommits.org/).
6.  Push to your fork and submit a Pull Request.

## Coding Style

*   We use **Ruff** for linting and formatting.
*   Please follow PEP 8 guidelines.
*   Use the provided `.editorconfig` to maintain consistent indentation.
*   Run `pre-commit install` to set up git hooks.

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src/geosnap --cov-report=term-missing
```

## Reporting Issues

If you find a bug or have a feature request, please open an issue on GitHub describing the problem or idea in detail.
