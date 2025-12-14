# Changelog

All notable changes to ngx-renamer will be documented in this file.

## [Unreleased] - Dev Branch

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

### Statistics
- **Total Changes**: 28 files changed
- **Additions**: +1,292 lines
- **Deletions**: -126 lines
- **Net**: +1,166 lines

## Breaking Changes

### None - Fully Backward Compatible
All changes are backward compatible. Existing installations continue to work with the manual setup method. Users can migrate to the new auto-init method at their convenience.

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

## Credits

Implementation and testing by Claude Code with human oversight.

---

**Note**: This changelog covers changes from the main branch to the dev branch.
For release notes, see individual release tags.
