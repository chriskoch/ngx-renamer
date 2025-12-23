# Changelog

All notable changes to ngx-renamer will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.4.0] - 2024-12-23

### Added
- **Anthropic Claude API Support**: Third LLM provider option alongside OpenAI and Ollama
  - New `ClaudeTitles` provider in `modules/claude_titles.py`
  - Uses Claude's tool calling feature for structured JSON outputs
  - Supports same configuration pattern as existing providers
  - Default model: `claude-sonnet-4-5-20250929` (Claude Sonnet 4.5)
  - Activated via `llm_provider: "claude"` in `settings.yaml`
  - Requires `CLAUDE_API_KEY` environment variable

- **Extended Test Coverage**: Comprehensive Claude integration tests
  - `tests/integration/test_claude_integration.py` - Full API integration tests
  - Provider selection tests for Claude in `test_llm_provider_selection.py`
  - Test fixtures: `settings_claude.yaml`, `settings_claude_with_date.yaml`
  - Added `@pytest.mark.claude` marker for expensive API tests

### Changed
- **Provider Factory Enhancement**: Extended to support Claude credentials
  - `modules/llm_factory.py` - Added `_create_claude_provider()` method
  - `modules/paperless_ai_titles.py` - Accept `claude_api_key` parameter
  - `change_title.py` - Load `CLAUDE_API_KEY` from environment
  - `modules/constants.py` - Added `PROVIDER_CLAUDE` constant and validation

- **Claude Model Update**: Migrated to latest stable model
  - Updated from deprecated Claude 3.5 Sonnet (`claude-3-5-sonnet-20241022`) to Claude Sonnet 4.5 (`claude-sonnet-4-5-20250929`)
  - Claude 3.5 Sonnet will be retired October 28, 2025
  - Updated all configuration files, test fixtures, and documentation
  - All tests passing with new model (10/10 Claude tests)

- **Dependency Updates**:
  - Added `anthropic>=0.39.0` to `requirements.txt`

### Removed
- **Code Cleanup**: Removed unused code and technical debt
  - Removed 3 unused exception classes: `SettingsError`, `LLMProviderError`, `TitleGenerationError`
  - Removed unused `PROVIDER_GROK` constants (future placeholder not actively developed)
  - Fixed trailing whitespace in `ollama_titles.py` and `openai_titles.py`
  - Simplified `exceptions.py` from 5 classes to 2 (kept only used exceptions)
  - Net code reduction: -18 lines (-7% overall)

### Documentation
- Plugin architecture successfully validated with third provider
- Adding new provider now requires ~100 lines vs ~200 with old architecture
- Updated all Claude model references to Sonnet 4.5
- Updated configuration examples in README.md, settings.yaml, and .env.example

## [1.3.0] - 2024-12-23

### Added
- **Centralized Logging Infrastructure**: Professional logging across all modules
  - New `modules/logger.py` with formatted console output
  - Replaced all `print()` statements with proper logging
  - Structured log messages with timestamps and log levels

- **Constants Module**: Eliminated magic numbers and duplicate schemas
  - New `modules/constants.py` with all constants and schemas
  - `TITLE_SCHEMA` defined once, imported everywhere
  - Provider names, default models, config keys centralized

- **Custom Exception Hierarchy**: Better error handling and debugging
  - New `modules/exceptions.py` with specific exception types
  - `NGXRenamerError`, `SettingsError`, `LLMProviderError`, `PaperlessAPIError`

- **Plugin Architecture**: Provider registry pattern for easy extensibility
  - New `modules/providers/__init__.py` with provider registry
  - Auto-registration of providers via `register_provider()`
  - Factory pattern in `modules/llm_factory.py`
  - New `modules/paperless_client.py` for API operations

### Changed
- **Code Quality Improvements**: Major OOP best practices refactoring
  - Moved `_parse_structured_response()` to `BaseLLMProvider` (eliminated 40+ duplicate lines)
  - Fixed name mangling misuse: `__method` → `_method` (PEP 8 compliance)
  - Added 100% type hint coverage (PEP 484)
  - Separated concerns: Factory, Client, Orchestrator (SOLID principles)

- **Provider Implementations**: Refactored for shared functionality
  - `modules/openai_titles.py` - Removed duplicated code, added type hints
  - `modules/ollama_titles.py` - Removed duplicated code, added type hints
  - `modules/paperless_ai_titles.py` - Refactored to use composition
  - All providers now inherit shared parsing, logging, and prompt building

### Removed
- Deleted outdated `ngx-renamer-standalone.py` script

### Documentation
- Updated `AGENTS.md` with v1.3.0 architecture details
- Documented plugin architecture and provider pattern
- Added examples for adding new providers
- Code quality score: 6.3/10 → 9.0/10

## [1.2.3] - 2024-12-23

### Added
- **Documentation Automation System**: Automated version synchronization across documentation
  - Enhanced `.bumpversion.cfg` to auto-update AGENTS.md and ARCHITECTURE.md
  - Created `scripts/update-docs-version.sh` for manual version synchronization
  - Added GitHub Actions CI workflow for documentation validation
  - Comprehensive automation guide in `.github/AUTOMATION.md`
  - See [AUTOMATION.md](.github/AUTOMATION.md) for details

- **Community Standards Documentation**: Professional contributor and security guidelines
  - `CONTRIBUTING.md` (500 lines): Complete contributor guide with Code of Conduct
  - `SECURITY.md` (316 lines): Security policy and vulnerability reporting process
  - Development workflow and coding standards documented
  - Testing requirements and PR guidelines clearly defined

### Changed
- **Documentation Updates**: Synchronized all documentation to v1.2.2
  - Updated AGENTS.md version footer (1.1.0 → 1.2.2)
  - Updated ARCHITECTURE.md version footer (1.1.0 → 1.2.2)
  - Documented structured outputs feature (v1.2.0) in AGENTS.md
  - Documented Ollama API key authentication (v1.2.2) in AGENTS.md
  - Added JSON schema validation to tech stack description
  - Enhanced testing requirements with structured output validation

### Fixed
- Fixed repository URL placeholder in README.md
- Removed outdated RELEASE_NOTES.md file

### Documentation
- Updated RELEASING.md with automated version update procedures
- Added comprehensive automation troubleshooting guide
- Documented security best practices for API key handling
- Added pre-deployment security checklist

## [1.2.2] - 2024-12-22

### Added
- **Ollama API Key Authentication**: Support for authenticated Ollama instances
  - Added optional `OLLAMA_API_KEY` environment variable
  - Ollama provider now supports Bearer token authentication via `Authorization` header
  - Works seamlessly with both authenticated and non-authenticated Ollama instances
  - Empty or whitespace-only API keys are treated as no authentication (backward compatible)
  - Comprehensive test suite with 15 tests covering all API key scenarios
  - See [PR #6](https://github.com/chriskoch/ngx-renamer/pull/6) for details

### Changed
- **Ollama Client Initialization**: Enhanced to conditionally set Authorization header
  - Only sets `Authorization: Bearer {api_key}` header when valid API key is provided
  - Maintains full backward compatibility with existing local Ollama setups

### Testing
- **New Test Suite**: `tests/integration/test_ollama_api_key.py`
  - 8 unit tests for API key initialization and header setting
  - 2 tests for PaperlessAITitles API key passing
  - 5 integration tests for real API calls with/without API key
  - All tests pass with proper mocking and real Ollama integration

### Acknowledgments
- **Special Thanks**: A huge thank you to [@kkettinger](https://github.com/kkettinger) (Kevin Kettinger) for contributing the Ollama API key authentication feature! This enhancement enables ngx-renamer to work with authenticated Ollama instances and cloud-hosted Ollama services. Your contribution is greatly appreciated! 🙏

## [1.2.1] - 2025-12-16

### Fixed
- **License Alignment**: Corrected all documentation to reflect GPL-3.0 license
  - Updated README.md badge from MIT to GPL-3.0
  - Updated license references in AGENTS.md, ARCHITECTURE.md, RELEASE_NOTES.md
  - All documentation now consistent with LICENSE file (GPL-3.0)

## [1.2.0] - 2025-12-16

### Added
- **Structured Outputs for All LLM Providers**: Implemented JSON schema-based structured outputs
  - Ollama provider now uses `format` parameter with JSON schema
  - OpenAI provider now uses `response_format` with json_schema
  - Ensures reliable title extraction without prompt engineering
  - Auto-truncates titles exceeding 127 characters for Paperless NGX compatibility
  - Comprehensive error handling for malformed JSON responses
  - 28 new unit tests covering JSON parsing, truncation, and edge cases
  - Cross-provider consistency tests ensure identical behavior
- **Testing Guide**: Created TESTING_STRUCTURED_OUTPUTS.md
  - Comprehensive guide for verifying structured outputs work correctly
  - Troubleshooting steps for common issues
  - Alternative format approaches for Ollama if needed
  - Manual testing procedures for both providers

### Changed
- **Improved Response Parsing**: Both providers now parse structured JSON responses
  - Ollama: Added `_parse_structured_response()` method
  - OpenAI: Added `_parse_structured_response()` method
  - Consistent error messages guide users when models don't support structured outputs

### Fixed
- **JSON Schema maxLength**: Corrected from 128 to 127 characters
  - Now matches Paperless NGX's actual title limit
  - Prevents models from generating titles that get truncated post-generation
  - Schema properly constrains models to the real limit

### Removed
- **Simplified Prompts**: Removed redundant "Output only the title text, nothing else" instruction
  - JSON schema now enforces output format automatically
  - Cleaner, more focused prompts

## [1.1.0] - 2024-12-15

### Changed
- **Documentation Restructure**: Complete documentation overhaul for clarity
  - Shortened README.md from 680 to 260 lines (62% reduction)
  - Created AGENTS.md following official agents.md specification
  - Renamed old AGENTS.md to ARCHITECTURE.md for detailed technical docs
  - Removed all AI tool advertisements from documentation
  - Clear separation: README (users) | AGENTS.md (AI agents) | ARCHITECTURE.md (developers)

### Added
- **AGENTS.md**: New file following [agents.md](https://agents.md/) specification
  - Clear persona and role for AI coding agents
  - Exact commands for development, testing, deployment
  - Code style examples and naming conventions
  - Three-tier boundaries (Always/Ask/Never)
  - Prevents AI tools from adding advertisements or co-author credits

- **ARCHITECTURE.md**: Renamed from AGENTS.md with expanded content
  - Detailed system architecture and data flow
  - Component documentation
  - Advanced LLM provider configuration
  - Model performance comparisons
  - Docker networking details
  - Development setup and testing guide

## [1.0.0] - 2024-12-15

### Added

#### Multi-LLM Provider Support (2024-12-15)
- **Ollama Integration**: Full support for local Ollama models
  - Privacy-focused: all processing stays on your server
  - Cost-free: no API charges for local models
  - Offline capable: works without internet connection
  - Support for various open-source models (gpt-oss, llama3, mistral, etc.)

- **Provider Architecture**:
  - Factory pattern in `PaperlessAITitles` for dynamic provider selection
  - `BaseLLMProvider` abstract class for shared functionality
  - `OllamaTitles` provider class for Ollama API integration
  - Unified configuration format with `llm_provider` setting
  - Backward compatible with existing OpenAI-only configurations

- **Comprehensive Test Suite** (17 new tests):
  - `test_ollama_integration.py`: 8 tests for Ollama provider
    - Title generation from various document types
    - Settings loading and validation
    - Date prefix functionality
    - Error handling (service unavailable, model not found)
    - Empty text edge cases
  - `test_llm_provider_selection.py`: 9 tests for multi-provider logic
    - Provider factory pattern verification
    - Missing credentials error handling
    - Invalid provider detection
    - Backward compatibility testing
    - Runtime provider switching
    - Multi-provider comparison tests

- **Test Infrastructure**:
  - 4 new test fixture files for provider configurations
  - Extended `conftest.py` with Ollama fixtures and helpers
  - Added `ollama` pytest marker for Ollama-specific tests
  - Updated `pytest.ini` with marker documentation

- **Documentation**:
  - Updated README.md with Ollama setup instructions
  - Complete AGENTS.md architecture update with multi-LLM diagrams
  - Provider selection flow documentation
  - Docker networking guide for Ollama
  - Troubleshooting section for Ollama connectivity

- **Configuration Flexibility**:
  - Simple provider switching via `llm_provider` setting in settings.yaml
  - Provider-specific configuration sections (openai.model, ollama.model)
  - Shared prompt templates across all providers
  - Environment variable support for both providers

### Added

#### Convenient Docker Installation Methods
- **Auto-Init Method (Recommended)**: Fully automated installation with zero manual setup
  - Automatic Python virtual environment initialization on container start
  - Persistent venv in Docker volume (survives container restarts)
  - Auto-detects dependency changes and rebuilds automatically
  - Custom entrypoint wrapper (`scripts/init-and-start.sh`)
  - Conditional venv setup script (`scripts/setup-venv-if-needed.sh`)
  - Post-consume wrapper script (`scripts/post_consume_wrapper.sh`)

- **Standalone Single-File Method**: Ultra-minimal installation alternative
  - All-in-one Python script (`ngx-renamer-standalone.py`)
  - No virtual environment needed
  - Configuration via environment variables only
  - Perfect for beginners and simple setups

#### Documentation & Configuration
- Comprehensive `.env.example` template with detailed instructions
- Two configuration methods supported:
  - Method A: Using `.env` file (traditional)
  - Method B: Using docker-compose environment variables (recommended)
- Complete README rewrite with:
  - Step-by-step installation instructions for both methods
  - Migration guide from old manual setup
  - Comprehensive troubleshooting section
  - Docker-compose.yml examples

#### Testing Infrastructure
- Complete pytest test suite with fixtures
- Integration tests for:
  - End-to-end document processing
  - OpenAI API integration
  - Paperless API integration
- Test configuration:
  - `pytest.ini` with markers (integration, openai, smoke, slow)
  - `requirements-dev.txt` for development dependencies
  - Test fixtures for various settings configurations
- Code coverage reporting with pytest-cov

### Fixed

#### Critical Fixes
- **API URL Configuration Error** (Commit: 8cdf3fb)
  - Fixed incorrect guidance about PAPERLESS_NGX_URL
  - URL must include `/api` at the end (e.g., `http://webserver:8000/api`)
  - Updated all documentation and examples
  - Fixes 401 Unauthorized errors when accessing Paperless API

- **Virtual Environment Initialization** (Commit: 7124bd6)
  - Fixed boot loop caused by Docker volume mount behavior
  - Changed check from directory existence to `activate` file existence
  - Prevents container restart loops when venv is incomplete
  - Docker creates volume mount point as empty directory, causing false detection

- **Docker Internal Networking** (Commit: 8cdf3fb)
  - Changed from `http://localhost:8000` to `http://webserver:8000`
  - Fixed connectivity issues within Docker container network
  - Service name must be used instead of localhost for internal communication

### Changed

#### Installation Process
- **Before**: Required 8+ manual steps including:
  - `sudo chown -R root ngx-renamer/`
  - `sudo chmod +x` on scripts
  - `docker compose exec webserver /usr/src/ngx-renamer/setup_venv.sh`
  - Re-run setup after every container rebuild

- **After**: Just 3 steps:
  - Clone/copy ngx-renamer
  - Configure API keys
  - `docker compose up -d`
  - Everything else is automatic!

#### Configuration
- Enhanced environment variable fallback in `change_title.py`
  - Supports both `.env` file and direct environment variables
  - Better error messages for missing configuration
  - Backward compatible with existing setups

#### Optimizations
- Settings.yaml changes no longer require container restart
- Upgraded default model from `gpt-4o-mini` to `gpt-4o` for better quality
- Streamlined prompt structure for more consistent results

### Maintenance

- Updated `.gitignore` to exclude:
  - `.claude/` directory
  - `.coverage` files
  - Development workspace files
- Improved logging output with `[ngx-renamer]` prefix
- Better error messages and troubleshooting guidance

## File Changes Summary

### New Files (9)
- `scripts/init-and-start.sh` - Entrypoint wrapper for auto-initialization
- `scripts/setup-venv-if-needed.sh` - Conditional venv setup
- `scripts/post_consume_wrapper.sh` - Updated post-consume script
- `ngx-renamer-standalone.py` - Single-file alternative (231 lines)
- `.env.example` - Configuration template
- `pytest.ini` - Test configuration
- `requirements-dev.txt` - Development dependencies
- `tests/` - Complete test suite (8 files, 603 lines)

### Modified Files (8)
- `README.md` - Complete rewrite (+176 lines)
- `change_title.py` - Environment variable fallback (+9 lines)
- `settings.yaml` - Optimized prompt structure
- `.gitignore` - Additional exclusions
- `modules/openai_titles.py` - Minor improvements
- `requirements.txt` - Updated dependencies
- `docker-compose.yml` - Example configuration (not committed)

### Statistics (Multi-LLM Update)
- **New Test Files**: 2 files, 17 tests, 100% passing
- **New Fixtures**: 4 YAML configuration files
- **Modified Files**: 4 (AGENTS.md, README.md, pytest.ini, conftest.py)
- **Test Coverage**: OpenAI (6/6), Ollama (8/8), Multi-provider (9/9)
- **Lines Added**: ~800 lines (tests + documentation)

### Previous Statistics
- **Total Changes**: 28 files changed
- **Additions**: +1,292 lines
- **Deletions**: -126 lines
- **Net**: +1,166 lines

## Breaking Changes

### None - Fully Backward Compatible
All changes are backward compatible:
- Multi-LLM support defaults to OpenAI if `llm_provider` is not specified
- Existing OpenAI configurations continue to work without modification
- Legacy `openai_model` setting still supported (deprecated but functional)
- Existing installations continue to work with the manual setup method
- Users can migrate to the new auto-init method at their convenience

## Migration Guide

### From Old Manual Setup to Auto-Init Method

1. **Backup your configuration**:
   - Save your `.env` file (if using)
   - Note your API keys

2. **Update docker-compose.yml**:
   ```yaml
   volumes:
     - ./ngx-renamer:/usr/src/ngx-renamer:ro
     - ngx-renamer-venv:/usr/src/ngx-renamer-venv
   environment:
     PAPERLESS_POST_CONSUME_SCRIPT: /usr/src/ngx-renamer/scripts/post_consume_wrapper.sh
   entrypoint: /usr/src/ngx-renamer/scripts/init-and-start.sh

   volumes:
     ngx-renamer-venv:
   ```

3. **Clean up old venv**:
   ```bash
   rm -rf ngx-renamer/venv  # Old venv no longer needed
   ```

4. **Restart**:
   ```bash
   docker compose down
   docker compose up -d
   ```

The new method uses `/usr/src/ngx-renamer-venv` in a Docker volume instead of the local directory.

## Troubleshooting

See the comprehensive [Troubleshooting section in README.md](README.md#troubleshooting) for solutions to common issues:

- Python environment setup failed
- Failed to get document details (401 errors)
- OPENAI_API_KEY not set
- Title generation not running
- Dependencies not updating
- Settings.yaml changes not applying

---

[Unreleased]: https://github.com/chriskoch/ngx-renamer/compare/v1.4.0...HEAD
[1.4.0]: https://github.com/chriskoch/ngx-renamer/compare/v1.3.0...v1.4.0
[1.3.0]: https://github.com/chriskoch/ngx-renamer/compare/v1.2.3...v1.3.0
[1.2.3]: https://github.com/chriskoch/ngx-renamer/compare/v1.2.2...v1.2.3
[1.2.2]: https://github.com/chriskoch/ngx-renamer/compare/v1.2.1...v1.2.2
[1.2.1]: https://github.com/chriskoch/ngx-renamer/compare/v1.2.0...v1.2.1
[1.2.0]: https://github.com/chriskoch/ngx-renamer/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/chriskoch/ngx-renamer/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/chriskoch/ngx-renamer/releases/tag/v1.0.0
