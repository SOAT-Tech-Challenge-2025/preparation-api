"""Factory module for manual dependency injection"""

from contextlib import asynccontextmanager
from typing import AsyncIterator

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from preparation_api.adapters.out import APIOrderInfoProvider
from preparation_api.domain.ports import OrderInfoProvider
from preparation_api.infrastructure.config import (
    DatabaseSettings,
    OrderAPISettings,
)
from preparation_api.infrastructure.orm import SessionManager


def get_session_manager(settings: DatabaseSettings) -> SessionManager:
    """Return a SessionManager instance"""
    return SessionManager(settings=settings)


@asynccontextmanager
async def get_db_session(
    session_manager: SessionManager,
) -> AsyncIterator[AsyncSession]:
    """Get a database session"""

    async with session_manager.session() as session:
        yield session


def get_http_client() -> AsyncClient:
    """Return an AsyncClient instance"""
    return AsyncClient(timeout=10.0)  # Default timeout of 10 seconds


def get_order_info_provider(
    settings: OrderAPISettings,
    http_client: AsyncClient,
) -> OrderInfoProvider:
    """Return an OrderInfoProvider instance"""
    return APIOrderInfoProvider(settings=settings, http_client=http_client)
