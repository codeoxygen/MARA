from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings from environment variables"""

    # LLM
    anthropic_api_key: str

    # Slack Configuration
    slack_webhook_url: Optional[str] = None
    slack_bot_token: Optional[str] = None
    base_url: str = "https://example.ngrok.io"

    # Analytics
    ga4_property_id: Optional[str] = None
    google_application_credentials: Optional[str] = None

    # App
    app_env: str = "development"
    log_level: str = "INFO"
    max_revision_iterations: int = 5
    websocket_max_size: int = 10485760

    # Server
    server_host: str = "0.0.0.0"
    server_port: int = 8000

    class Config:
        env_file = str(Path(__file__).parent.parent.parent / ".env")
        case_sensitive = False

settings = Settings()
