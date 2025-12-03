"""Application configuration module"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class APPSettings(BaseSettings):
    """APP specific settings"""

    model_config = SettingsConfigDict(
        env_file="settings/app.env", env_file_encoding="utf-8", env_prefix="APP_"
    )

    TITLE: str = "SOAT Tech Challenge Preparation Api"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "PRD"
    ROOT_PATH: str = "/api"


class DatabaseSettings(BaseSettings):
    """Database specific settings"""

    model_config = SettingsConfigDict(
        env_file="settings/database.env",
        env_file_encoding="utf-8",
        env_prefix="DATABASE_",
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
        env_file="settings/order_api.env",
        env_file_encoding="utf-8",
        env_prefix="ORDER_API_",
    )

    BASE_URL: str
    TIMEOUT: float = 10.0  # seconds


class PaymentClosedListenerSettings(BaseSettings):
    """Payment Closed Listener settings"""

    model_config = SettingsConfigDict(
        env_file="settings/payment_closed_listener.env",
        env_file_encoding="utf-8",
        env_prefix="PAYMENT_CLOSED_LISTENER_",
    )

    QUEUE_NAME: str
    WAIT_TIME_SECONDS: int = 5
    MAX_NUMBER_OF_MESSAGES_PER_BATCH: int = 5
    VISIBILITY_TIMEOUT_SECONDS: int = 60


class AWSSettings(BaseSettings):
    """AWS integration settings"""

    model_config = SettingsConfigDict(
        env_file="settings/aws.env",
        env_file_encoding="utf-8",
        env_prefix="AWS_",
    )

    REGION_NAME: str = "us-east-1"
    ACCOUNT_ID: str
    ACCESS_KEY_ID: str
    SECRET_ACCESS_KEY: str
