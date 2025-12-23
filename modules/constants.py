"""Constants and default values for ngx-renamer."""

# Document title constraints
MAX_TITLE_LENGTH = 127  # Paperless NGX maximum title length

# Provider names - extensible for future providers
PROVIDER_OPENAI = "openai"
PROVIDER_OLLAMA = "ollama"
PROVIDER_CLAUDE = "claude"  # Future
PROVIDER_GROK = "grok"      # Future

# Valid providers (for validation)
VALID_PROVIDERS = frozenset([PROVIDER_OPENAI, PROVIDER_OLLAMA])

# Default models per provider
DEFAULT_MODELS = {
    PROVIDER_OPENAI: "gpt-4o-mini",
    PROVIDER_OLLAMA: "gpt-oss:latest",
    PROVIDER_CLAUDE: "claude-3-5-sonnet-20241022",  # Future
    PROVIDER_GROK: "grok-2",  # Future
}

# Provider-specific config keys (for settings.yaml)
PROVIDER_CONFIG_KEYS = {
    PROVIDER_OPENAI: ["api_key", "model", "organization"],
    PROVIDER_OLLAMA: ["base_url", "api_key", "model"],
    PROVIDER_CLAUDE: ["api_key", "model"],  # Future
    PROVIDER_GROK: ["api_key", "model"],    # Future
}

# JSON schema for structured title output (shared across all providers)
TITLE_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {
            "type": "string",
            "maxLength": MAX_TITLE_LENGTH,
            "description": "The generated document title"
        }
    },
    "required": ["title"],
    "additionalProperties": False
}
