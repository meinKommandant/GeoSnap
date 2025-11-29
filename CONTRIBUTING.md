# Contributing to GeoSnap

Thank you for your interest in contributing to GeoSnap! We welcome contributions from everyone.

## Getting Started

1.  **Fork the repository** on GitHub.
2.  **Clone your fork** locally:
    ```bash
    git clone https://github.com/yourusername/geosnap.git
    cd geosnap
    ```
3.  **Create a virtual environment** and install dependencies:
    ```bash
    python -m venv venv
    # Activate venv (Windows: .\venv\Scripts\activate, Unix: source venv/bin/activate)
    pip install -r requirements.txt
    ```

## Development Workflow

1.  Create a new branch for your feature or fix:
    ```bash
    git checkout -b feature/amazing-feature
    ```
2.  Make your changes.
3.  Run tests to ensure nothing is broken (if applicable):
    ```bash
    pytest
    ```
4.  Commit your changes following conventional commit messages.
5.  Push to your fork and submit a Pull Request.

## Coding Style

*   We use `flake8` for linting.
*   Please follow PEP 8 guidelines.
*   Use the provided `.editorconfig` to maintain consistent indentation.

## Reporting Issues

If you find a bug or have a feature request, please open an issue on GitHub describing the problem or idea in detail.
