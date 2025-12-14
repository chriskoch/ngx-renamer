"""
Shared pytest fixtures for ngx-renamer tests.

This module provides:
- Settings file fixtures (valid, invalid, with_date variations)
- Mock Paperless API responses
- Sample document text
- Environment variable management
- OpenAI client fixtures
"""

import os
import pytest
import yaml
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


# ============================================================================
# PATH FIXTURES
# ============================================================================

@pytest.fixture
def fixtures_dir():
    """Return path to test fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def project_root():
    """Return path to project root directory."""
    return Path(__file__).parent.parent


# ============================================================================
# SETTINGS FILE FIXTURES
# ============================================================================

@pytest.fixture
def settings_valid_path(fixtures_dir):
    """Path to valid settings.yaml fixture."""
    return fixtures_dir / "settings_valid.yaml"


@pytest.fixture
def settings_with_date_path(fixtures_dir):
    """Path to settings with date=true fixture."""
    return fixtures_dir / "settings_with_date.yaml"


@pytest.fixture
def settings_minimal_path(fixtures_dir):
    """Path to minimal valid settings fixture."""
    return fixtures_dir / "settings_minimal.yaml"


@pytest.fixture
def settings_invalid_path(fixtures_dir):
    """Path to invalid settings fixture."""
    return fixtures_dir / "settings_invalid.yaml"


@pytest.fixture
def settings_ollama_path(fixtures_dir):
    """Path to Ollama provider settings fixture."""
    return fixtures_dir / "settings_ollama.yaml"


@pytest.fixture
def settings_ollama_with_date_path(fixtures_dir):
    """Path to Ollama settings with date=true fixture."""
    return fixtures_dir / "settings_ollama_with_date.yaml"


@pytest.fixture
def settings_openai_new_format_path(fixtures_dir):
    """Path to OpenAI settings using new llm_provider format."""
    return fixtures_dir / "settings_openai_new_format.yaml"


@pytest.fixture
def settings_invalid_provider_path(fixtures_dir):
    """Path to settings with invalid provider."""
    return fixtures_dir / "settings_invalid_provider.yaml"


@pytest.fixture
def settings_valid(settings_valid_path):
    """Load and return valid settings as dict."""
    with open(settings_valid_path, 'r') as f:
        return yaml.safe_load(f)


# ============================================================================
# API KEY FIXTURES
# ============================================================================

@pytest.fixture
def openai_api_key():
    """
    Get OpenAI API key from environment.

    Tests marked with @pytest.mark.openai will skip if key is not set.
    """
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        pytest.skip("OPENAI_API_KEY not set - skipping OpenAI integration test")
    return key


@pytest.fixture
def ollama_base_url():
    """
    Get Ollama base URL from environment.

    Tests marked with @pytest.mark.ollama will skip if URL is not set.
    Defaults to http://localhost:11434 if not specified.
    """
    url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    # Note: We don't skip here, we'll let individual tests verify if Ollama is actually running
    return url


@pytest.fixture
def paperless_api_key():
    """Mock Paperless API key for testing."""
    return "test-paperless-api-key-12345"


@pytest.fixture
def paperless_url():
    """Mock Paperless URL for testing."""
    return "http://localhost:8000/api"


# ============================================================================
# SAMPLE DOCUMENT FIXTURES
# ============================================================================

@pytest.fixture
def sample_invoice_text():
    """Sample invoice document text."""
    return """
INVOICE #12345
Date: 2024-01-15

Amazon Web Services, Inc.
410 Terry Avenue North
Seattle, WA 98109

Bill To:
John Doe
123 Main Street

Description                           Amount
------------------------------------------------
AWS Monthly Subscription              $125.00
Additional Storage                     $25.00
------------------------------------------------
Total Due:                            $150.00

Payment due by: February 15, 2024
"""


@pytest.fixture
def sample_legal_text():
    """Sample legal document text (from test_title.py)."""
    return """
Each of these had some immediate appeal to me. The responses from our
distinguished panel of commentators have placed them in the proper
perspective.

I start the discussion with reason number 10, that almost no one
understood the ULTA. I have taught the UCC courses in Sales and Sales
Financing. In many law schools, Sales and Sales Financing are two separate
courses, each getting three credit hours. That means each course meets a
minimum of three hours per week over a fourteen-week semester for a total
of eighty-four class hours.
"""


@pytest.fixture
def sample_empty_text():
    """Empty document text for edge case testing."""
    return ""


@pytest.fixture
def sample_long_text():
    """Very long document text for testing token limits."""
    return "Lorem ipsum dolor sit amet. " * 1000  # ~5000 words


# ============================================================================
# PAPERLESS API MOCK FIXTURES
# ============================================================================

@pytest.fixture
def mock_paperless_document_response():
    """Mock successful Paperless document GET response."""
    return {
        "id": 123,
        "title": "Untitled Document",
        "content": "Sample document content for testing.",
        "created": "2024-01-15T10:30:00Z",
        "modified": "2024-01-15T10:30:00Z",
        "correspondent": 5,
        "document_type": 2,
        "tags": [1, 3, 7]
    }


@pytest.fixture
def mock_paperless_update_response():
    """Mock successful Paperless document PATCH response."""
    return {
        "id": 123,
        "title": "Amazon - Monthly Subscription Invoice",  # Updated title
        "content": "Sample document content for testing.",
        "created": "2024-01-15T10:30:00Z",
        "modified": "2024-01-15T10:35:00Z",
        "correspondent": 5,
        "document_type": 2,
        "tags": [1, 3, 7]
    }


# ============================================================================
# HELPER FIXTURES
# ============================================================================

@pytest.fixture
def env_vars(openai_api_key, paperless_api_key, paperless_url):
    """
    Set up environment variables for tests.

    Returns dict of environment variables that were set.
    """
    env = {
        "OPENAI_API_KEY": openai_api_key,
        "PAPERLESS_NGX_API_KEY": paperless_api_key,
        "PAPERLESS_NGX_URL": paperless_url,
    }

    # Store original values
    original = {}
    for key, value in env.items():
        original[key] = os.environ.get(key)
        os.environ[key] = value

    yield env

    # Restore original values
    for key, value in original.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value


@pytest.fixture
def temp_settings_file(tmp_path, settings_valid):
    """Create a temporary settings file for testing."""
    settings_file = tmp_path / "settings.yaml"
    with open(settings_file, 'w') as f:
        yaml.dump(settings_valid, f)
    return settings_file
