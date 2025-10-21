"""Application configuration using Pydantic Settings"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    app_name: str = Field(default="Label Check API", alias="APP_NAME")
    app_version: str = Field(default="1.0.0", alias="APP_VERSION")
    environment: str = Field(default="development", alias="ENVIRONMENT")
    debug: bool = Field(default=True, alias="DEBUG")
    host: str = Field(default="0.0.0.0", alias="HOST")
    port: int = Field(default=8000, alias="PORT")
    
    # API Keys
    claude_api_key: str = Field(..., alias="CLAUDE_API_KEY")
    
    # Database (Supabase)
    supabase_url: str = Field(..., alias="SUPABASE_URL")
    supabase_key: str = Field(..., alias="SUPABASE_KEY")
    
    # CORS
    allowed_origins: List[str] = Field(
        default=["http://localhost:3000"],
        alias="ALLOWED_ORIGINS"
    )
    
    # File Upload
    max_file_size: int = Field(default=10485760, alias="MAX_FILE_SIZE")  # 10MB
    upload_dir: str = Field(default="./uploads", alias="UPLOAD_DIR")
    
    # Email Service (optional)
    smtp_host: str = Field(default="smtp.gmail.com", alias="SMTP_HOST")
    smtp_port: int = Field(default=587, alias="SMTP_PORT")
    smtp_user: str = Field(default="", alias="SMTP_USER")
    smtp_password: str = Field(default="", alias="SMTP_PASSWORD")
    from_email: str = Field(default="noreply@labelcheck.com", alias="FROM_EMAIL")
    
    # Rate Limiting
    rate_limit_per_minute: int = Field(default=60, alias="RATE_LIMIT_PER_MINUTE")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        
        @classmethod
        def parse_env_var(cls, field_name: str, raw_val: str) -> any:
            if field_name == "allowed_origins":
                return [origin.strip() for origin in raw_val.split(",")]
            return raw_val


# Create settings instance
settings = Settings()

