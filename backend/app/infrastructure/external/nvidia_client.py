from openai import AsyncOpenAI

from app.core.config import get_settings


def get_nvidia_client() -> AsyncOpenAI:
    settings = get_settings()
    return AsyncOpenAI(
        base_url=settings.api_base or "https://integrate.api.nvidia.com/v1",
        api_key=settings.nvidia_api_key or settings.api_key,
    )
