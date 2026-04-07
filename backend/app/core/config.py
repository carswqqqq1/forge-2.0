import os
import json
import logging
import secrets
from pydantic_settings import BaseSettings
from functools import lru_cache

logger = logging.getLogger(__name__)


def _parse_extra_headers() -> dict | None:
    raw = os.environ.get("EXTRA_HEADERS")
    if not raw:
        return None
    try:
        headers = json.loads(raw)
        if isinstance(headers, dict):
            return headers
        logger.warning("EXTRA_HEADERS is not a JSON object, ignoring")
    except json.JSONDecodeError:
        logger.warning("EXTRA_HEADERS is not valid JSON, ignoring")
    return None


class Settings(BaseSettings):
    
    # Model provider configuration
    api_key: str | None = None
    api_base: str | None = None
    
    # Model configuration
    model_tier: str = "lite"  # "lite", "regular" or "max"
    model_name: str = "meta/llama-3.1-8b-instruct"
    model_name_lite: str = "meta/llama-3.1-8b-instruct"
    model_name_regular: str = "openai/gpt-oss-20b"
    model_name_max: str = "openai/gpt-oss-120b"
    model_provider: str = "openai"
    memory_model_name_lite: str = "meta/llama-3.1-8b-instruct"
    memory_model_name_regular: str = "openai/gpt-oss-20b"
    memory_model_name_max: str = "openai/gpt-oss-120b"
    memory_model_name: str = "meta/llama-3.1-8b-instruct"
    temperature_lite: float = 0.7
    max_tokens_lite: int = 1600
    temperature: float = 0.7
    max_tokens: int = 2000
    temperature_max: float = 0.3
    max_tokens_max: int = 4000
    
    # MongoDB configuration
    mongodb_uri: str = "mongodb://mongodb:27017"
    mongodb_database: str = "manus"
    mongodb_username: str | None = None
    mongodb_password: str | None = None
    
    # Redis configuration
    redis_host: str = "redis"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str | None = None
    
    # Sandbox configuration
    sandbox_address: str | None = None
    sandbox_image: str | None = None
    sandbox_name_prefix: str | None = None
    sandbox_ttl_minutes: int | None = 30
    sandbox_network: str | None = None  # Docker network bridge name
    sandbox_chrome_args: str | None = ""
    sandbox_https_proxy: str | None = None
    sandbox_http_proxy: str | None = None
    sandbox_no_proxy: str | None = None

    # Browser engine configuration
    browser_engine: str = "browser_use"  # "playwright" or "browser_use"
    
    # Search engine configuration
    search_provider: str | None = "bing_web"  # "baidu", "baidu_web", "google", "bing", "bing_web", "tavily"
    baidu_search_api_key: str | None = None
    bing_search_api_key: str | None = None
    google_search_api_key: str | None = None
    google_search_engine_id: str | None = None
    tavily_api_key: str | None = None
    
    # Google Analytics configuration
    google_analytics_id: str | None = None

    # Auth configuration
    auth_provider: str = "password"  # "password", "none", "local"
    show_github_button: bool = False
    github_repository_url: str = ""
    password_salt: str | None = None
    password_hash_rounds: int = 10
    password_hash_algorithm: str = "pbkdf2_sha256"
    local_auth_email: str = ""
    local_auth_password: str = ""
    
    # Email configuration
    email_host: str | None = None  # "smtp.gmail.com"
    email_port: int | None = None  # 587
    email_username: str | None = None
    email_password: str | None = None
    email_from: str | None = None
    
    # JWT configuration
    jwt_secret_key: str = secrets.token_hex(32)
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7
    
    # Extra headers for LLM requests (parsed from EXTRA_HEADERS env var, JSON)
    extra_headers: dict | None = None
    
    # Claw (OpenClaw) configuration
    claw_enabled: bool = False
    claw_image: str = "simpleyyt/manus-claw"
    claw_name_prefix: str = "manus-claw"
    claw_ttl_seconds: int = 3600
    claw_network: str | None = None  # Docker network bridge name for claw containers
    claw_ready_timeout: int = 300  # Max seconds to wait for claw container to become ready
    claw_address: str | None = None  # If set, use this fixed host instead of creating Docker containers
    claw_api_key: str | None = None  # Static API key accepted by the LLM proxy (for dev/fixed container)
    manus_api_base_url: str = "http://backend:8000"  # URL of this backend accessible from claw containers

    # MCP configuration
    mcp_config_path: str = "/etc/mcp.json"
    
    # Logging configuration
    log_level: str = "INFO"
    max_request_body_size_bytes: int = 1_048_576
    tool_call_timeout_seconds: float = 25.0
    agent_task_timeout_seconds: float = 600.0
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        
    def validate(self):
        """Validate configuration settings"""
        if not self.api_key:
            raise ValueError("API key is required")
        if self.auth_provider == "local" and (not self.local_auth_email or not self.local_auth_password):
            raise ValueError("LOCAL_AUTH_EMAIL and LOCAL_AUTH_PASSWORD must be set in environment")

@lru_cache()
def get_settings() -> Settings:
    """Get application settings"""
    if not os.environ.get("OPENAI_API_KEY"):
        api_key = os.getenv("API_KEY")
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
    if not os.environ.get("OPENAI_BASE_URL") and os.getenv("API_BASE"):
        os.environ["OPENAI_BASE_URL"] = os.getenv("API_BASE")
    settings = Settings()
    tier = (settings.model_tier or "regular").lower()
    if tier == "max":
        settings.model_name = settings.model_name_max
        settings.temperature = settings.temperature_max
        settings.max_tokens = settings.max_tokens_max
        settings.memory_model_name = settings.memory_model_name_max
    elif tier == "regular":
        settings.model_name = settings.model_name_regular
        settings.memory_model_name = settings.memory_model_name_regular
    else:
        settings.model_name = settings.model_name_lite
        settings.temperature = settings.temperature_lite
        settings.max_tokens = settings.max_tokens_lite
        settings.memory_model_name = settings.memory_model_name_lite
    settings.extra_headers = _parse_extra_headers()
    settings.validate()
    return settings 
