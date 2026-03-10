# Contributing to THRESHOLD_ONSET

Thank you for your interest in THRESHOLD_ONSET! 

## Important Notice

**The entire project is FROZEN FOREVER.** See [PROJECT_FREEZE.md](PROJECT_FREEZE.md).

- Phases 0-4: `threshold_onset/phase0` through `phase4` — FROZEN
- Phases 5-9: `threshold_onset/semantic/` — FROZEN
- Symbol Decoder: `threshold_onset/semantic/phase9/symbol_decoder.py` — FROZEN
- Integration: `integration/` — FROZEN

**No modifications to frozen code are permitted.** This project is a structure-first language model: text in, structure, text out. No embeddings. No transformers. No third-party logic.

## What Can Be Contributed

### Documentation
- Improvements to existing documentation
- Additional examples
- Clarifications and corrections
- Translation of documentation

### Tests
- Additional test cases for validation
- Edge case testing
- Performance benchmarks

### Tools
- Improvements to version control tools
- Development utilities
- Build and deployment scripts

### Submodules
- Improvements to `santok_complete` tokenization module
- Additional utilities and examples

### Bug Fixes
- Non-core bug fixes (documentation, build scripts, etc.)
- Test fixes

## What Cannot Be Changed

### FROZEN FOREVER - Do Not Modify
- `threshold_onset/phase0/` through `phase4/` - Structure foundation
- `threshold_onset/semantic/` - Phases 5-9, decoder
- `integration/` - Unified system, run_complete, fluency_text_generator, etc.
- `run_all.py`, `run_all.bat` - Full project run

All frozen components are locked. See [PROJECT_FREEZE.md](PROJECT_FREEZE.md).

## Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/chavalasantosh/THRESHOLDONSET.git
   cd THRESHOLDONSET
   ```

2. **Install in development mode**
   ```bash
   pip install -e .
   ```

3. **Install optional development dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Code Standards

- **Python standard library only** for core system
- **Python 3.8+** compatibility required
- **Clean, minimal code** - no unnecessary dependencies
- **Documentation co-located** with code
- **Type hints** where appropriate
- **Docstrings** for all public functions and classes

## Testing

- Run existing tests:
  ```bash
  python run_all.py
  python -m pytest tests/ threshold_onset/semantic/tests/ -v
  ```

- All tests must pass before submitting changes
- Add tests for any new functionality

## Documentation

- Update relevant documentation when making changes
- Keep documentation in markdown format
- Use clear, concise language
- Include examples where helpful

## Submitting Changes

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes** (respecting frozen phases)
4. **Run tests** to ensure nothing breaks
5. **Update documentation** as needed
6. **Commit with clear messages**
7. **Submit a pull request** with a detailed description

## Pull Request Guidelines

- **Clear title** describing the change
- **Detailed description** of what changed and why
- **Reference related issues** if applicable
- **Confirm no frozen phases were modified**
- **Include test results** if adding tests

## Reporting Issues

When reporting issues:

- **Do not report** issues with frozen phase implementations (they are by design)
- **Include**: Python version, OS, steps to reproduce
- **Provide**: Expected vs actual behavior
- **Add**: Error messages and stack traces if applicable

## Questions?

For questions or discussions:
- Open an issue on GitHub
- Check existing documentation in `/docs`
- Review phase-specific documentation in `threshold_onset/phaseX/phaseX/`

## Philosophy

THRESHOLD_ONSET is built on the principle:

> **कार्य (kārya) happens before ज्ञान (jñāna)**
>
> **Function stabilizes before knowledge appears.**

The system proves that structure emerges naturally before language exists. This is a foundational research system, not a general-purpose framework.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for respecting the frozen nature of the core phases while contributing to improvements in documentation, tests, and tools!
