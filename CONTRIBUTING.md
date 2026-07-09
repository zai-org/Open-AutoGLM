# Contributing to Open-AutoGLM

Thank you for your interest in contributing! Open-AutoGLM is a phone agent automation framework by Zhipu AI that enables LLM-based control of Android, HarmonyOS, and iOS devices.

## Development Setup

```bash
git clone https://github.com/zai-org/Open-AutoGLM.git
cd Open-AutoGLM
pip install -e ".[dev]"
```

### Prerequisites
- Python 3.10+
- ADB (Android), HDC (HarmonyOS), or WebDriverAgent (iOS) depending on your target platform
- An OpenAI-compatible API endpoint (e.g., AutoGLM-Phone-9B model)

## Code Style

We use pre-commit hooks to enforce code quality:

```bash
pip install pre-commit
pre-commit install
```

This runs:
- **ruff** for linting and formatting (PEP 8 compliant)
- **ruff-format** for automatic code formatting
- **typos** for spell checking
- **pymarkdown** for Markdown linting

All code and comments should be in English. Follow PEP 8 naming conventions.

## Running Tests

```bash
pytest
```

Please ensure all tests pass before submitting a PR. If you add new functionality, include tests.

## Pull Request Process

1. Fork the repository and create a feature branch: `git checkout -b feature/my-feature`
2. Make your changes, following the code style guidelines
3. Add tests for any new functionality
4. Ensure all tests pass: `pytest`
5. Update documentation if needed
6. Submit a pull request to the `main` branch

### PR Title Format
Use descriptive titles. Prefix with the area of change:
- `fix:` for bug fixes
- `feat:` for new features
- `docs:` for documentation changes
- `test:` for test additions
- `refactor:` for code refactoring

### PR Description
Please include:
- **What**: What does this PR do?
- **Why**: Why is this change needed?
- **How**: How was it implemented?
- **Testing**: How was it tested?

## Types of Contributions

### Bug Fixes
Check the [Issues](https://github.com/zai-org/Open-AutoGLM/issues) page for reported bugs. Issues tagged with `bug` are confirmed issues.

### New Features
For larger features, please open an issue first to discuss the design with maintainers.

### Documentation
We welcome documentation improvements! This includes:
- Fixing typos or unclear explanations
- Translating documentation (especially Chinese ↔ English)
- Adding usage examples
- Improving code docstrings

### Tests
We especially need tests! See [Issues tagged with testing needs](https://github.com/zai-org/Open-AutoGLM/issues) for areas that need coverage.

## Adding Support for New Apps

To add a new app to the agent's supported list:
1. Add the app configuration in the appropriate platform directory
2. Add the app to the prompts (both English and Chinese)
3. Test with manual verification

## Adding a New Action Type

1. Add the action definition in `phone_agent/actions/handler.py`
2. Update both `phone_agent/config/prompts.py` and `phone_agent/config/prompts_en.py`
3. Add tests for the new action in `tests/`

## Community

- Report bugs via [GitHub Issues](https://github.com/zai-org/Open-AutoGLM/issues)
- For questions, open a Discussion or comment on related Issues

## License

By contributing, you agree that your contributions will be licensed under the Apache 2.0 License.
