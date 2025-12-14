# ngx-renamer Architecture

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

## Troubleshooting

See [README.md Troubleshooting Section](README.md#troubleshooting) for common issues and solutions.

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

See [CHANGELOG.md](CHANGELOG.md) for recent changes and development history.

---

**Last Updated**: 2024-12-15
**Version**: Dev Branch (Multi-LLM Support)
**Maintained by**: Claude Code with human oversight

## Recent Changes

### 2024-12-15: Multi-LLM Provider Support
- Added Ollama provider for local/offline title generation
- Implemented provider factory pattern in PaperlessAITitles
- Created BaseLLMProvider abstract class for shared functionality
- Added comprehensive test suite for multi-provider support
- Updated configuration format with `llm_provider` setting
- Backward compatible with existing OpenAI-only configurations
