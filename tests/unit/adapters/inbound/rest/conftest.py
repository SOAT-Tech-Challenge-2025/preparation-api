# pylint: disable=W0621

"""Fixture to provide an AsyncClient for testing FastAPI endpoints"""

from typing import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from pytest_mock import MockerFixture

from preparation_api.adapters.inbound.rest.dependencies.core import (
    get_get_waiting_list_use_case,
    get_mark_preparation_as_completed_use_case,
    get_mark_preparation_as_ready_use_case,
    get_start_next_preparation_use_case,
)
from preparation_api.entrypoints.api import app


@pytest.fixture
def payment_use_cases_mock(mocker: MockerFixture):
    """Fixture to provide a mock for payment use cases called in the REST API"""
    return {
        "waiting_list": mocker.MagicMock(),
        "start_next": mocker.MagicMock(),
        "mark_as_ready": mocker.MagicMock(),
        "mark_as_completed": mocker.MagicMock(),
    }


@pytest.fixture
async def test_app_client(
    payment_use_cases_mock: dict,
) -> AsyncGenerator[AsyncClient, None]:
    """Fixture to provide an AsyncClient for testing FastAPI endpoints"""
    app.dependency_overrides = {
        get_get_waiting_list_use_case: lambda: payment_use_cases_mock["waiting_list"],
        get_start_next_preparation_use_case: lambda: payment_use_cases_mock[
            "start_next"
        ],
        get_mark_preparation_as_ready_use_case: lambda: payment_use_cases_mock[
            "mark_as_ready"
        ],
        get_mark_preparation_as_completed_use_case: (
            lambda: payment_use_cases_mock["mark_as_completed"]
        ),
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client

    app.dependency_overrides.clear()
