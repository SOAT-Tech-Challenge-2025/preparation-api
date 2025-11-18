# pylint: disable=W0621

"""Integration test configuration fixtures"""

from typing import AsyncGenerator

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from preparation_api.infrastructure import factory
from preparation_api.infrastructure.config import TestDatabaseSettings
from preparation_api.infrastructure.orm import SessionManager
from preparation_api.infrastructure.orm.models import BaseModel


@pytest.fixture(scope="session")
def test_db_settings() -> TestDatabaseSettings:
    """Fixture to create TestDatabaseSettings for integration tests"""
    return TestDatabaseSettings()


@pytest.fixture
async def db_session_manager(
    test_db_settings: TestDatabaseSettings,
) -> AsyncGenerator[SessionManager]:
    """Fixture to create a database session manager for integration tests"""
    session_manager = factory.get_session_manager(settings=test_db_settings)

    # Initialize the database
    async with session_manager._engine.begin() as conn:  # pylint: disable=W0212
        await conn.run_sync(BaseModel.metadata.drop_all)
        await conn.run_sync(BaseModel.metadata.create_all)

    yield session_manager
    await session_manager.close()


@pytest.fixture
async def db_session(
    db_session_manager: SessionManager,
) -> AsyncGenerator[AsyncSession]:
    """Fixture para obter uma sessão individual do banco"""
    async with factory.get_db_session(db_session_manager) as session:
        yield session
