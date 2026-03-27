# Contributing to SanTOK

Thank you for your interest in contributing to SanTOK! This document provides guidelines and instructions for contributing.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/yourusername/santok-complete.git`
3. Create a branch for your changes: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Test your changes: `pytest tests/`
6. Submit a pull request

## Development Setup

1. Install the package in development mode:
   ```bash
   pip install -e .
   ```

2. Install development dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Code Style

- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Write docstrings for all public functions and classes
- Keep functions focused and single-purpose

## Testing

- Write tests for all new features
- Ensure all existing tests pass: `pytest tests/`
- Aim for good test coverage
- Test with multiple Python versions (3.7+)

## Documentation

- Update README.md if adding new features
- Add examples to `examples/` directory
- Update CHANGELOG.md with your changes
- Write clear docstrings

## Submitting Changes

1. Ensure your code passes all tests
2. Update documentation as needed
3. Add an entry to CHANGELOG.md
4. Submit a pull request with a clear description

## Reporting Issues

When reporting issues, please include:
- Python version
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Error messages (if any)

## Questions?

Feel free to open an issue for questions or discussion!
