# Forge Free-First Stack

Use this if you want the first version running with little or no API spend.

## Model options

### Option 1: NVIDIA API Catalog / NIM

- Good when you want hosted models with free credits
- Use OpenAI-compatible settings in the backend
- Use the example script at `scripts/nvidia_chat_example.py`
- This is the default local example for Forge
- Start with:

```ini
API_KEY=nvapi-your-key
API_BASE=https://integrate.api.nvidia.com/v1
MODEL_PROVIDER=openai
MODEL_NAME=meta/llama-3.1-70b-instruct
```

For the exact sample you pasted, use:

```ini
NVIDIA_API_KEY=your-key
NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1
NVIDIA_MODEL=openai/gpt-oss-20b
```

### Option 2: Gemini API

- Good when you want a free tier and fast setup
- Also works with OpenAI-style API compatibility
- Start with:

```ini
API_KEY=your-gemini-key
API_BASE=https://generativelanguage.googleapis.com/v1beta/openai/
MODEL_PROVIDER=openai
MODEL_NAME=gemini-2.0-flash
```

### Option 3: Local Ollama

- Good when you want truly free local inference
- Requires Ollama running on your machine

```ini
API_KEY=ollama
API_BASE=http://host.docker.internal:11434/v1
MODEL_PROVIDER=openai
MODEL_NAME=llama3.1
```

## Search options

- `tavily` for better research with free credits
- `bing_web` for no-key web scraping style search

Recommended starting search config:

```ini
SEARCH_PROVIDER=tavily
TAVILY_API_KEY=your-key
```

## Minimum local services

- Docker
- MongoDB
- Redis
- backend
- frontend
- sandbox
- claw

## What to do first

1. Copy `.env.example` to `.env`
2. Pick one model provider above
3. Set `SEARCH_PROVIDER`
4. Run `docker compose up -d`
