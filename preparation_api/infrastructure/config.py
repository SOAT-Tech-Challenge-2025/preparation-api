"""Application configuration module"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class APPSettings(BaseSettings):
    """APP specific settings"""

    model_config = SettingsConfigDict(
        env_file="settings/app.env", env_file_encoding="utf-8"
    )

    TITLE: str = "SOAT Tech Challenge Preparation Api"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "PRD"
    ROOT_PATH: str = "/api"


class DatabaseSettings(BaseSettings):
    """Database specific settings"""

    model_config = SettingsConfigDict(
        env_file="settings/database.env", env_file_encoding="utf-8"
    )

    DSN: str
    ECHO: bool = False


class TestDatabaseSettings(BaseSettings):
    """Test Database specific settings"""

    model_config = SettingsConfigDict(
        env_file="settings/test_database.env", env_file_encoding="utf-8"
    )

    DSN: str
    ECHO: bool = False


class OrderAPISettings(BaseSettings):
    """Order API specific settings"""

    model_config = SettingsConfigDict(
        env_file="settings/order_api.env", env_file_encoding="utf-8"
    )

    BASE_URL: str
    TIMEOUT: float = 10.0  # seconds
