"""
Configuration management for CSE-AIML ERP MCP Server.
"""
import os
from typing import Optional
from pydantic import BaseSettings, Field
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    """Application settings with validation."""
    
    mongo_uri: str = Field(
        default="mongodb://localhost:27017/",
        description="MongoDB connection URI"
    )
    
    database_name: str = Field(
        default="cse_aiml_erp",
        description="MongoDB database name"
    )
    
    mcp_server_name: str = Field(
        default="cse-aiml-erp-server",
        description="MCP server name"
    )
    
    max_connection_pool_size: int = Field(
        default=10,
        description="Maximum MongoDB connection pool size"
    )
    
    connection_timeout: int = Field(
        default=5000,
        description="MongoDB connection timeout in milliseconds"
    )
    
    server_timeout: int = Field(
        default=30000,
        description="Server timeout in milliseconds"
    )
    
    # Pagination settings
    default_page_size: int = Field(
        default=50,
        description="Default page size for paginated results"
    )
    
    max_page_size: int = Field(
        default=1000,
        description="Maximum page size for paginated results"
    )
    
    # Logging settings
    log_level: str = Field(
        default="INFO",
        description="Logging level"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings."""
    return settings


def get_mongo_uri() -> str:
    """Get MongoDB URI from environment or settings."""
    return os.getenv("MONGO_URI", settings.mongo_uri)


def get_database_name() -> str:
    """Get database name from environment or settings."""
    return os.getenv("DATABASE_NAME", settings.database_name)


def get_mcp_server_name() -> str:
    """Get MCP server name from environment or settings."""
    return os.getenv("MCP_SERVER_NAME", settings.mcp_server_name)
