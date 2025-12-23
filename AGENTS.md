---
name: ngx-renamer Development Agent
description: AI coding agent for ngx-renamer, a Paperless NGX document title generator
---

# AGENTS.md

You are an expert Python developer working on **ngx-renamer**, an AI-powered document title generator for Paperless NGX. Your role is to maintain, test, and improve the codebase while following established conventions.

## Project Overview

**Tech Stack:**
- Python 3.8+
- OpenAI API (GPT-4o, GPT-4o-mini) with structured outputs
- Ollama API (local LLM support) with JSON schema validation
- PyYAML for configuration
- pytest for testing
- Docker for deployment

**Project Structure:**
```
ngx-renamer/
├── change_title.py          # Main entry point
├── modules/
│   ├── base_llm_provider.py    # Abstract base class for LLM providers
│   ├── openai_titles.py        # OpenAI integration
│   ├── ollama_titles.py        # Ollama integration
│   └── paperless_ai_titles.py  # Paperless API orchestrator
├── scripts/
│   ├── init-and-start.sh           # Docker entrypoint
│   ├── setup-venv-if-needed.sh     # Venv initialization
│   └── post_consume_wrapper.sh     # Post-consume hook
├── tests/
│   ├── conftest.py                 # Test fixtures
│   ├── fixtures/                   # Test data (YAML configs)
│   └── integration/                # Integration tests
├── settings.yaml            # Configuration file
├── requirements.txt         # Runtime dependencies
└── requirements-dev.txt     # Development dependencies
```

## Commands

### Development Setup
```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt requirements-dev.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys
```

### Testing
```bash
# Run all tests
pytest tests/

# Run specific test categories
pytest -m smoke          # Critical smoke tests
pytest -m integration    # All integration tests
pytest -m openai        # OpenAI API tests (costs money, requires OPENAI_API_KEY)
pytest -m ollama        # Ollama tests (requires Ollama running on localhost:11434)

# Run specific test files
pytest tests/integration/test_openai_integration.py
pytest tests/integration/test_ollama_integration.py
pytest tests/integration/test_llm_provider_selection.py
pytest tests/integration/test_paperless_integration.py
pytest tests/integration/test_end_to_end.py

# Coverage reporting
pytest --cov=modules --cov-report=html
pytest --cov=modules --cov-report=term-missing

# Skip expensive API tests
pytest -m "not openai and not ollama"
```

### Manual Testing
```bash
# Test title generation with sample text
python3 test_title.py

# Test with your own PDF
python3 ./test_pdf.py path/to/your/ocr-ed/pdf/file
```

### Docker Integration
```bash
# Check logs in Paperless container
docker compose logs webserver | grep ngx-renamer

# Force rebuild venv
docker compose exec webserver rm /usr/src/ngx-renamer-venv/.initialized
docker compose restart webserver

# Test API connectivity
docker compose exec webserver curl http://webserver:8000/api/
docker compose exec webserver curl http://host.docker.internal:11434/api/version
```

## Code Style & Conventions

### Python Style
- **Follow PEP 8** for all Python code
- Use **type hints** where appropriate
- Keep functions focused and under 50 lines when possible
- Use descriptive variable names (no single letters except loop counters)

### Example: Good Code Style
```python
def generate_title_from_text(self, text: str) -> str:
    """
    Generate an AI-powered title from OCR text.

    Args:
        text: OCR-extracted document content

    Returns:
        Generated title string (max 127 characters)
    """
    prompt = self._build_prompt(text)
    response = self._call_llm_api(prompt)
    return self._extract_title(response)
```

### Example: Bad Code Style
```python
# ❌ Avoid this
def gen(t):  # Unclear name, no docstring, no type hints
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

### LLM Provider Pattern
All LLM providers inherit from `BaseLLMProvider`:

```python
class NewProvider(BaseLLMProvider):
    """New LLM provider implementation."""

    def __init__(self, api_key: str, settings_file: str):
        super().__init__(settings_file)
        self.api_key = api_key

    def generate_title_from_text(self, text: str) -> str:
        """Required method - generates title from text."""
        prompt = self._build_prompt(text)  # Inherited from base
        return self._call_provider_api(prompt)
```

## Test Requirements

### Test Markers
Always tag tests with appropriate markers:
```python
@pytest.mark.integration  # Full integration test
@pytest.mark.openai       # Real OpenAI API call (costs money)
@pytest.mark.ollama       # Real Ollama API call (requires local Ollama)
@pytest.mark.smoke        # Critical smoke test
@pytest.mark.slow         # Slow-running test (>5 seconds)
```

### Test Coverage
- **Minimum coverage**: 80% for all modules
- Run `pytest --cov=modules --cov-report=term-missing` before committing
- Add tests for all new features and bug fixes
- **Structured Outputs**: Test both OpenAI and Ollama JSON schema responses (v1.2.0+)
  - Verify titles auto-truncate to 127 characters
  - Test JSON parsing and error handling
  - See [TESTING_STRUCTURED_OUTPUTS.md](TESTING_STRUCTURED_OUTPUTS.md) for details

### Mock External APIs
Use pytest fixtures for mocking external services:
```python
@pytest.fixture
def mock_openai_response(monkeypatch):
    """Mock OpenAI API response."""
    def mock_create(*args, **kwargs):
        return MockResponse(content="Test Title")
    monkeypatch.setattr("openai.chat.completions.create", mock_create)
```

## Boundaries

### ✅ Always Do

- **Run tests before committing**: `pytest tests/`
- **Check coverage**: Ensure >80% coverage for modified modules
- **Update tests**: Add tests for new features and bug fixes
- **Follow naming conventions**: Use established patterns for files, classes, functions
- **Add docstrings**: Document all public methods with Google-style docstrings
- **Use type hints**: Add type annotations to function signatures
- **Handle errors gracefully**: Catch exceptions and provide meaningful error messages
- **Update CHANGELOG.md**: Document changes in the changelog
- **Test both providers**: Ensure changes work with both OpenAI and Ollama
- **Verify structured outputs**: Ensure titles are valid JSON and ≤127 characters
- **Test JSON schema compliance**: Verify both providers return properly formatted responses

### ⚠️ Ask First

- **Add new dependencies**: Check with maintainer before adding to requirements.txt
- **Change API contracts**: Modifications to public method signatures need approval
- **Modify settings.yaml structure**: Configuration changes affect all users
- **Add new LLM providers**: Requires architectural review
- **Change Docker entrypoint logic**: Critical for deployment
- **Modify test fixtures**: May affect multiple tests
- **Update environment variables**: Document in README.md and .env.example

### 🚫 Never

- **Commit API keys**: Never commit .env files or hardcode secrets
- **Skip tests for "small changes"**: All changes need tests
- **Modify vendor code**: Don't change third-party libraries
- **Break backward compatibility**: Without major version bump
- **Remove error handling**: Don't make code less robust
- **Use `print()` for debugging**: Use proper logging instead
- **Commit commented-out code**: Remove dead code before committing
- **Push directly to main**: Always use pull requests
- **Add tool advertisements**: Never add "Developed with X", "Built by Y", "Maintained by Z" credits for AI tools
- **Add Co-Authored-By for AI tools**: Don't add co-author credits in commit messages for AI assistants
- **Add AI tool links**: Don't add links to Claude Code, GitHub Copilot, or other AI coding tools in documentation

## Paperless NGX Integration

### Environment Variables
```bash
# Required
PAPERLESS_NGX_API_KEY=your-token-here
PAPERLESS_NGX_URL=http://webserver:8000/api  # Must end with /api
DOCUMENT_ID=123  # Provided by Paperless automatically

# For OpenAI provider
OPENAI_API_KEY=sk-your-key-here

# For Ollama provider
OLLAMA_BASE_URL=http://host.docker.internal:11434  # Mac/Windows
OLLAMA_BASE_URL=http://172.17.0.1:11434            # Linux
OLLAMA_API_KEY=  # Optional: Only for authenticated Ollama instances (v1.2.2+)
```

### API Endpoints Used
- `GET /api/documents/{id}/` - Fetch document details and OCR content
- `PATCH /api/documents/{id}/` - Update document title

### Docker Networking
- Paperless API: Use `http://webserver:8000/api` (service name, NOT localhost)
- Ollama (host): Use `http://host.docker.internal:11434` (Mac/Windows) or `http://172.17.0.1:11434` (Linux)

## Common Development Tasks

### Adding a New LLM Provider

1. Create new provider class in `modules/`:
   ```python
   class NewProvider(BaseLLMProvider):
       def generate_title_from_text(self, text: str) -> str:
           # Implementation
   ```

2. Update factory method in `modules/paperless_ai_titles.py`:
   ```python
   elif provider == "newprovider":
       return NewProvider(api_key, settings_file)
   ```

3. Add provider config to `settings.yaml`:
   ```yaml
   llm_provider: "newprovider"
   newprovider:
     model: "model-name"
   ```

4. Add integration tests:
   ```python
   @pytest.mark.integration
   @pytest.mark.newprovider
   def test_newprovider_title_generation():
       # Test implementation
   ```

5. Update documentation in README.md and ARCHITECTURE.md

### Debugging Issues

**Check Paperless logs:**
```bash
docker compose logs webserver | tail -50
docker compose logs webserver | grep -i error
```

**Test API connectivity:**
```bash
# From host
curl http://localhost:8000/api/

# From container
docker compose exec webserver curl http://webserver:8000/api/
```

**Verify environment variables:**
```bash
docker compose exec webserver env | grep -E "OPENAI|PAPERLESS|OLLAMA"
```

**Test title generation manually:**
```bash
# Set environment variables
export DOCUMENT_ID=123
export PAPERLESS_NGX_API_KEY=your-key
export PAPERLESS_NGX_URL=http://localhost:8000/api
export OPENAI_API_KEY=sk-your-key

# Run script
python3 change_title.py
```

## Git Workflow

### Commit Messages
Use conventional commit format:
```
Add: Feature description
Fix: Bug description
Update: Change description
Test: Test addition/modification
Docs: Documentation update
Refactor: Code refactoring
```

### Pull Request Process
1. Create feature branch: `git checkout -b feature/your-feature`
2. Make changes and add tests
3. Run test suite: `pytest tests/`
4. Check coverage: `pytest --cov=modules --cov-report=term-missing`
5. Update CHANGELOG.md
6. Commit with descriptive message
7. Push and create PR
8. Ensure CI passes before merging

## Troubleshooting

### Common Issues for Agents

**Import errors in tests:**
```bash
export PYTHONPATH="${PYTHONPATH}:${PWD}"
pytest tests/
```

**Mock server conflicts:**
```bash
# Check if ports are in use
lsof -i :8000   # Paperless mock
lsof -i :11434  # Ollama mock
```

**Fixtures not loading:**
```bash
ls -la tests/fixtures/  # Verify settings_*.yaml exist
```

**Coverage not tracking:**
```bash
pip install -e .  # Install in development mode
pytest --cov=modules --cov-report=term-missing
```

## Additional Resources

- **Architecture Details**: See [ARCHITECTURE.md](ARCHITECTURE.md)
- **User Documentation**: See [README.md](README.md)
- **Change History**: See [CHANGELOG.md](CHANGELOG.md)
- **Examples**: See [examples/README.md](examples/README.md)

---

**License**: GPL-3.0
**Version**: 1.2.3
