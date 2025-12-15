# Testing Structured Outputs

This guide helps verify that structured outputs work correctly with both Ollama and OpenAI providers.

## Background

Structured outputs were implemented using JSON schemas to ensure reliable title extraction. The implementation addresses feedback about:

1. ✅ **Fixed**: maxLength corrected from 128 to 127 (matches Paperless NGX limit)
2. ⚠️ **Needs Testing**: Ollama format parameter structure verification

## Ollama Format Parameter

### Current Implementation

We pass the JSON schema dict directly to the `format` parameter:

```python
response = self._client.chat(
    model=model,
    messages=[...],
    format=TITLE_SCHEMA,  # Dict passed directly
)
```

### Type Signature

According to `ollama-python` library (v0.6.1):
```python
format: Union[Literal['', 'json'], dict[str, Any], None]
```

This confirms that passing a `dict` is valid.

### Alternative Approaches (if issues arise)

If the current approach fails in practice, try these alternatives:

#### Option 1: Generic JSON Mode
```python
response = self._client.chat(
    model=model,
    messages=[...],
    format='json',  # Generic JSON, no schema validation
)
```

#### Option 2: Pydantic Schema (Recommended by Ollama)
```python
from pydantic import BaseModel

class TitleResponse(BaseModel):
    title: str

response = self._client.chat(
    model=model,
    messages=[...],
    format=TitleResponse.model_json_schema(),
)
```

## Testing Checklist

### Prerequisites

- [ ] Ollama installed and running: `ollama --version`
- [ ] Model pulled: `ollama pull qwen3-vl:2b` (or your configured model)
- [ ] Environment variables set in `.env`:
  - `OLLAMA_BASE_URL=http://localhost:11434`
  - `PAPERLESS_NGX_URL` and `PAPERLESS_NGX_API_KEY`

### Test 1: Ollama Structured Output (Real API)

Run Ollama-specific integration tests:

```bash
pytest -v tests/integration/test_ollama_integration.py::TestOllamaTitleGeneration::test_structured_output_returns_valid_title
```

**Expected Output:**
- Test passes ✓
- Prints: `Structured output title: <generated title>`
- Title is valid JSON-parsed string

**If test fails with JSON decode error:**
- Ollama may be returning plain text instead of JSON
- Check Ollama version: `ollama --version` (needs 0.5.0+)
- Try alternative format approaches above

### Test 2: OpenAI Structured Output (Real API)

Requires OpenAI API key in `.env`:

```bash
pytest -v tests/integration/test_openai_integration.py::TestOpenAITitleGeneration::test_generate_title_from_invoice
```

**Expected Output:**
- Test passes ✓
- Returns valid JSON-parsed title
- Auto-truncates to 127 chars if needed

### Test 3: Schema Validation

Verify schemas are correctly formatted:

```bash
pytest -v tests/integration/test_structured_outputs.py::TestSchemaStructure
```

**Expected Output:**
- All 3 tests pass ✓
- maxLength is 127 (not 128)
- Both providers use identical schemas

### Test 4: Manual Title Generation (Ollama)

Test with a real document:

```bash
python3 -c "
from modules.ollama_titles import OllamaTitles
import os

ollama_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
ai = OllamaTitles(ollama_url, 'settings.yaml')

sample_text = '''
INVOICE #12345
Amazon Web Services
Monthly Subscription: \$125.00
'''

title = ai.generate_title_from_text(sample_text)
print(f'Generated title: {title}')
print(f'Title length: {len(title) if title else 0}')
print(f'Is valid: {title is not None and len(title) <= 127}')
"
```

**Expected Output:**
```
Generated title: Amazon - Monthly Subscription Invoice
Title length: 41
Is valid: True
```

**If you see:**
- `Error: Ollama returned invalid JSON` → Model doesn't support structured outputs or format parameter is incorrect
- `None` → Check Ollama is running and model is available

### Test 5: Manual Title Generation (OpenAI)

```bash
python3 -c "
from modules.openai_titles import OpenAITitles
import os

api_key = os.getenv('OPENAI_API_KEY')
ai = OpenAITitles(api_key, 'settings.yaml')

sample_text = '''
Legal Notice
Contract Amendment
Effective Date: 2024-01-15
'''

title = ai.generate_title_from_text(sample_text)
print(f'Generated title: {title}')
print(f'Title length: {len(title) if title else 0}')
print(f'Is valid: {title is not None and len(title) <= 127}')
"
```

## Troubleshooting

### Issue: "Ollama returned invalid JSON"

**Cause**: Model doesn't support structured outputs or format parameter structure is incorrect.

**Solutions**:

1. **Update Ollama**: Ensure Ollama >= 0.5.0
   ```bash
   ollama --version
   ```

2. **Try Generic JSON Mode**: Edit `modules/ollama_titles.py`:
   ```python
   # Change line 68 from:
   format=TITLE_SCHEMA,
   # To:
   format='json',
   ```

3. **Use Pydantic** (more reliable):
   ```python
   from pydantic import BaseModel, Field

   class TitleResponse(BaseModel):
       title: str = Field(..., max_length=127)

   # In __call_ollama_api:
   response = self._client.chat(
       model=model,
       messages=[...],
       format=TitleResponse.model_json_schema(),
   )
   ```

4. **Check Model Compatibility**: Not all models support structured outputs
   - ✅ Works: `llama3.1:8b`, `qwen2:7b`, `mistral:7b`
   - ❌ May not work: Older models or very small models

### Issue: Title Exceeds 127 Characters

**Cause**: Model ignores maxLength constraint or generates title before schema validation.

**Solution**: Auto-truncation is already implemented in `_parse_structured_response()`:
```python
if len(title) > 127:
    title = title[:127]
```

This is a fallback; ideally the schema should constrain the model.

### Issue: Empty or None Titles

**Cause**: JSON parsing succeeded but title field is empty/missing.

**Check**:
1. Verify prompt is being sent: Add debug print in `generate_title_from_text()`
2. Check model response: Add print before JSON parsing
3. Verify settings.yaml prompt configuration

## Version Compatibility

| Component | Version | Notes |
|-----------|---------|-------|
| ollama-python | 0.6.1 | Current installed version |
| Ollama Server | 0.5.0+ | Required for structured outputs |
| OpenAI API | Latest | Structured outputs supported in gpt-4o, gpt-4o-mini |
| Python | 3.8+ | Required for type hints |

## Success Criteria

✅ **Implementation is working correctly if:**

1. All 28 structured output tests pass
2. Ollama integration tests pass (or skip if Ollama not running)
3. OpenAI integration tests pass (or skip if no API key)
4. Manual testing produces valid JSON-parsed titles
5. Titles are auto-truncated to 127 chars when needed
6. Both providers use identical schemas (maxLength: 127)

## References

- Ollama Structured Outputs: https://ollama.com/blog/structured-outputs
- OpenAI Structured Outputs: https://platform.openai.com/docs/guides/structured-outputs
- Ollama Python Client: https://github.com/ollama/ollama-python
- Implementation: [modules/ollama_titles.py](modules/ollama_titles.py), [modules/openai_titles.py](modules/openai_titles.py)
