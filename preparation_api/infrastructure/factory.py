"""Factory module for manual dependency injection"""

from contextlib import asynccontextmanager
from typing import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession

from preparation_api.infrastructure.config import DatabaseSettings
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
