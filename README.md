# ngx-renamer

AI-powered document title generator for Paperless NGX supporting OpenAI and Ollama.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## Overview

ngx-renamer automatically generates intelligent titles for your Paperless NGX documents using AI. When you upload a document, it analyzes the OCR text and creates a meaningful title instead of generic filenames like `scan_001.pdf`.

**Example transformations**:
- `scan_2024_03_15.pdf` → `Amazon - Monthly Prime Subscription Invoice`
- `IMG_2043.pdf` → `Deutsche Bank - Account Statement March 2024`
- `document.pdf` → `Versicherung - Änderungen AVB DKV 2026`

### Features

- **Multiple LLM Providers** - OpenAI (cloud) or Ollama (local/private)
- **Zero-Setup Installation** - Automatic initialization, no manual setup
- **Smart Title Generation** - Context-aware titles in the document's language
- **Configurable Prompts** - Customize via YAML settings
- **Production Ready** - Handles errors gracefully

### Requirements

- Paperless NGX in Docker
- **Choose one**:
  - OpenAI API key ([Get one](https://platform.openai.com/signup)) or
  - Local Ollama ([Install](https://ollama.ai))
- Paperless API token (from your user profile)

## Table of Contents

- [Quick Start](#quick-start)
- [LLM Provider Setup](#llm-provider-setup) - OpenAI or Ollama
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Development & Architecture](#development--architecture) - See [ARCHITECTURE.md](ARCHITECTURE.md)

## Quick Start

Choose your installation method:

### Method 1: Auto-Init (Recommended)

Fully automated setup with persistent configuration.

**1. Clone the repository**
```bash
cd ~/paperless  # Your docker-compose.yml location
git clone <repository-url> ngx-renamer
```

**2. Configure credentials**

Add to your `docker-compose.env`:
```bash
PAPERLESS_NGX_API_KEY=your-paperless-api-token
PAPERLESS_NGX_URL=http://webserver:8000/api
# For OpenAI:
OPENAI_API_KEY=sk-your-key-here
# OR for Ollama:
OLLAMA_BASE_URL=http://host.docker.internal:11434
```

**3. Update docker-compose.yml**

Add to your `webserver` service:
```yaml
webserver:
  volumes:
    - ./ngx-renamer:/usr/src/ngx-renamer:ro
    - ngx-renamer-venv:/usr/src/ngx-renamer-venv
  environment:
    PAPERLESS_POST_CONSUME_SCRIPT: /usr/src/ngx-renamer/scripts/post_consume_wrapper.sh
  entrypoint: /usr/src/ngx-renamer/scripts/init-and-start.sh

volumes:
  ngx-renamer-venv:
```

**4. Restart**
```bash
docker compose down && docker compose up -d
```

First startup takes 30-60 seconds. Check logs: `docker compose logs webserver | grep ngx-renamer`

---

### Method 2: Single-File Installation

Minimal setup - one file only.

**1. Download the standalone script**
```bash
cd ~/paperless
wget https://raw.githubusercontent.com/<repo>/ngx-renamer/main/ngx-renamer-standalone.py
```

**2. Update docker-compose.yml**
```yaml
webserver:
  volumes:
    - ./ngx-renamer-standalone.py:/usr/local/bin/ngx-renamer.py:ro
  environment:
    PAPERLESS_POST_CONSUME_SCRIPT: python3 /usr/local/bin/ngx-renamer.py
    OPENAI_API_KEY: ${OPENAI_API_KEY}
    PAPERLESS_NGX_URL: http://webserver:8000/api
    PAPERLESS_NGX_API_KEY: ${PAPERLESS_API_KEY}
```

**3. Add credentials to .env**
```bash
OPENAI_API_KEY=sk-your-key-here
PAPERLESS_API_KEY=your-token-here
```

**4. Restart**
```bash
docker compose down && docker compose up -d
```

## LLM Provider Setup

Choose between **OpenAI** (cloud) or **Ollama** (local/private).

### OpenAI Setup

**Quick setup for cloud-based AI:**

1. Get API key: https://platform.openai.com/settings/organization/api-keys
2. Add to `docker-compose.env`:
   ```bash
   OPENAI_API_KEY=sk-your-key-here
   ```
3. Edit `settings.yaml`:
   ```yaml
   llm_provider: "openai"
   openai:
     model: "gpt-4o-mini"  # or "gpt-4o" for better quality
   ```

### Ollama Setup

**For local/private AI (free, no API costs):**

1. Install Ollama on your host:
   ```bash
   # macOS/Linux
   curl -fsSL https://ollama.ai/install.sh | sh
   # Windows: Download from https://ollama.ai/download
   ```

2. Pull a model:
   ```bash
   ollama pull gpt-oss:latest
   # Or: llama3, mistral, qwen2.5
   ```

3. Configure ngx-renamer in `docker-compose.env`:
   ```bash
   # Mac/Windows:
   OLLAMA_BASE_URL=http://host.docker.internal:11434
   # Linux:
   OLLAMA_BASE_URL=http://172.17.0.1:11434
   ```

4. Edit `settings.yaml`:
   ```yaml
   llm_provider: "ollama"
   ollama:
     model: "gpt-oss:latest"
   ```

**Switch providers anytime** by editing `llm_provider` in `settings.yaml` - no restart needed!

## Configuration

Edit `settings.yaml` to customize title generation.

### Key Settings

**Choose model:**
```yaml
llm_provider: "openai"  # or "ollama"
openai:
  model: "gpt-4o-mini"  # or "gpt-4o" for better quality
ollama:
  model: "gpt-oss:latest"
```

**Date prefix:**
```yaml
with_date: false  # Set true to add YYYY-MM-DD prefix
```

**Customize prompt:**
```yaml
prompt:
  main: |
    * generate a title for the given OCR text in its original language
    * add sender/author (max 20 chars)
    * format: Sender - Brief Description
    * max 127 characters total
    * no asterisks or currencies
  with_date: |
    * find document date and add as YYYY-MM-DD prefix
  no_date: |
    * use format: sender title
```

See [settings.yaml](settings.yaml) for full configuration options.

## Troubleshooting

### Common Issues

**"Failed to get document details"**
- Verify `PAPERLESS_NGX_URL` uses `http://webserver:8000/api` (not `localhost`, must end with `/api`)
- Check API token is correct
- Test: `docker compose exec webserver curl http://webserver:8000/api/`

**"OPENAI_API_KEY not set"**
- Verify `.env` file or docker-compose environment variables
- Check: `docker compose exec webserver env | grep OPENAI`

**"Cannot connect to Ollama"**
- Ensure Ollama is running: `curl http://localhost:11434/api/version`
- Check `OLLAMA_BASE_URL` is correct for your platform (Mac/Windows: `host.docker.internal`, Linux: `172.17.0.1`)
- Verify model is pulled: `ollama list`

**Title generation not running**
- Check logs: `docker compose logs webserver | grep ngx-renamer`
- Verify `PAPERLESS_POST_CONSUME_SCRIPT` is set
- Upload a test document and watch logs

**Force rebuild after updates**
```bash
docker compose exec webserver rm /usr/src/ngx-renamer-venv/.initialized
docker compose restart webserver
```

## Development & Architecture

**For AI Coding Agents**: See [AGENTS.md](AGENTS.md) for development commands, testing, and code conventions.

**For Human Developers**: See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed architecture documentation.

**Quick links:**
- System architecture and data flow → [ARCHITECTURE.md](ARCHITECTURE.md)
- Development setup and testing → [AGENTS.md](AGENTS.md)
- Component documentation → [ARCHITECTURE.md](ARCHITECTURE.md)
- Security considerations → [ARCHITECTURE.md](ARCHITECTURE.md)

## License

MIT License - see LICENSE file for details.
