# LLM Configuration Guide — AI Career Agent V2

## Overview

The LLM provider layer is optional. The system always works in demo mode
without any API key. When a real provider is configured, it can be used
for richer job analysis (currently available as a future hook in the detail panel).

---

## Provider Selection

Set the `LLM_PROVIDER` environment variable to choose a provider:

```bash
LLM_PROVIDER=claude    # Anthropic Claude
LLM_PROVIDER=openai    # OpenAI
LLM_PROVIDER=gemini    # Google Gemini
LLM_PROVIDER=ollama    # Local Ollama (self-hosted)
LLM_PROVIDER=mock      # Mock/rule-based (default, no API key needed)
```

If `LLM_PROVIDER` is not set, the system uses `mock` automatically.

---

## Provider Setup

### Claude (Anthropic)

```bash
pip install anthropic>=0.25.0
export LLM_PROVIDER=claude
export ANTHROPIC_API_KEY=sk-ant-...

# Optional: choose model (default: claude-haiku-4-5-20251001)
export CLAUDE_MODEL=claude-haiku-4-5-20251001
```

Models:
- `claude-haiku-4-5-20251001` — fastest, cheapest (default)
- `claude-sonnet-4-6` — more capable

### OpenAI

```bash
pip install openai>=1.0.0
export LLM_PROVIDER=openai
export OPENAI_API_KEY=sk-...

# Optional: choose model (default: gpt-4o-mini)
export OPENAI_MODEL=gpt-4o-mini
```

### Gemini (Google)

```bash
pip install google-generativeai>=0.5.0
export LLM_PROVIDER=gemini
export GOOGLE_API_KEY=AIza...

# Optional: choose model (default: gemini-1.5-flash)
export GEMINI_MODEL=gemini-1.5-flash
```

### Ollama (Local / Self-hosted)

Ollama requires no Python SDK — it uses HTTP. Install Ollama from https://ollama.com,
then pull a model and start the server.

```bash
ollama pull llama3
ollama serve   # starts on http://localhost:11434

export LLM_PROVIDER=ollama
# Optional overrides:
export OLLAMA_BASE_URL=http://localhost:11434
export OLLAMA_MODEL=llama3
```

---

## Fallback Behavior

If the configured provider is unavailable for any reason:
- Missing API key
- SDK package not installed
- Network error

The system **automatically falls back to MockLLMProvider** and logs a warning.
No exception is raised; the app continues to function.

---

## Using .env File

Create a `.env` file in the project root (never commit it):

```
# .env
LLM_PROVIDER=claude
ANTHROPIC_API_KEY=sk-ant-...
```

The app loads `.env` automatically via `python-dotenv` if present.

---

## Provider Status in Dashboard

The sidebar shows the active LLM provider name and availability:
- `⚪ mock` — no real provider configured (demo mode)
- `🟢 claude` — Claude is active
- `🟢 openai` — OpenAI is active

---

## Adding a Custom Provider

1. Create `app/llm/providers/my_provider.py` implementing `BaseLLMProvider`
2. Add the provider name to `KNOWN_PROVIDERS` in `app/llm/provider_factory.py`
3. Add a case in `_load_provider()` in the factory
4. Set `LLM_PROVIDER=my_provider` in your environment
