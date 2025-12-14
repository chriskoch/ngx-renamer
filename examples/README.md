# Examples

This directory contains standalone example scripts for testing ngx-renamer functionality outside of Paperless NGX.

## Scripts

### test_title.py
Demonstrates title generation from sample text using the OpenAI API.

**Usage**:
```bash
python3 examples/test_title.py
```

**Requirements**:
- Active virtual environment
- OpenAI API key in `.env` file
- `settings.yaml` configuration

### test_pdf.py
Extracts and displays text content from a PDF file using pdfplumber.

**Usage**:
```bash
python3 examples/test_pdf.py path/to/your/file.pdf
```

**Requirements**:
- Active virtual environment
- PDF file path as argument

### test_api.py
Tests the complete integration with Paperless NGX API.

**Usage**:
```bash
python3 examples/test_api.py
```

**Requirements**:
- Running Paperless NGX instance
- Valid API credentials in `.env` file
- At least one document in Paperless

## Setup

1. **Create virtual environment** (if not already done):
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. **Run examples**:
   ```bash
   python3 examples/test_title.py
   ```

## Note

For automated testing, use the comprehensive test suite in the `tests/` directory instead:
```bash
pytest tests/
```
