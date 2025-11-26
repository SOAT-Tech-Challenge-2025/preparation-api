"""Entrypoint module for the Preparation API application"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from preparation_api.adapters.inbound.rest.v1.router import (
    router as preparation_router_v1,
)
from preparation_api.infrastructure import factory
from preparation_api.infrastructure.config import (
    APPSettings,
    DatabaseSettings,
)

logger = logging.getLogger(__name__)


def create_api() -> FastAPI:
    """Create FastAPI application instance"""

    logger.info("Creating FastAPI application instance")
    app_instance = FastAPI(lifespan=fastapi_lifespan)
    logger.info("Including preparation router v1")
    app_instance.include_router(preparation_router_v1)
    return app_instance


@asynccontextmanager
async def fastapi_lifespan(app_instance: FastAPI):
    """Lifespan context manager for FastAPI application"""

    # Application state setup
    logger.info("Loading application settings")
    app_instance.state.app_settings = APPSettings()
    logger.info("Loading database settings")
    app_instance.state.database_settings = DatabaseSettings()
    app_instance.title = app_instance.state.app_settings.TITLE
    app_instance.version = app_instance.state.app_settings.VERSION
    app_instance.root_path = app_instance.state.app_settings.ROOT_PATH
    logger.info(
        "Application settings loaded title=%s version=%s root_path=%s",
        app_instance.title,
        app_instance.version,
        app_instance.root_path,
    )

    logger.info("Starting session manager")
    app_instance.state.session_manager = factory.get_session_manager(
        settings=app_instance.state.database_settings
    )

    # Application state teardown
    yield
    logger.info("Closing session manager")
    await app_instance.state.session_manager.close()


app = create_api()
