"""
Configuration management using Pydantic Settings.
"""

from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow"
    )
    
    # Application
    environment: str = "development"
    secret_key: str
    debug: bool = False
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 4
    
    # WhatsApp
    whatsapp_provider: str = "meta"
    whatsapp_api_token: str
    whatsapp_phone_number_id: str
    whatsapp_business_account_id: Optional[str] = None
    whatsapp_webhook_verify_token: str
    whatsapp_api_version: str = "v18.0"
    meta_api_url: str = "https://graph.facebook.com"
    
    # Database
    database_url: str
    database_pool_size: int = 20
    database_max_overflow: int = 40
    database_echo: bool = False
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    redis_max_connections: int = 50
    
    # Celery
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"
    
    # Storage
    storage_provider: str = "s3"
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_s3_bucket: Optional[str] = None
    aws_region: str = "us-east-1"
    max_file_size_mb: int = 16
    signed_url_expiry_seconds: int = 3600
    
    # Security
    encryption_key: str
    jwt_secret_key: Optional[str] = None
    jwt_algorithm: str = "HS256"
    bcrypt_rounds: int = 12
    
    # Session
    session_timeout_minutes: int = 30
    session_reminder_minutes: int = 25
    
    # Features
    enable_virus_scan: bool = False
    enable_analytics: bool = False
    enable_metrics: bool = True
    
    # Monitoring
    sentry_dsn: Optional[str] = None
    log_level: str = "INFO"
    log_format: str = "json"
    
    # CORS
    cors_origins: List[str] = Field(default_factory=lambda: ["*"])
    
    @property
    def whatsapp_api_url(self) -> str:
        """Get WhatsApp API URL based on provider."""
        if self.whatsapp_provider == "meta":
            return f"{self.meta_api_url}/{self.whatsapp_api_version}"
        # Add other providers as needed
        return self.meta_api_url


# Global settings instance
settings = Settings()
