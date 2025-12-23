# Contributing to ngx-renamer

Thank you for your interest in contributing to ngx-renamer! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Requirements](#testing-requirements)
- [Documentation](#documentation)
- [Submitting Changes](#submitting-changes)
- [Release Process](#release-process)

---

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors. We expect all participants to:

- Use welcoming and inclusive language
- Be respectful of differing viewpoints and experiences
- Gracefully accept constructive criticism
- Focus on what is best for the project and community
- Show empathy towards other community members

### Unacceptable Behavior

- Harassment, discriminatory language, or personal attacks
- Publishing others' private information without permission
- Trolling, insulting/derogatory comments, or political arguments
- Other conduct that could reasonably be considered inappropriate

### Enforcement

Project maintainers have the right to remove, edit, or reject contributions that don't align with this Code of Conduct. Please report unacceptable behavior by opening an issue or contacting the maintainers.

---

## Getting Started

### Prerequisites

Before contributing, ensure you have:

- Python 3.8 or higher
- Git
- A GitHub account
- Basic understanding of:
  - Python programming
  - Docker and docker-compose
  - pytest testing framework
  - Git version control

### Setting Up Development Environment

1. **Fork and clone the repository:**
   ```bash
   git fork https://github.com/chriskoch/ngx-renamer.git
   cd ngx-renamer
   git remote add upstream https://github.com/chriskoch/ngx-renamer.git
   ```

2. **Create a virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

4. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys for testing
   ```

5. **Verify setup:**
   ```bash
   pytest tests/ -m "not openai and not ollama"
   ```

---

## Development Workflow

### 1. Create a Feature Branch

Always work on a feature branch, never directly on `main` or `dev`:

```bash
git checkout dev
git pull upstream dev
git checkout -b feature/your-feature-name
```

**Branch Naming Conventions:**
- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation updates
- `test/description` - Test improvements
- `refactor/description` - Code refactoring

### 2. Make Your Changes

- Write clean, readable code following [PEP 8](https://peps.python.org/pep-0008/)
- Add type hints to function signatures
- Include docstrings for all public methods
- Write tests for new features and bug fixes
- Update documentation as needed

### 3. Test Your Changes

```bash
# Run all non-API tests
pytest tests/ -m "not openai and not ollama"

# Run specific test file
pytest tests/integration/test_llm_provider_selection.py

# Check code coverage
pytest --cov=modules --cov-report=term-missing

# Ensure >80% coverage for modified modules
```

### 4. Update Documentation

If your changes affect:
- **User features** → Update `README.md`
- **Development workflow** → Update `AGENTS.md`
- **Architecture** → Update `ARCHITECTURE.md`
- **Version changes** → Update `CHANGELOG.md`

### 5. Commit Your Changes

Follow conventional commit format:

```bash
git add .
git commit -m "Add: Brief description of feature

Detailed explanation of what changed and why.
Include any breaking changes or important notes.

Fixes #123"
```

**Commit Message Format:**
- `Add:` - New features
- `Fix:` - Bug fixes
- `Update:` - Changes to existing functionality
- `Docs:` - Documentation updates
- `Test:` - Test additions or modifications
- `Refactor:` - Code refactoring without behavior changes

---

## Coding Standards

### Python Style Guide

Follow [PEP 8](https://peps.python.org/pep-0008/) with these specifics:

**Good Example:**
```python
def generate_title_from_text(self, text: str) -> str:
    """
    Generate an AI-powered title from OCR text.

    Args:
        text: OCR-extracted document content

    Returns:
        Generated title string (max 127 characters)

    Raises:
        ValueError: If text is empty or None
    """
    if not text:
        raise ValueError("Text cannot be empty")

    prompt = self._build_prompt(text)
    response = self._call_llm_api(prompt)
    return self._extract_title(response)
```

**Bad Example:**
```python
# ❌ Avoid this
def gen(t):  # No type hints, unclear name, no docstring
    p = self.make_p(t)
    r = self.call(p)
    return r.strip()
```

### Naming Conventions

- **Classes**: `PascalCase` (e.g., `PaperlessAITitles`, `OpenAITitles`)
- **Functions/Methods**: `snake_case` (e.g., `generate_title`, `_build_prompt`)
- **Private methods**: Prefix with `_` (e.g., `_call_openai_api`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `DEFAULT_MODEL`, `MAX_TITLE_LENGTH`)
- **Test files**: `test_*.py` (e.g., `test_openai_integration.py`)
- **Test functions**: `test_*` (e.g., `test_ollama_title_generation`)

### Code Organization

- Keep functions focused and under 50 lines when possible
- Use descriptive variable names (avoid single letters except loop counters)
- Add comments for complex logic, not obvious code
- Group related functionality together
- Import order: standard library, third-party, local modules

---

## Testing Requirements

### Test Coverage

- **Minimum coverage**: 80% for all modified modules
- Run coverage check: `pytest --cov=modules --cov-report=term-missing`
- All new features **must** include tests
- All bug fixes **must** include regression tests

### Test Markers

Use appropriate pytest markers:

```python
@pytest.mark.integration  # Full integration test
@pytest.mark.openai       # Real OpenAI API call (costs money)
@pytest.mark.ollama       # Real Ollama API call (requires local Ollama)
@pytest.mark.smoke        # Critical smoke test
@pytest.mark.slow         # Slow-running test (>5 seconds)
```

### Writing Tests

**Example test structure:**
```python
import pytest
from modules.openai_titles import OpenAITitles

@pytest.mark.integration
def test_generate_title_from_invoice(temp_settings_openai):
    """Test title generation from invoice text."""
    # Arrange
    ai = OpenAITitles("test-api-key", temp_settings_openai)
    invoice_text = "Invoice #123\nAmazon Web Services\nAmount: $100"

    # Act
    title = ai.generate_title_from_text(invoice_text)

    # Assert
    assert title is not None
    assert len(title) <= 127
    assert "Amazon" in title or "AWS" in title
```

### Testing Best Practices

- ✅ Test both success and failure cases
- ✅ Mock external APIs in unit tests
- ✅ Use fixtures for common setup
- ✅ Write descriptive test names
- ✅ Keep tests independent and isolated
- ❌ Don't commit tests that require API keys without proper markers
- ❌ Don't write tests that depend on network availability

---

## Documentation

### Documentation Requirements

All contributions must include appropriate documentation:

1. **Code Documentation:**
   - Docstrings for all public classes and methods
   - Inline comments for complex logic
   - Type hints for function signatures

2. **User Documentation:**
   - Update README.md if adding user-facing features
   - Include usage examples
   - Update troubleshooting section if relevant

3. **Developer Documentation:**
   - Update AGENTS.md for development workflow changes
   - Update ARCHITECTURE.md for architectural changes
   - Add examples and diagrams where helpful

4. **Changelog:**
   - Add entry to CHANGELOG.md under `[Unreleased]`
   - Categorize as Added/Changed/Fixed/Removed
   - Include relevant issue/PR numbers

### Documentation Style

- Use clear, concise language
- Include code examples where appropriate
- Use markdown formatting consistently
- Link to related documentation
- Keep user docs separate from developer docs

---

## Submitting Changes

### Pull Request Process

1. **Ensure all tests pass:**
   ```bash
   pytest tests/
   ```

2. **Check code coverage:**
   ```bash
   pytest --cov=modules --cov-report=term-missing
   ```

3. **Update documentation:**
   - README.md (if user-facing changes)
   - AGENTS.md (if developer workflow changes)
   - CHANGELOG.md (always)

4. **Push your branch:**
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Create Pull Request:**
   - Go to GitHub repository
   - Click "New Pull Request"
   - Select your branch
   - Fill out PR template completely
   - Link related issues

### Pull Request Guidelines

**Good PR Title:**
```
Add: Structured output support for Gemini provider
```

**Good PR Description:**
```markdown
## Summary
Adds support for Google Gemini as a new LLM provider with structured JSON outputs.

## Changes
- Created `modules/gemini_titles.py` with GeminiTitles class
- Added Gemini configuration to settings.yaml
- Updated factory pattern in PaperlessAITitles
- Added 8 integration tests for Gemini provider
- Updated documentation (README.md, AGENTS.md, ARCHITECTURE.md)

## Testing
- All existing tests pass
- New Gemini tests pass with API key
- Code coverage: 87% (above 80% threshold)

## Breaking Changes
None - fully backward compatible

## Related Issues
Fixes #42
```

### PR Review Process

1. **Automated Checks:**
   - GitHub Actions will run tests
   - Documentation validation will check version consistency
   - All checks must pass before merge

2. **Code Review:**
   - Maintainer will review your code
   - Address any feedback or requested changes
   - Update PR as needed

3. **Approval and Merge:**
   - Once approved, maintainer will merge
   - PR will be squashed and merged to `dev` branch
   - Eventually released from `dev` to `main`

---

## Release Process

### For Contributors

Contributors don't need to worry about releases - maintainers handle this. However, understanding the process helps:

1. **Development happens on `dev` branch**
2. **Features accumulate in `dev`**
3. **Periodic releases merge `dev` → `main`**
4. **Version bumping is automated** (bump2version)
5. **GitHub releases are created** with changelog

### For Maintainers

See [RELEASING.md](RELEASING.md) for complete release process.

---

## Common Contribution Scenarios

### Adding a New LLM Provider

1. Create new provider class inheriting from `BaseLLMProvider`
2. Implement required methods (`generate_title_from_text`)
3. Update factory pattern in `PaperlessAITitles`
4. Add provider configuration to `settings.yaml`
5. Write integration tests (minimum 8 tests)
6. Update documentation (README, AGENTS, ARCHITECTURE)

See [AGENTS.md - Adding a New LLM Provider](AGENTS.md#adding-a-new-llm-provider) for details.

### Fixing a Bug

1. Create issue describing the bug
2. Create fix branch: `fix/issue-123-description`
3. Write failing test that reproduces bug
4. Fix the bug
5. Verify test now passes
6. Add regression test to prevent recurrence
7. Update CHANGELOG.md
8. Submit PR referencing issue

### Improving Documentation

1. Create branch: `docs/description`
2. Make documentation improvements
3. Verify links work and formatting is correct
4. Submit PR with clear description of changes

---

## Getting Help

### Resources

- **User Documentation**: [README.md](README.md)
- **Developer Guide**: [AGENTS.md](AGENTS.md)
- **Architecture Details**: [ARCHITECTURE.md](ARCHITECTURE.md)
- **Release Process**: [RELEASING.md](RELEASING.md)
- **Automation Guide**: [.github/AUTOMATION.md](.github/AUTOMATION.md)

### Support Channels

- **Issues**: https://github.com/chriskoch/ngx-renamer/issues
- **Discussions**: https://github.com/chriskoch/ngx-renamer/discussions
- **Pull Requests**: https://github.com/chriskoch/ngx-renamer/pulls

### Questions?

If you have questions about contributing:

1. Check existing documentation first
2. Search closed issues for similar questions
3. Open a new discussion (not an issue) for general questions
4. Open an issue for bug reports or feature requests

---

## Recognition

Contributors will be:
- Listed in git commit history
- Mentioned in CHANGELOG.md for significant contributions
- Credited in release notes when applicable

We appreciate all contributions, whether they're:
- Code improvements
- Bug fixes
- Documentation updates
- Test additions
- Feature suggestions
- Bug reports

Thank you for contributing to ngx-renamer! 🎉

---

## License

By contributing to ngx-renamer, you agree that your contributions will be licensed under the [GPL-3.0 License](LICENSE).

---

**Version**: 1.2.2
**Last Updated**: 2024-12-23
