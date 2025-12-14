# ngx-renamer

AI-powered document title generator for Paperless NGX supporting multiple LLM providers (OpenAI, Ollama).

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-compose-blue.svg)](https://docs.docker.com/compose/)

## Overview

ngx-renamer is a Paperless NGX [post-consumption hook](https://docs.paperless-ngx.com/advanced_usage/#consume-hooks) that automatically generates intelligent, descriptive titles for your documents using AI language models. It supports both cloud-based OpenAI GPT models and local Ollama models for privacy-focused deployments. When Paperless NGX consumes a new document, this script analyzes the OCR-extracted text and creates a meaningful title instead of generic filenames.

**Example transformations**:
- `scan_2024_03_15.pdf` → `Amazon - Monthly Prime Subscription Invoice`
- `IMG_2043.pdf` → `Deutsche Bank - Account Statement March 2024`
- `document.pdf` → `Versicherung - Änderungen AVB DKV 2026`

### Features

✅ **Multiple LLM Providers** - OpenAI (cloud) or Ollama (local/private)
✅ **Zero-Setup Installation** - Automatic venv initialization, no manual commands
✅ **Persistent Configuration** - Survives container restarts and rebuilds
✅ **Smart Title Generation** - Context-aware titles in the document's language
✅ **Configurable Prompts** - Customize title format via YAML settings
✅ **Dual Installation Methods** - Full-featured or ultra-minimal single-file
✅ **Comprehensive Testing** - Full integration test suite for all providers
✅ **Production Ready** - Handles errors, retries, and edge cases

### Requirements

- Paperless NGX running in Docker
- **Either**:
  - OpenAI API account ([Get one here](https://platform.openai.com/signup)), **or**
  - Local Ollama installation ([Install here](https://ollama.ai))
- Paperless NGX API token (from your user profile)

## Table of Contents

- [Installation](#installation-in-paperless-ngx)
  - [Method 1: Auto-Init (Recommended)](#method-1-auto-init-installation-recommended)
  - [Method 2: Standalone Single-File](#method-2-standalone-single-file-installation)
  - [Migration Guide](#migration-from-old-installation-method)
- [Configuration](#the-settings)
- [Troubleshooting](#troubleshooting)
- [Development](#python-development-and-testing)
- [Architecture](#architecture)
- [Contributing](#contributing)
- [License](#license)

## Installation in Paperless NGX

We provide **two installation methods** - choose the one that fits your needs:

1. **Auto-Init Method** (Recommended) - Fully automated, no manual setup
2. **Standalone Single-File** (Simplest) - Ultra-minimal, one file only

---

### Method 1: Auto-Init Installation (Recommended)

This method automatically sets up the Python environment on container start. **No manual commands needed!**

#### Step 1: Copy ngx-renamer to your Paperless directory

```bash
cd ~/paperless  # or wherever your docker-compose.yml is located
git clone <repository-url> ngx-renamer
```

Your directory structure will look like:
```
~/paperless/
├── docker-compose.yml
├── docker-compose.env
├── consume/
├── export/
└── ngx-renamer/        # ← The cloned directory
    ├── change_title.py
    ├── modules/
    ├── scripts/        # ← New helper scripts
    ├── settings.yaml
    └── ...
```

#### Step 2: Configure API credentials

**Option A: Using .env file** (traditional method)
```bash
cd ngx-renamer
cp .env.example .env
nano .env  # Edit with your API keys
```

**Option B: Using docker-compose environment** (recommended for new installations)

Add to your `docker-compose.env` file:
```bash
OPENAI_API_KEY=sk-your-openai-api-key-here
PAPERLESS_NGX_API_KEY=your-paperless-api-token-here
PAPERLESS_NGX_URL=http://webserver:8000/api
```

> **Note:** Get your OpenAI API key from https://platform.openai.com/settings/organization/api-keys
>
> Get your Paperless API token from your Paperless user profile.

#### Step 3: Update docker-compose.yml

Add the following to your `webserver` service:

```yaml
webserver:
  image: ghcr.io/paperless-ngx/paperless-ngx:latest
  restart: unless-stopped
  depends_on:
    - db
    - broker
  ports:
    - "8000:8000"
  volumes:
    # Your existing volumes...
    - ./data:/usr/src/paperless/data
    - ./media:/usr/src/paperless/media
    - ./export:/usr/src/paperless/export
    - ./consume:/usr/src/paperless/consume

    # Add these two lines for ngx-renamer:
    - ./ngx-renamer:/usr/src/ngx-renamer:ro  # Source code (read-only)
    - ngx-renamer-venv:/usr/src/ngx-renamer-venv  # Persistent venv

  env_file: docker-compose.env
  environment:
    PAPERLESS_REDIS: redis://broker:6379
    PAPERLESS_DBHOST: db

    # Add this line to enable ngx-renamer:
    PAPERLESS_POST_CONSUME_SCRIPT: /usr/src/ngx-renamer/scripts/post_consume_wrapper.sh

  # Add this custom entrypoint:
  entrypoint: /usr/src/ngx-renamer/scripts/init-and-start.sh

# Add this at the bottom of your docker-compose.yml:
volumes:
  ngx-renamer-venv:  # Persistent volume for Python dependencies
```

#### Step 4: Restart Paperless

```bash
docker compose down
docker compose up -d
```

**That's it!** The first startup will take 30-60 seconds to initialize the Python environment. Subsequent restarts are instant.

Check the logs to verify:
```bash
docker compose logs webserver | grep ngx-renamer
```

You should see:
```
[ngx-renamer] Initializing Python environment...
[ngx-renamer] Python environment setup complete!
[ngx-renamer] Starting Paperless NGX...
```

---

### Method 2: Standalone Single-File Installation

This is the **simplest possible** installation - just one Python file!

#### Step 1: Copy the standalone script

```bash
cd ~/paperless
wget https://raw.githubusercontent.com/<your-repo>/ngx-renamer/main/ngx-renamer-standalone.py
# Or: curl -O https://...
```

#### Step 2: Update docker-compose.yml

```yaml
webserver:
  image: ghcr.io/paperless-ngx/paperless-ngx:latest
  volumes:
    # Your existing volumes...

    # Add this single line:
    - ./ngx-renamer-standalone.py:/usr/local/bin/ngx-renamer.py:ro

  environment:
    # Add these environment variables:
    PAPERLESS_POST_CONSUME_SCRIPT: python3 /usr/local/bin/ngx-renamer.py
    OPENAI_API_KEY: ${OPENAI_API_KEY}
    PAPERLESS_NGX_URL: http://webserver:8000/api
    PAPERLESS_NGX_API_KEY: ${PAPERLESS_API_KEY}
    OPENAI_MODEL: gpt-4o  # Optional: defaults to gpt-4o-mini
```

#### Step 3: Add credentials to .env

Create or edit your `.env` file in the same directory as `docker-compose.yml`:
```bash
OPENAI_API_KEY=sk-your-key-here
PAPERLESS_API_KEY=your-paperless-token-here
```

#### Step 4: Restart

```bash
docker compose down
docker compose up -d
```

**Done!** No setup, no venv, just one file.

---

### Migration from Old Installation Method

If you previously installed ngx-renamer using the manual `setup_venv.sh` method:

1. **Backup your `.env` file** (if using Method 1) or note your API keys
2. Follow the new installation instructions above
3. Remove the old manual setup:
   ```bash
   rm -rf ngx-renamer/venv  # Old venv no longer needed
   ```
4. The new method uses `/usr/src/ngx-renamer-venv` in a Docker volume instead

Your settings.yaml and configuration will continue to work as-is.

---

### Troubleshooting

#### Issue: "Python environment setup failed"

- **Check logs:** `docker compose logs webserver | grep ngx-renamer`
- **Verify volume:** `docker volume ls | grep ngx-renamer`
- **Manual setup:** `docker compose exec webserver /usr/src/ngx-renamer/scripts/setup-venv-if-needed.sh`

#### Issue: "Failed to get document details" or "Failed to update title"

- **Verify PAPERLESS_NGX_URL:** Must be accessible from inside the container
  - Use `http://webserver:8000/api` (service name with /api), NOT `http://localhost:8000/api`
  - MUST include `/api` at the end
- **Check API key:** Verify your Paperless API token is correct
- **Test connectivity:** `docker compose exec webserver curl http://webserver:8000/api/`

#### Issue: "OPENAI_API_KEY environment variable not set"

- **Method 1 users:** Verify `.env` file exists in `ngx-renamer/` directory
- **Method 2 users:** Check environment variables in `docker-compose.yml`
- **Verify:** `docker compose exec webserver env | grep OPENAI`

#### Issue: Title generation not running after document upload

- **Check post-consume script is set:**
  ```bash
  docker compose exec webserver env | grep PAPERLESS_POST_CONSUME_SCRIPT
  ```
- **Manually trigger:** Upload a test document and check logs
- **Verify script is executable:**
  ```bash
  docker compose exec webserver ls -la /usr/src/ngx-renamer/scripts/
  ```

#### Issue: Dependencies changed but not updating

Method 1 auto-detects requirements.txt changes. To force rebuild:
```bash
docker compose exec webserver rm /usr/src/ngx-renamer-venv/.initialized
docker compose restart webserver
```

#### Issue: Want to update settings.yaml

Method 1: Just edit `settings.yaml` - **no restart needed!** Changes apply to next document.

Method 2: Edit environment variables in docker-compose.yml, then `docker compose up -d`

---

## LLM Provider Configuration

ngx-renamer supports **two LLM providers** for generating document titles:

1. **OpenAI** (default) - Cloud-based, requires API key
2. **Ollama** - Local/self-hosted, free and private

### Choosing Your Provider

Provider selection is configured in `settings.yaml`:

```yaml
# Choose your LLM provider
llm_provider: "openai"  # options: "openai" or "ollama"
```

---

### Option 1: OpenAI (Default)

**Pros:**
- High-quality title generation
- Fast response times
- No local setup required

**Cons:**
- Requires API key and incurs costs
- Data sent to OpenAI servers

**Setup:**

1. Get your API key from https://platform.openai.com/settings/organization/api-keys
2. Configure in `.env`:
   ```bash
   OPENAI_API_KEY=sk-your-openai-api-key-here
   ```
3. Set in `settings.yaml`:
   ```yaml
   llm_provider: "openai"
   openai:
     model: "gpt-4o"  # or "gpt-4o-mini" for lower cost
   ```

---

### Option 2: Ollama (Local/Self-Hosted)

**Pros:**
- Completely free
- Private - data stays on your server
- No API key required
- Works offline

**Cons:**
- Requires local Ollama installation
- Needs sufficient hardware (CPU/GPU)
- May be slower than OpenAI

**Setup:**

#### Step 1: Install Ollama

**On your host machine** (where Docker runs):

- **macOS/Linux:**
  ```bash
  curl -fsSL https://ollama.ai/install.sh | sh
  ```

- **Windows:**
  Download from https://ollama.ai/download

- **Verify installation:**
  ```bash
  ollama --version
  ```

#### Step 2: Pull the Model

```bash
# Pull the gpt-oss model (or any other model you prefer)
ollama pull gpt-oss:latest

# Alternative models:
# ollama pull llama3:latest
# ollama pull mistral:latest
# ollama pull qwen2.5:latest
```

#### Step 3: Start Ollama Server

```bash
# The server usually starts automatically, but you can start it manually:
ollama serve
```

**Verify Ollama is running:**
```bash
curl http://localhost:11434/api/version
```

#### Step 4: Configure ngx-renamer

1. **Update `.env`:**

   For local development:
   ```bash
   OLLAMA_BASE_URL=http://localhost:11434
   ```

   For Docker on Mac/Windows:
   ```bash
   OLLAMA_BASE_URL=http://host.docker.internal:11434
   ```

   For Docker on Linux:
   ```bash
   OLLAMA_BASE_URL=http://172.17.0.1:11434
   ```

2. **Update `settings.yaml`:**
   ```yaml
   llm_provider: "ollama"
   ollama:
     model: "gpt-oss:latest"  # or whichever model you pulled
   ```

3. **Restart Paperless:**
   ```bash
   docker compose restart webserver
   ```

---

### Switching Between Providers

You can easily switch between OpenAI and Ollama:

1. Edit `settings.yaml` and change `llm_provider`
2. **No restart needed** - changes apply to the next document

**Example:**
```yaml
# Switch to Ollama
llm_provider: "ollama"

# Switch back to OpenAI
llm_provider: "openai"
```

---

### Docker Networking for Ollama

When running Paperless in Docker and Ollama on the host, you need the correct URL:

| Platform | OLLAMA_BASE_URL |
|----------|-----------------|
| **macOS** | `http://host.docker.internal:11434` |
| **Windows** | `http://host.docker.internal:11434` |
| **Linux** | `http://172.17.0.1:11434` |
| **Ollama in Docker** | `http://ollama:11434` (if in same docker-compose) |

**Test connectivity from container:**
```bash
docker compose exec webserver curl http://host.docker.internal:11434/api/version
```

---

### Troubleshooting Ollama

#### Issue: "Cannot connect to Ollama"

**Solution:**
1. Check Ollama is running: `curl http://localhost:11434/api/version`
2. Start if needed: `ollama serve`
3. Verify correct OLLAMA_BASE_URL for your platform (see table above)
4. Check Docker networking (try `host.docker.internal` on Mac/Windows)

#### Issue: "Model not found"

**Solution:**
```bash
# Pull the model first
ollama pull gpt-oss:latest

# List available models
ollama list
```

#### Issue: Slow performance

**Solution:**
- Use a smaller model (e.g., `llama3:8b` instead of `llama3:70b`)
- Ensure sufficient RAM/VRAM
- Consider using OpenAI for better speed

#### Issue: Error during title generation

**Check logs:**
```bash
docker compose logs webserver | grep -i ollama
```

**Common fixes:**
- Ensure model is pulled: `ollama list`
- Restart Ollama: `ollama serve`
- Check firewall isn't blocking port 11434

---

## The settings

You may edit `settings.yaml` to edit the prompt and with that the results.

**Test the different models at OpenAI:**
```yaml
openai_model: "gpt-4o-mini" # the model to use for the generation
```
**Decide whether you want to have a date as a prefix:**
```yaml
with_date: true # boolean if the title should the date as a prefix
```
**Play with the prompt - it is a work in progress and tested in Englsh and German:**
```yaml
prompt:
  # the main prompt for the AI
  main: |
    * this is a text from a PDF document generated with OCR
    * begin the text with the following line: ### begin of text ###
    * end the text with the following line: ### end of text ###
    * generate a title for that given text in the corresponding language
    * add the sender or author of the document with a maximum of 20 characters to the  title 
    * remove all stop words from the title
    * the  title must be in a Concise and Informative style
    * remove duplicate information
    * the length must be smaller that 200 characters
    * do not use asterisks in the title
    * do not use currencies in the result
    * optimize it for readability
    * check the result for filename conventions
    * re-read the generated  title and optimize it
  # the prompt part will be appended if the date should be included in the title using with_date: true
  with_date: |
    * analyze the text and find the date of the document
    * add the found date in form YYYY-MM-DD as a prefix to the doument title
    * if there is no date information in the document, use {current_date}
    * use the form: date sender title
  # the prompt part will be appended if the date should not be included in the title using with_date: false
  no_date: |
    * use the form: sender title
  # the prompt before the content of the document will be appended
  pre_content: |
    ### begin of text ###
  # the prompt after the content of the document will be appended
  post_content: |  
    ### end of text ###
```

## Python development and testing

If you want to develop and test is without integrating it in Paperless NGX you can do that.

* Create a virtual environment
* Load all libraries
* Call test scripts
* Enjoy optimizing the prompt in settings.yaml

### Create virtual environment

```bash
# python or python3 is up to your system
$ python3 -m venv .venv
$ source .venv/bin/activate
```

### Load all needed libraries

```bash
(.venv)$ pip install -r requirements.txt
```

### Call test scripts

```bash
# prints the thought title from a american law text
(.venv)$ python3 test_title.py
````

```bash
# read the content from a OCR'ed pdf file
(.venv)$ python3 ./test_pdf.py path/to/your/ocr-ed/pdf/file
```

### Run the test suite

For automated testing with full coverage:

```bash
# Install dev dependencies
(.venv)$ pip install -r requirements-dev.txt

# Run all tests
(.venv)$ pytest tests/

# Run specific test categories
(.venv)$ pytest -m smoke        # Critical smoke tests
(.venv)$ pytest -m integration  # All integration tests
(.venv)$ pytest -m openai       # OpenAI API tests (requires API key, costs money)
(.venv)$ pytest -m ollama       # Ollama API tests (requires Ollama running)

# Test specific providers
(.venv)$ pytest tests/integration/test_openai_integration.py
(.venv)$ pytest tests/integration/test_ollama_integration.py
(.venv)$ pytest tests/integration/test_llm_provider_selection.py

# With coverage report
(.venv)$ pytest --cov=modules --cov-report=html
```

See [examples/README.md](examples/README.md) for standalone testing scripts.

---

## Architecture

For detailed information about the system architecture, components, data flow, and security considerations, see [AGENTS.md](AGENTS.md).

**Key Components**:
- **Entry Point**: `scripts/init-and-start.sh` - Container initialization
- **Setup**: `scripts/setup-venv-if-needed.sh` - Automatic venv management
- **Wrapper**: `scripts/post_consume_wrapper.sh` - Post-consume hook
- **Orchestrator**: `change_title.py` - Main workflow coordinator
- **Paperless Agent**: `modules/paperless_ai_titles.py` - API integration & provider selection
- **LLM Providers**:
  - `modules/openai_titles.py` - OpenAI integration
  - `modules/ollama_titles.py` - Ollama integration
  - `modules/base_llm_provider.py` - Shared base class

**Data Flow**:
```
Document Upload → Paperless OCR → Post-Consume Hook →
ngx-renamer → Paperless API (fetch) →
Provider Selection (OpenAI or Ollama) → LLM API (generate) →
Paperless API (update) → Document with AI Title
```

---

## Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

### Development Setup

1. Clone the repository
2. Create a virtual environment: `python3 -m venv .venv`
3. Install dependencies: `pip install -r requirements.txt requirements-dev.txt`
4. Run tests: `pytest tests/`

### Reporting Issues

When reporting issues, please include:
- Paperless NGX version
- Docker/docker-compose version
- Error messages from logs
- Steps to reproduce

### Recent Changes

See [CHANGELOG.md](CHANGELOG.md) for recent changes and development history.

---

## License

MIT License - see LICENSE file for details.

---

## Acknowledgments

- Built for [Paperless NGX](https://github.com/paperless-ngx/paperless-ngx)
- LLM Support: [OpenAI](https://openai.com/) and [Ollama](https://ollama.ai)
- Developed with [Claude Code](https://claude.com/claude-code)

---

**Questions or Issues?** 
- Check the [Troubleshooting](#troubleshooting) section
- Review [AGENTS.md](AGENTS.md) for architecture details
- Open an issue on GitHub
