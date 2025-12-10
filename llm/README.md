# LLM Provider Plugin System

This directory contains a pluggable LLM provider system that allows you to easily switch between different AI models (Gemini, OpenAI, Anthropic, Ollama) without changing your application code.

## Architecture

```
llm/
├── __init__.py          # Package exports
├── base.py              # Abstract base class for all providers
├── factory.py           # Factory pattern for provider creation
├── gemini.py            # Google Gemini implementation
├── openai.py            # OpenAI implementation
├── anthropic.py         # Anthropic Claude implementation
└── ollama.py            # Ollama (local) implementation
```

## Supported Providers

| Provider | Model Examples | API Key Required | Package Required |
|----------|---------------|------------------|------------------|
| **Gemini** | `gemini-flash-latest`, `gemini-2.0-flash-exp` | Yes (GEMINI_API_KEY) | `google-generativeai` |
| **OpenAI** | `gpt-4o-mini`, `gpt-4o`, `gpt-3.5-turbo` | Yes (OPENAI_API_KEY) | `openai` |
| **Anthropic** | `claude-3-5-sonnet-20241022`, `claude-3-opus` | Yes (ANTHROPIC_API_KEY) | `anthropic` |
| **Ollama** | `llama3.2`, `mistral`, `codellama` | No (local) | None (httpx) |

## Quick Start

### 1. Choose Your Provider

Set the `LLM_PROVIDER` environment variable in `.env`:

```bash
# Use Gemini (default)
LLM_PROVIDER="gemini"
GEMINI_API_KEY="your-api-key"
GEMINI_MODEL="gemini-flash-latest"

# OR use OpenAI
LLM_PROVIDER="openai"
OPENAI_API_KEY="your-api-key"
LLM_MODEL="gpt-4o-mini"

# OR use Anthropic
LLM_PROVIDER="anthropic"
ANTHROPIC_API_KEY="your-api-key"
LLM_MODEL="claude-3-5-sonnet-20241022"

# OR use Ollama (local)
LLM_PROVIDER="ollama"
OLLAMA_MODEL="llama3.2"
OLLAMA_BASE_URL="http://localhost:11434"
```

### 2. Install Required Package

```bash
# For Gemini (already installed)
pip install google-generativeai

# For OpenAI
pip install openai

# For Anthropic
pip install anthropic

# For Ollama (no package needed, just ensure Ollama is running)
# Download from: https://ollama.com/
```

### 3. Use in Code

```python
from llm.factory import LLMFactory

# Create provider (reads from environment)
provider = LLMFactory.create_provider()

# Generate text
response = await provider.generate("Analyze this SQL error...")
print(response)
```

## API Endpoints

### Check Available Providers

```bash
curl http://localhost:8000/llm/providers
```

Response:
```json
{
  "current_provider": "gemini",
  "available_providers": ["gemini"],
  "supported_providers": ["gemini", "openai", "anthropic", "ollama"]
}
```

### Test LLM

```bash
curl -X POST "http://localhost:8000/llm/test?prompt=Hello"
```

Response:
```json
{
  "provider": "gemini",
  "model": "gemini-flash-latest",
  "prompt": "Hello",
  "response": "Hello! How can I help you today?"
}
```

## Provider-Specific Configuration

### Gemini
```bash
GEMINI_API_KEY="your-key"
GEMINI_MODEL="gemini-flash-latest"  # or gemini-2.0-flash-exp
```

Available models: `gemini-flash-latest`, `gemini-2.0-flash-exp`, `gemini-pro-latest`

### OpenAI
```bash
OPENAI_API_KEY="your-key"
LLM_MODEL="gpt-4o-mini"  # or gpt-4o, gpt-3.5-turbo
```

Optional parameters (set in code):
- `temperature`: 0.0 to 2.0 (default: 0.7)
- `max_tokens`: Max response length (default: 2000)

### Anthropic
```bash
ANTHROPIC_API_KEY="your-key"
LLM_MODEL="claude-3-5-sonnet-20241022"
```

Available models: `claude-3-5-sonnet-20241022`, `claude-3-opus-20240229`, `claude-3-haiku`

### Ollama
```bash
OLLAMA_MODEL="llama3.2"
OLLAMA_BASE_URL="http://localhost:11434"  # optional, this is default
```

Available models (must be pulled first):
```bash
ollama pull llama3.2
ollama pull mistral
ollama pull codellama
```

## Adding a New Provider

1. Create a new file `llm/your_provider.py`
2. Inherit from `BaseLLMProvider`
3. Implement `generate()` and `is_available()` methods
4. Add to factory in `llm/factory.py`

Example:
```python
from .base import BaseLLMProvider

class YourProvider(BaseLLMProvider):
    async def generate(self, prompt: str) -> str:
        # Your implementation
        pass
    
    def is_available(self) -> bool:
        # Check if configured
        return self.api_key is not None
```

## Advanced Usage

### Custom Configuration

```python
from llm.factory import LLMFactory

# Override provider from code
provider = LLMFactory.create_provider(
    provider_type="openai",
    api_key="custom-key",
    model="gpt-4o",
    temperature=0.5,
    max_tokens=3000
)

response = await provider.generate("Your prompt")
```

### Programmatic Provider Selection

```python
# Check available providers
available = LLMFactory.get_available_providers()
print(f"Available: {available}")  # ['gemini', 'openai']

# Use first available
if 'gemini' in available:
    provider = LLMFactory.create_provider(provider_type='gemini')
elif 'openai' in available:
    provider = LLMFactory.create_provider(provider_type='openai')
```

## Best Practices

1. **Development**: Use Ollama for local testing (free, fast, offline)
2. **Production**: Use Gemini for cost-effectiveness or OpenAI/Anthropic for quality
3. **API Keys**: Store in `.env` file, never commit to version control
4. **Rate Limits**: Implement retry logic for production use
5. **Cost**: Monitor API usage, Gemini free tier: 15 requests/minute

## Troubleshooting

### "Provider not available"
- Check API key is set in `.env`
- Verify package is installed (`pip list | grep openai`)
- For Ollama, ensure server is running (`ollama serve`)

### "Quota exceeded"
- Wait for rate limit to reset
- Switch to different provider
- Upgrade to paid tier

### "Model not found"
- Check model name spelling
- For Ollama, run `ollama pull <model>`
- Verify model is available for your API tier

## Performance Comparison

| Provider | Speed | Cost | Quality | Offline |
|----------|-------|------|---------|---------|
| Ollama | ⚡⚡⚡ Fast | 💰 Free | ⭐⭐⭐ Good | ✅ Yes |
| Gemini | ⚡⚡ Medium | 💰 Low | ⭐⭐⭐⭐ Great | ❌ No |
| OpenAI | ⚡ Slower | 💰💰 Medium | ⭐⭐⭐⭐⭐ Best | ❌ No |
| Anthropic | ⚡ Slower | 💰💰 Medium | ⭐⭐⭐⭐⭐ Best | ❌ No |
