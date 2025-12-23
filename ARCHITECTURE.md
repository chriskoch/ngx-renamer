# ngx-renamer Architecture

> **For AI Coding Agents**: See [AGENTS.md](AGENTS.md) for development commands, testing, and code conventions.
>
> **For Human Developers**: This document provides detailed architecture documentation.

## Overview

ngx-renamer is an AI-powered document title generator for Paperless NGX that automatically renames documents using AI language models. It supports multiple LLM providers including OpenAI GPT models and local Ollama models. This document describes the architecture, components, and data flow.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      Paperless NGX Container                     │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  1. Document Consumption (OCR, Indexing)                   │ │
│  └────────────────────────────────────────────────────────────┘ │
│                            │                                      │
│                            ▼                                      │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  2. Post-Consume Hook Trigger                              │ │
│  │     PAPERLESS_POST_CONSUME_SCRIPT                          │ │
│  └────────────────────────────────────────────────────────────┘ │
│                            │                                      │
│                            ▼                                      │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  3. ngx-renamer Execution                                  │ │
│  │                                                              │ │
│  │     ┌──────────────────────────────────────────────┐       │ │
│  │     │ init-and-start.sh (Entrypoint)               │       │ │
│  │     │ - Checks venv existence                      │       │ │
│  │     │ - Initializes if needed                      │       │ │
│  │     │ - Delegates to Paperless entrypoint          │       │ │
│  │     └──────────────────────────────────────────────┘       │ │
│  │                                                              │ │
│  │     ┌──────────────────────────────────────────────┐       │ │
│  │     │ post_consume_wrapper.sh                      │       │ │
│  │     │ - Activates venv                             │       │ │
│  │     │ - Sets environment variables                 │       │ │
│  │     │ - Executes change_title.py                   │       │ │
│  │     └──────────────────────────────────────────────┘       │ │
│  │                                                              │ │
│  │     ┌──────────────────────────────────────────────┐       │ │
│  │     │ change_title.py (Main Orchestrator)          │       │ │
│  │     │ - Loads configuration                        │       │ │
│  │     │ - Instantiates PaperlessAITitles             │       │ │
│  │     │ - Triggers title generation                  │       │ │
│  │     └──────────────────────────────────────────────┘       │ │
│  │                                                              │ │
│  └────────────────────────────────────────────────────────────┘ │
│                            │                                      │
│                            ▼                                      │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  4. PaperlessAITitles Agent (Orchestrator)                │ │
│  │     - Fetches document via Paperless API                   │ │
│  │     - Extracts OCR content                                 │ │
│  │     - Selects LLM provider (OpenAI or Ollama)              │ │
│  │     - Delegates to provider agent                          │ │
│  │     - Updates document title via Paperless API             │ │
│  └────────────────────────────────────────────────────────────┘ │
│                            │                                      │
└────────────────────────────┼──────────────────────────────────────┘
                             │
                    ┌────────┴────────┐
                    ▼                 ▼
       ┌─────────────────────┐  ┌──────────────────────┐
       │   OpenAI Provider   │  │   Ollama Provider    │
       │  - GPT-4o           │  │  - Local models      │
       │  - GPT-4o-mini      │  │  - gpt-oss:latest    │
       │  - Cloud API        │  │  - No API costs      │
       └─────────────────────┘  └──────────────────────┘
                │                         │
                └────────┬────────────────┘
                         ▼
              Generates optimized title
              Returns to PaperlessAITitles
```

## Core Components

### 1. Entry Point & Initialization

#### `scripts/init-and-start.sh`
**Purpose**: Custom entrypoint wrapper that ensures Python environment is ready before Paperless starts.

**Responsibilities**:
- Check if virtual environment exists
- Detect if requirements.txt has changed
- Trigger venv initialization if needed
- Delegate to Paperless's original entrypoint

**Flow**:
```bash
if [ ! -f "$VENV_PATH/bin/activate" ]; then
    # Initialize new venv
    /usr/src/ngx-renamer/scripts/setup-venv-if-needed.sh
else
    # Venv exists, proceed to Paperless startup
    exec /sbin/docker-entrypoint.sh "$@"
fi
```

#### `scripts/setup-venv-if-needed.sh`
**Purpose**: Conditional virtual environment setup and dependency installation.

**Responsibilities**:
- Create Python venv at `/usr/src/ngx-renamer-venv`
- Install dependencies from `requirements.txt`
- Create `.initialized` marker file
- Handle dependency updates

**Key Logic**:
```bash
# Check for activate file, not just directory (Docker volume mount fix)
if [ ! -f "$VENV_PATH/bin/activate" ]; then
    python3 -m venv "$VENV_PATH"
fi
```

### 2. Execution Wrapper

#### `scripts/post_consume_wrapper.sh`
**Purpose**: Post-consume hook that bridges Paperless and the Python environment.

**Responsibilities**:
- Activate the persistent venv
- Set environment variables (RUN_DIR)
- Execute the main Python script
- Handle errors gracefully

**Environment**:
- `DOCUMENT_ID`: Provided by Paperless NGX
- `RUN_DIR`: Path to ngx-renamer source

### 3. Main Orchestrator

#### `change_title.py`
**Purpose**: Main entry point for title generation workflow.

**Components**:
```python
def main():
    # 1. Load environment variables
    load_dotenv()  # Support both .env file and env vars

    # 2. Extract configuration
    document_id = os.environ.get('DOCUMENT_ID')
    paperless_url = os.getenv("PAPERLESS_NGX_URL")
    paperless_api_key = os.getenv("PAPERLESS_NGX_API_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")

    # 3. Instantiate agent
    ai = PaperlessAITitles(
        openai_api_key,
        paperless_url,
        paperless_api_key,
        settings_path
    )

    # 4. Execute workflow
    ai.generate_and_update_title(document_id)
```

**Configuration Sources** (priority order):
1. Environment variables from docker-compose
2. `.env` file in ngx-renamer directory
3. Default values

### 4. Paperless Integration Agent

#### `modules/paperless_ai_titles.py`
**Purpose**: Orchestrator that handles Paperless NGX API interactions and LLM provider selection.

**Architecture**: Factory pattern for provider selection based on configuration.

**Key Methods**:

##### `_create_llm_provider()`
**Factory method** that instantiates the appropriate LLM provider:
```python
provider = settings.get("llm_provider", "openai").lower()

if provider == "openai":
    return OpenAITitles(openai_api_key, settings_file)
elif provider == "ollama":
    return OllamaTitles(ollama_base_url, settings_file)
else:
    raise ValueError(f"Unknown LLM provider '{provider}'")
```

##### `__get_document_details(document_id)`
```python
GET /api/documents/{document_id}/
Authorization: Token {paperless_api_key}

Returns: {
    "id": 123,
    "title": "original_filename.pdf",
    "content": "OCR-extracted text...",
    ...
}
```

##### `__update_document_title(document_id, new_title)`
```python
PATCH /api/documents/{document_id}/
Authorization: Token {paperless_api_key}
Content-Type: application/json

Body: {
    "title": "AI-Generated - Brief Description"
}
```

##### `generate_and_update_title(document_id)`
**Workflow**:
1. Fetch document details from Paperless
2. Extract OCR content
3. Call OpenAI agent to generate title
4. Update document with new title
5. Handle errors at each step

### 5. LLM Provider Agents

All providers inherit from `BaseLLMProvider` which provides common functionality:
- Settings loading from YAML
- Prompt building with date handling
- Shared configuration structure

#### `modules/openai_titles.py` - OpenAI Provider
**Purpose**: Handles all interactions with OpenAI API and prompt engineering.

**Key Methods**:

#### `modules/ollama_titles.py` - Ollama Provider
**Purpose**: Handles interactions with local Ollama API for on-premise/offline title generation.

**Key Features**:
- No API costs (runs locally)
- Privacy-focused (no data leaves your network)
- Support for various open-source models
- Same prompt structure as OpenAI

**Key Methods**:

##### `__call_ollama_api(content, role="user")`
```python
ollama.Client(host=ollama_base_url).chat(
    model="gpt-oss:latest",
    messages=[{"role": "user", "content": prompt}]
)
```

**Error Handling**:
- Model not found → Suggests `ollama pull` command
- Service unavailable → Returns None gracefully
- Connection errors → Logged with helpful debug info

### 6. Shared Configuration

##### Settings File Structure (`settings.yaml`)
Supports both providers with unified configuration:
```yaml
# Provider Selection
llm_provider: "ollama"  # or "openai"

# Provider-specific settings
openai:
  model: "gpt-4o"

ollama:
  model: "gpt-oss:latest"

# Shared settings
with_date: false
prompt:
  main: "System instruction for title generation..."
  with_date: "Date extraction instructions..."
  no_date: ""
```

##### `__ask_chat_gpt(content, role="user")`
```python
OpenAI.chat.completions.create(
    model="gpt-4o",
    messages=[{
        "role": "user",
        "content": prompt
    }]
)
```

##### `generate_title_from_text(text)`
**Workflow**:
1. Load settings from YAML
2. Build prompt based on configuration
3. Append date instructions if `with_date: true`
4. Add document content
5. Call OpenAI API
6. Extract and return generated title

**Prompt Structure**:
```
{main_prompt}
{with_date_or_no_date_prompt}
{pre_content_marker}
{document_text}
{post_content_marker}
```

## Data Flow

### Normal Document Processing

```
1. User uploads document to Paperless
   ↓
2. Paperless performs OCR and indexing
   ↓
3. Paperless triggers post-consume script
   PAPERLESS_POST_CONSUME_SCRIPT=/usr/src/ngx-renamer/scripts/post_consume_wrapper.sh
   Environment: DOCUMENT_ID=123
   ↓
4. post_consume_wrapper.sh activates venv and runs change_title.py
   ↓
5. change_title.py instantiates PaperlessAITitles
   ↓
6. PaperlessAITitles.generate_and_update_title(123)
   ├─ 6a. Load settings and select provider (OpenAI or Ollama)
   ├─ 6b. GET /api/documents/123/ (fetch document)
   ├─ 6c. Extract content: "OCR text..."
   ├─ 6d. LLMProvider.generate_title_from_text("OCR text...")
   │      ├─ Build prompt from settings
   │      ├─ Call LLM API (OpenAI or Ollama)
   │      └─ Return: "Amazon - Monthly Subscription Invoice"
   └─ 6e. PATCH /api/documents/123/ (update title)
   ↓
7. Paperless saves document with new AI-generated title
```

### Error Handling

Each layer handles errors independently:

**Layer 1: Paperless API**
- 401 Unauthorized → Invalid API token
- 404 Not Found → Document doesn't exist
- Network errors → Retry logic

**Layer 2: OpenAI API**
- 401 Unauthorized → Invalid OpenAI key
- 429 Rate Limit → Back off and retry
- Timeout → Log and skip

**Layer 3: Script Execution**
- Missing environment → Error message
- Failed venv activation → Initialization error
- Python errors → Logged to Paperless console

## Installation Methods

### Method 1: Auto-Init (Recommended)

**Components Required**:
- Docker volume: `ngx-renamer-venv`
- Custom entrypoint: `init-and-start.sh`
- Volume mount: `./ngx-renamer:/usr/src/ngx-renamer:ro`
- Post-consume script: `post_consume_wrapper.sh`

**Advantages**:
- Zero manual setup
- Automatic venv initialization
- Persistent across restarts
- Dependency change detection

### Method 2: Standalone Single-File

**Components Required**:
- Single file: `ngx-renamer-standalone.py`
- Environment variables only
- No venv needed

**Advantages**:
- Ultra-minimal setup
- No build step
- Easier to understand
- Good for simple deployments

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DOCUMENT_ID` | Yes | - | Provided by Paperless automatically |
| `OPENAI_API_KEY` | Conditional | - | Required if using OpenAI provider |
| `OLLAMA_BASE_URL` | Conditional | `http://localhost:11434` | Required if using Ollama provider |
| `PAPERLESS_NGX_API_KEY` | Yes | - | Paperless API token |
| `PAPERLESS_NGX_URL` | Yes | - | Paperless API URL (must include `/api`) |
| `OPENAI_MODEL` | No | `gpt-4o-mini` | OpenAI model to use (deprecated, use settings.yaml) |
| `TITLE_WITH_DATE` | No | `false` | Include date in title |
| `RUN_DIR` | No | - | Script runtime directory |

### Settings File (settings.yaml)

```yaml
# ============================================================================
# LLM Provider Configuration
# ============================================================================
# Choose which LLM provider to use: "openai" or "ollama"
llm_provider: "ollama"  # options: "openai" or "ollama"

# ============================================================================
# OpenAI-specific Configuration
# ============================================================================
openai:
  model: "gpt-4o"  # OpenAI model to use

# ============================================================================
# Ollama-specific Configuration
# ============================================================================
ollama:
  model: "gpt-oss:latest"  # Ollama model (must be pulled first)

# ============================================================================
# Shared Configuration
# ============================================================================
with_date: false  # Include date prefix in title

# Prompt engineering (shared by all providers)
prompt:
  main: |
    System instructions for title generation
    Requirements: 50-100 chars, max 127
    Format: "Sender - Brief Description"

  with_date: |
    Additional instructions for date extraction

  no_date: ""

# ============================================================================
# Legacy Configuration (backward compatibility)
# ============================================================================
openai_model: "gpt-4o"  # Deprecated: Use openai.model instead
```

## Advanced LLM Provider Configuration

### OpenAI Provider Details

**Available Models:**
- `gpt-4o` - High quality, higher cost (~$5/million input tokens)
- `gpt-4o-mini` - Good quality, lower cost (~$0.15/million input tokens)
- `gpt-3.5-turbo` - Fastest, lowest cost (deprecated for this use case)

**Model Selection Strategy:**
- **Development/Testing:** Use `gpt-4o-mini` for fast iteration and low costs
- **Production:** Use `gpt-4o` for best quality if budget allows
- **High Volume:** Consider `gpt-4o-mini` with optimized prompts

### Ollama Provider Details

**Recommended Models:**
- `gpt-oss:latest` - Default, good balance (1.5GB)
- `llama3:8b` - Fast, efficient (4.7GB)
- `llama3:70b` - Highest quality, slow (39GB)
- `mistral:latest` - Fast alternative (4.1GB)
- `qwen2.5:latest` - Multilingual support (4.7GB)

**Model Performance Comparison:**

| Model | Size | Speed | Quality | Multilingual |
|-------|------|-------|---------|--------------|
| gpt-oss | 1.5GB | Fast | Good | Yes |
| llama3:8b | 4.7GB | Fast | Very Good | Limited |
| llama3:70b | 39GB | Slow | Excellent | Limited |
| mistral | 4.1GB | Fast | Good | Limited |
| qwen2.5 | 4.7GB | Medium | Very Good | Excellent |

**Docker Networking for Ollama:**

When running Paperless in Docker and Ollama on the host:

```yaml
# For Mac/Windows (docker-compose.env)
OLLAMA_BASE_URL=http://host.docker.internal:11434

# For Linux (docker-compose.env)
OLLAMA_BASE_URL=http://172.17.0.1:11434

# If Ollama is also in Docker (same docker-compose.yml)
services:
  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"

  webserver:
    environment:
      OLLAMA_BASE_URL: http://ollama:11434
```

**Verify Ollama connectivity from container:**
```bash
docker compose exec webserver curl http://host.docker.internal:11434/api/version
```

### Provider Selection Logic

The factory pattern in `PaperlessAITitles` selects the provider:

```python
def _create_llm_provider(self):
    """Factory method for LLM provider selection"""
    provider = self.settings.get("llm_provider", "openai").lower()

    if provider == "openai":
        return OpenAITitles(
            openai_api_key=self.openai_api_key,
            settings_file=self.settings_file
        )
    elif provider == "ollama":
        ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        return OllamaTitles(
            ollama_base_url=ollama_base_url,
            settings_file=self.settings_file
        )
    else:
        raise ValueError(f"Unknown LLM provider: {provider}")
```

**Backward Compatibility:**
- Old `openai_model` setting still works (maps to `openai.model`)
- Missing `llm_provider` defaults to `"openai"`
- Environment variables override settings.yaml values

## Testing

### Test Structure

```
tests/
├── conftest.py              # Fixtures and configuration
├── fixtures/                # Test data
│   ├── settings_valid.yaml
│   ├── settings_ollama.yaml
│   ├── settings_openai_new_format.yaml
│   ├── settings_invalid_provider.yaml
│   └── ...
└── integration/             # Integration tests
    ├── test_end_to_end.py                 # Full workflow
    ├── test_openai_integration.py         # OpenAI API tests
    ├── test_ollama_integration.py         # Ollama API tests
    ├── test_llm_provider_selection.py     # Multi-provider tests
    └── test_paperless_integration.py      # Paperless API tests
```

### Test Markers

```python
@pytest.mark.integration  # Full integration test
@pytest.mark.openai       # Real OpenAI API call (requires API key, costs money)
@pytest.mark.ollama       # Real Ollama API call (requires Ollama running locally)
@pytest.mark.smoke        # Critical smoke test
@pytest.mark.slow         # Slow-running test
```

### Running Tests

```bash
# Run all tests
pytest

# Run only OpenAI tests (requires OPENAI_API_KEY)
pytest -m openai

# Run only Ollama tests (requires Ollama running)
OLLAMA_BASE_URL=http://localhost:11434 pytest -m ollama

# Run provider selection tests (no API calls)
pytest tests/integration/test_llm_provider_selection.py::TestLLMProviderSelection
```

## Security Considerations

### API Keys
- Never commit `.env` files (gitignored)
- Use environment variables in production
- Rotate keys regularly

### Network Security
- All API calls use HTTPS (OpenAI)
- Internal Docker networking (Paperless)
- No external access required for Paperless API

### Container Security
- Read-only source mount (`:ro`)
- Minimal permissions
- Isolated venv in separate volume
- No root execution required

## Performance

### Initialization
- First start: 30-60 seconds (venv creation)
- Subsequent starts: Instant (venv cached)

### Title Generation
- API latency: 1-3 seconds (depends on document length)
- No impact on document consumption
- Runs asynchronously after OCR

### Resource Usage
- Memory: ~50MB (Python + dependencies)
- Disk: ~200MB (venv + dependencies)
- CPU: Minimal (I/O bound)

## Development Setup

### Local Development Environment

For developing and testing ngx-renamer without integrating it into Paperless NGX:

**1. Create virtual environment**
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

**2. Install dependencies**
```bash
# Runtime dependencies
pip install -r requirements.txt

# Development dependencies (includes pytest, coverage, etc.)
pip install -r requirements-dev.txt
```

**3. Configure environment**
```bash
cp .env.example .env
nano .env  # Add your API keys
```

### Testing Scripts

**Quick title generation test:**
```bash
# Test with sample American law text
python3 test_title.py
```

**Test with your own PDF:**
```bash
# Extract and analyze OCR text from a PDF
python3 ./test_pdf.py path/to/your/ocr-ed/pdf/file
```

### Running the Test Suite

ngx-renamer includes comprehensive integration tests for all providers.

**Run all tests:**
```bash
pytest tests/
```

**Run specific test categories:**
```bash
# Critical smoke tests
pytest -m smoke

# All integration tests
pytest -m integration

# OpenAI API tests (requires API key, costs money)
pytest -m openai

# Ollama API tests (requires Ollama running locally)
pytest -m ollama
```

**Test specific providers:**
```bash
# OpenAI integration
pytest tests/integration/test_openai_integration.py

# Ollama integration
pytest tests/integration/test_ollama_integration.py

# Multi-provider selection logic
pytest tests/integration/test_llm_provider_selection.py

# Paperless API integration
pytest tests/integration/test_paperless_integration.py

# End-to-end workflow
pytest tests/integration/test_end_to_end.py
```

**Coverage reporting:**
```bash
# Generate HTML coverage report
pytest --cov=modules --cov-report=html

# View coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

**Environment-specific testing:**
```bash
# Test with Ollama (requires Ollama running on localhost:11434)
OLLAMA_BASE_URL=http://localhost:11434 pytest -m ollama

# Test with OpenAI (requires OPENAI_API_KEY in .env)
pytest -m openai

# Skip expensive API tests
pytest -m "not openai and not ollama"
```

### Standalone Testing

See [examples/README.md](examples/README.md) for standalone testing scripts and examples.

## Troubleshooting

### User Issues

See [README.md Troubleshooting Section](README.md#troubleshooting) for common user-facing issues.

### Developer Issues

**Pytest import errors:**
```bash
# Ensure modules are in PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:${PWD}"
pytest tests/
```

**Mock server issues in tests:**
```bash
# Check if ports are available
lsof -i :8000  # Paperless mock server
lsof -i :11434 # Ollama mock server
```

**Coverage not tracking modules:**
```bash
# Install in development mode
pip install -e .
pytest --cov=modules --cov-report=term-missing
```

**Test fixtures not loading:**
```bash
# Verify test fixtures directory
ls -la tests/fixtures/
# Should show settings_*.yaml files
```

## Future Enhancements

Completed:
- [x] Multiple AI provider support (OpenAI, Ollama) ✅ 2024-12-15

Potential improvements:
- [ ] Batch processing for existing documents
- [ ] Custom prompt templates per document type
- [ ] Additional providers (Claude, Gemini, local models)
- [ ] Title quality scoring and validation
- [ ] Automatic language detection
- [ ] Title history and rollback
- [ ] Web UI for configuration
- [ ] Metrics and analytics dashboard

## Contributing

### Development Workflow

1. **Fork and clone** the repository
2. **Create a feature branch**: `git checkout -b feature/your-feature`
3. **Set up development environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt requirements-dev.txt
   ```
4. **Make your changes** and add tests
5. **Run tests**: `pytest tests/`
6. **Check coverage**: `pytest --cov=modules --cov-report=term-missing`
7. **Commit with descriptive message**: `git commit -m "Add: feature description"`
8. **Push and create PR**: `git push origin feature/your-feature`

### Code Standards

- **Python Style**: Follow PEP 8
- **Testing**: Add tests for all new features
- **Coverage**: Maintain >80% test coverage
- **Documentation**: Update README.md and AGENTS.md
- **Commit Messages**: Use conventional commits (Add:, Fix:, Update:, etc.)

### Reporting Issues

When reporting bugs, include:
- Paperless NGX version
- Docker/docker-compose version
- ngx-renamer version/commit
- Error messages from logs
- Steps to reproduce
- Expected vs actual behavior

### Feature Requests

For new features, describe:
- Use case and motivation
- Proposed implementation approach
- Potential impact on existing functionality
- Backward compatibility considerations

## Release History

See [CHANGELOG.md](CHANGELOG.md) for detailed release notes and development history.

### Recent Changes

**2024-12-15: Multi-LLM Provider Support (v1.0.0)**
- Added Ollama provider for local/offline title generation
- Implemented provider factory pattern in PaperlessAITitles
- Created BaseLLMProvider abstract class for shared functionality
- Added comprehensive test suite for multi-provider support
- Updated configuration format with `llm_provider` setting
- Backward compatible with existing OpenAI-only configurations

---

**License**: GPL-3.0
**Version**: 1.4.0
**Documentation**: README.md (users) | AGENTS.md (developers) | ARCHITECTURE.md (architecture)
