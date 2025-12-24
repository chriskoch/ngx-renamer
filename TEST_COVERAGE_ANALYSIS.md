# Test Coverage Analysis

**Date:** 2025-12-24
**Current Overall Coverage:** 52%
**Total Test Functions:** 85 tests (all integration tests)

## Executive Summary

The ngx-renamer codebase has a **moderate test coverage of 52%**, but with significant gaps that need attention. The testing strategy currently relies entirely on integration tests, with **no unit tests** present. This analysis identifies critical areas requiring improved test coverage and proposes a comprehensive testing strategy.

---

## Current Coverage Breakdown

### Well-Tested Modules (>90%)
✅ **100% Coverage:**
- `modules/__init__.py`
- `modules/constants.py` - Constants and configuration values
- `modules/exceptions.py` - Custom exception classes
- `modules/logger.py` - Logging utilities

✅ **95% Coverage:**
- `modules/providers/__init__.py` - Provider registry system

✅ **85% Coverage:**
- `modules/llm_factory.py` - LLM provider factory pattern
  - **Missing coverage:** Lines 62, 78-79, 113-114 (edge case error handling)

### Moderately Tested Modules (50-70%)
⚠️ **57% Coverage:**
- `modules/base_llm_provider.py` - Abstract base class for LLM providers
  - **Missing coverage:** Lines 40-42 (error handling), 55-82 (prompt building), 125-127 (exception handling), 141 (abstract method)
- `modules/paperless_ai_titles.py` - Main orchestrator class
  - **Missing coverage:** Lines 72-74 (error handling), 89-116 (core workflow methods)

### Poorly Tested Modules (<40%)
❌ **20% Coverage:**
- `modules/claude_titles.py` - Anthropic Claude provider implementation
  - **Missing coverage:** Lines 22-23, 34-70 (API calls), 81-109 (title generation logic)
  - **Critical gap:** Main API integration and response parsing untested

❌ **32% Coverage:**
- `modules/paperless_client.py` - Paperless NGX API client
  - **Missing coverage:** Lines 40-60 (get_document), 72-100 (update_document_title)
  - **Critical gap:** Core API methods completely untested

❌ **33% Coverage:**
- `modules/ollama_titles.py` - Ollama provider implementation
  - **Missing coverage:** Lines 51-85 (API calls), 96-110 (title generation)
  - **Critical gap:** Main integration logic untested

❌ **34% Coverage:**
- `modules/openai_titles.py` - OpenAI provider implementation
  - **Missing coverage:** Lines 22-23, 35-65 (API calls), 76-85 (title generation)
  - **Critical gap:** Main integration logic untested

---

## Test Suite Analysis

### Current Test Structure
```
tests/
├── integration/          # 8 test files, 85 tests
│   ├── test_claude_integration.py
│   ├── test_end_to_end.py
│   ├── test_llm_provider_selection.py
│   ├── test_ollama_api_key.py
│   ├── test_ollama_integration.py
│   ├── test_openai_integration.py
│   ├── test_paperless_integration.py
│   └── test_structured_outputs.py
├── fixtures/             # Test fixtures and settings
└── conftest.py           # Shared fixtures
```

### ❌ Missing Test Structure
```
tests/
└── unit/                 # DOES NOT EXIST!
```

---

## Critical Gaps Identified

### 1. **No Unit Tests**
**Impact:** High
**Severity:** Critical

The entire test suite consists of integration tests. This creates several problems:
- **Slow test execution** - Integration tests require external dependencies
- **Difficult debugging** - Failures don't pinpoint specific functions
- **Low coverage of edge cases** - Integration tests typically cover happy paths
- **External dependencies** - Tests skip when API keys unavailable

**Examples of untested unit-level functionality:**
- Prompt building logic (`base_llm_provider.py:_build_prompt()`)
- JSON response parsing (`base_llm_provider.py:_parse_structured_response()`)
- Settings file loading error handling
- Title truncation logic
- Error message formatting

### 2. **Paperless API Client Untested**
**Impact:** High
**Severity:** Critical

`modules/paperless_client.py` has only 32% coverage:
- `get_document()` method - **completely untested**
- `update_document_title()` method - **completely untested**
- Error handling for HTTP errors - **untested**
- Network timeout handling - **untested**
- Authentication header construction - **partially tested**

**Risk:** Production failures in API communication won't be caught by tests.

### 3. **Provider Implementation Logic Undertested**
**Impact:** High
**Severity:** High

All three provider implementations (Claude 20%, Ollama 33%, OpenAI 34%) have critical gaps:
- API call methods - **mostly untested**
- Response parsing - **mostly untested**
- Error handling for API failures - **mostly untested**
- Retry logic (if any) - **untested**
- Model configuration reading - **partially tested**

### 4. **Core Workflow Untested**
**Impact:** Medium
**Severity:** High

`paperless_ai_titles.py:generate_and_update_title()` (lines 89-116) is **completely untested**:
- Document fetching flow
- Content validation
- Title generation orchestration
- Error handling cascade
- Logging behavior

### 5. **Edge Cases and Error Paths**
**Impact:** Medium
**Severity:** Medium

Integration tests focus on happy paths. Untested scenarios include:
- Empty document content
- Malformed settings files
- Network timeouts
- Invalid JSON responses from LLMs
- Title length edge cases (exactly 127 chars, unicode boundaries)
- Missing configuration values
- Invalid API keys (partially tested)

---

## Recommended Test Improvements

### Priority 1: Add Unit Tests (High Impact)

#### 1.1 Create `tests/unit/` Directory Structure
```
tests/
├── unit/
│   ├── __init__.py
│   ├── test_base_llm_provider.py
│   ├── test_paperless_client.py
│   ├── test_paperless_ai_titles.py
│   ├── test_claude_titles.py
│   ├── test_ollama_titles.py
│   ├── test_openai_titles.py
│   └── test_llm_factory.py
└── integration/
    └── [existing tests]
```

#### 1.2 Unit Test Coverage Goals

**`test_base_llm_provider.py`** (Target: 90%+)
- `_load_settings()`:
  - ✓ Valid YAML file
  - ✓ Missing file
  - ✓ Invalid YAML syntax
  - ✓ Empty file
  - ✓ File with invalid encoding

- `_build_prompt()`:
  - ✓ Standard prompt with date
  - ✓ Standard prompt without date
  - ✓ Missing prompt configuration
  - ✓ Empty text input
  - ✓ Very long text input
  - ✓ Text with special characters
  - ✓ Date substitution in prompt

- `_parse_structured_response()`:
  - ✓ Valid JSON with title
  - ✓ Valid JSON, empty title
  - ✓ Valid JSON, missing title field
  - ✓ Invalid JSON syntax
  - ✓ Title exactly at 127 char limit
  - ✓ Title over 127 chars (truncation)
  - ✓ Unicode characters near truncation boundary
  - ✓ Non-string title value
  - ✓ Null title value

**`test_paperless_client.py`** (Target: 90%+)
- `__init__()`:
  - ✓ URL with trailing slash
  - ✓ URL without trailing slash
  - ✓ Headers correctly formatted

- `get_document()`:
  - ✓ Successful response (200)
  - ✓ Document not found (404)
  - ✓ Unauthorized (401)
  - ✓ Server error (500)
  - ✓ Network timeout
  - ✓ Connection refused
  - ✓ Invalid JSON response
  - ✓ Malformed document ID

- `update_document_title()`:
  - ✓ Successful update (200)
  - ✓ Document not found (404)
  - ✓ Unauthorized (401)
  - ✓ Server error (500)
  - ✓ Network timeout
  - ✓ Connection refused
  - ✓ Empty title
  - ✓ Very long title
  - ✓ Title with special characters

**`test_paperless_ai_titles.py`** (Target: 85%+)
- `__init__()`:
  - ✓ Valid initialization with all providers
  - ✓ Missing settings file
  - ✓ Invalid settings file
  - ✓ Default provider selection

- `generate_and_update_title()`:
  - ✓ Successful end-to-end flow (mock all dependencies)
  - ✓ Document fetch fails
  - ✓ Document has no content
  - ✓ Title generation fails
  - ✓ Title update fails
  - ✓ PaperlessAPIError handling
  - ✓ Unexpected exceptions

**`test_claude_titles.py`** (Target: 80%+)
- `__init__()`:
  - ✓ Valid initialization
  - ✓ API key validation

- `_call_claude_api()`:
  - ✓ Successful API call
  - ✓ Model from settings (new format)
  - ✓ Model from settings (legacy format)
  - ✓ Default model when not configured
  - ✓ API error handling
  - ✓ Network errors
  - ✓ Invalid response format

- `generate_title_from_text()`:
  - ✓ Successful title generation
  - ✓ Prompt building fails
  - ✓ API call fails
  - ✓ Response missing tool_use block
  - ✓ Title truncation
  - ✓ Empty title in response
  - ✓ Malformed response structure

**`test_ollama_titles.py`** (Target: 80%+)
- `__init__()`:
  - ✓ With API key
  - ✓ Without API key
  - ✓ Empty API key
  - ✓ Whitespace-only API key
  - ✓ Authorization header set correctly

- `_call_ollama_api()`:
  - ✓ Successful API call
  - ✓ Model from settings
  - ✓ Default model
  - ✓ API errors
  - ✓ Network errors
  - ✓ Connection refused (Ollama not running)

- `generate_title_from_text()`:
  - ✓ Successful generation
  - ✓ JSON parsing
  - ✓ Error handling

**`test_openai_titles.py`** (Target: 80%+)
- Similar structure to Claude and Ollama tests
- Focus on OpenAI-specific structured output format
- Response parsing edge cases

**`test_llm_factory.py`** (Target: 95%+)
- `create_provider()`:
  - ✓ All provider types
  - ✓ Case insensitivity
  - ✓ Unknown provider
  - ✓ Missing credentials for each provider
  - ✓ Invalid provider name formats

### Priority 2: Expand Integration Test Coverage

#### 2.1 End-to-End Workflow Tests
Create `tests/integration/test_complete_workflows.py`:
- Full document processing cycle with mocked Paperless API
- Provider switching at runtime
- Configuration reload behavior
- Error recovery scenarios

#### 2.2 Error Scenario Integration Tests
Create `tests/integration/test_error_scenarios.py`:
- Network failures and retries
- Partial failures (document fetched, title generation fails)
- API rate limiting
- Timeout handling

### Priority 3: Test Infrastructure Improvements

#### 3.1 Add Test Coverage Enforcement
Add to `pytest.ini`:
```ini
[pytest]
# ... existing config ...

# Fail build if coverage drops below threshold
addopts =
    -v
    --strict-markers
    --tb=short
    --disable-warnings
    --cov=modules
    --cov-report=term-missing
    --cov-report=html
    --cov-fail-under=75  # Enforce minimum coverage
```

#### 3.2 Add Coverage Badge
Add to README.md:
```markdown
[![Coverage](https://img.shields.io/badge/coverage-XX%25-yellowgreen.svg)]
```

#### 3.3 Separate Unit and Integration Test Execution
Add to `pytest.ini`:
```ini
markers =
    unit: Unit tests (fast, no external dependencies)
    integration: Integration tests (may call external APIs)
    # ... existing markers ...
```

Enable running separately:
```bash
pytest tests/unit/              # Run only unit tests (fast)
pytest tests/integration/       # Run only integration tests
pytest -m "not integration"     # Run all except integration
```

### Priority 4: Add Missing Test Scenarios

#### 4.1 Configuration Edge Cases
- Invalid YAML syntax
- Missing required fields
- Extra unknown fields
- Type mismatches (string vs number)
- Empty configuration values

#### 4.2 Content Edge Cases
- Empty document content
- Very large documents (>100k chars)
- Documents with only whitespace
- Documents with unusual encodings
- Documents with control characters

#### 4.3 Title Edge Cases
- Exactly 127 characters
- 128 characters (requires truncation)
- Unicode characters at position 127
- Emoji in titles
- Special characters: `* / \ : ? " < > |`
- Leading/trailing whitespace

#### 4.4 Error Handling
- All API HTTP error codes (400, 401, 403, 404, 500, 502, 503)
- Network timeouts
- Connection refused
- DNS resolution failures
- SSL/TLS errors

---

## Implementation Roadmap

### Phase 1: Foundation (1-2 days)
1. Create `tests/unit/` directory structure
2. Add `test_base_llm_provider.py` with full coverage
3. Add `test_paperless_client.py` with full coverage
4. Update pytest configuration for unit test separation
5. **Target:** Raise overall coverage to 65%

### Phase 2: Core Logic (2-3 days)
1. Add unit tests for all three provider implementations
2. Add unit tests for `paperless_ai_titles.py`
3. Add unit tests for `llm_factory.py` edge cases
4. **Target:** Raise overall coverage to 80%

### Phase 3: Edge Cases (1-2 days)
1. Add comprehensive edge case tests
2. Add error scenario tests
3. Add integration tests for complete workflows
4. **Target:** Raise overall coverage to 85%+

### Phase 4: Infrastructure (1 day)
1. Add coverage enforcement to CI/CD
2. Add coverage badges
3. Document testing guidelines
4. Set up coverage reporting
5. **Target:** Maintain 85%+ coverage with enforcement

---

## Testing Best Practices to Adopt

### 1. Use Mocking for External Dependencies
```python
# Good: Mock external API calls in unit tests
@patch('modules.claude_titles.anthropic.Anthropic')
def test_call_claude_api_success(mock_anthropic):
    mock_client = mock_anthropic.return_value
    mock_client.messages.create.return_value = mock_response
    # ... test logic
```

### 2. Test One Thing Per Test
```python
# Good: Focused test
def test_parse_response_truncates_long_title():
    response = '{"title": "A" * 200}'
    result = provider._parse_structured_response(response)
    assert len(result) == 127

# Bad: Testing multiple behaviors
def test_parse_response():  # Too broad
    # Tests parsing AND truncation AND error handling
```

### 3. Use Descriptive Test Names
```python
# Good
def test_get_document_returns_404_when_document_not_found():
    pass

# Bad
def test_get_document():
    pass
```

### 4. Separate Unit and Integration Tests
```python
# Unit test - mock all external dependencies
@pytest.mark.unit
def test_build_prompt_with_date():
    # No external calls, pure logic testing
    pass

# Integration test - may call external APIs
@pytest.mark.integration
@pytest.mark.claude
def test_claude_generates_title_end_to_end():
    # Actually calls Claude API
    pass
```

### 5. Test Error Paths, Not Just Happy Paths
```python
def test_get_document_success():           # Happy path
    pass

def test_get_document_network_timeout():   # Error path
    pass

def test_get_document_invalid_response():  # Error path
    pass
```

---

## Metrics and Goals

| Metric | Current | Target | Timeline |
|--------|---------|--------|----------|
| Overall Coverage | 52% | 85% | 6-8 days |
| Unit Test Count | 0 | 150+ | 4-5 days |
| Integration Tests | 85 | 100+ | 2-3 days |
| Modules at 100% | 4/12 (33%) | 8/12 (67%) | 6-8 days |
| Modules under 50% | 5/12 (42%) | 0/12 (0%) | 3-4 days |

---

## Conclusion

The ngx-renamer project has a solid foundation of integration tests (85 tests) but lacks the critical unit test layer needed for robust, maintainable code. The current 52% coverage masks significant gaps in core functionality, particularly in:

1. **Paperless API client** (32% coverage)
2. **Claude provider** (20% coverage)
3. **Provider implementations** (33-34% coverage)
4. **Error handling** across all modules

By implementing the recommended testing strategy—prioritizing unit tests for core logic, expanding edge case coverage, and adding proper test infrastructure—the project can achieve 85%+ coverage and significantly improve code quality, maintainability, and reliability.

The recommended phased approach allows for incremental progress while maintaining development velocity, with the most critical gaps (Paperless client, base provider logic) addressed first.
