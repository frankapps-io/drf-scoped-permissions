# Contributing to DRF Scoped Permissions

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/frankapps-io/drf-scoped-permissions.git
   cd drf-scoped-permissions
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Run tests**
   ```bash
   pytest
   ```

## Code Style

We use the following tools to maintain code quality:

- **Ruff** for linting and formatting (replaces black, isort, flake8)
- **mypy** for type checking

Run all checks:
```bash
ruff check --fix drf_scoped_permissions tests
ruff format drf_scoped_permissions tests
mypy drf_scoped_permissions
```

Or use the Makefile:
```bash
make format  # Auto-fix and format
make lint    # Check everything
```

## Testing

- Write tests for all new features
- Ensure all tests pass before submitting PR
- Aim for >90% test coverage

```bash
pytest --cov=drf_scoped_permissions --cov-report=html
```

## Pull Request Process

1. **Fork the repository** and create your branch from `main`
2. **Make your changes** with clear, descriptive commits
3. **Add tests** for any new functionality
4. **Update documentation** if needed
5. **Run all checks** (tests, linting, type checking)
6. **Submit a pull request** with a clear description

### Commit Message Guidelines

- Use present tense ("Add feature" not "Added feature")
- Use imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit first line to 72 characters
- Reference issues and PRs where appropriate

Examples:
```
Add scope wildcard support (#123)
Fix permission check for custom actions
Update README with JWT integration example
```

## Reporting Issues

When reporting issues, please include:

- **Environment details** (Python version, Django version, DRF version)
- **Steps to reproduce** the issue
- **Expected behavior** vs actual behavior
- **Error messages** or stack traces if applicable

## Feature Requests

We welcome feature requests! Please:

- **Check existing issues** to avoid duplicates
- **Explain the use case** clearly
- **Describe the proposed solution** if you have one
- **Consider alternatives** you've evaluated

## Code of Conduct

### Our Standards

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on what's best for the community
- Show empathy towards others

### Unacceptable Behavior

- Harassment, discrimination, or derogatory comments
- Trolling, insulting comments, or personal attacks
- Publishing others' private information
- Other conduct inappropriate in a professional setting

## Questions?

Feel free to open an issue with your question or reach out to the maintainers directly.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
