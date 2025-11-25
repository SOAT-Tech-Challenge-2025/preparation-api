# pylint: disable=W0621

"""Unit tests for GetWaitingListUseCase"""

from datetime import datetime

import pytest
from pytest_mock import MockerFixture

from preparation_api.application.use_cases import GetWaitingListUseCase
from preparation_api.domain.entities import PreparationOut
from preparation_api.domain.value_objects import PreparationStatus


@pytest.fixture
def use_case(mocker: MockerFixture) -> GetWaitingListUseCase:
    """Fixture for GetWaitingListUseCase with mocked dependencies"""
    preparation_repository = mocker.Mock()
    return GetWaitingListUseCase(preparation_repository=preparation_repository)


async def test_should_return_complete_waiting_list_combining_all_statuses(
    mocker: MockerFixture,
    use_case: GetWaitingListUseCase,
):
    """Given that there are preparations in different statuses
    When executing the use case to get the waiting list
    Then all preparations should be returned in a combined list
    """

    # Given
    repository = use_case.preparation_repository
    ready_list = [
        PreparationOut(
            id="A001",
            preparation_position=1,
            preparation_time=10,
            preparation_status=PreparationStatus.READY,
            created_at=datetime(2024, 1, 1, 10, 0, 0),
            timestamp=datetime(2024, 1, 1, 10, 0, 0),
        )
    ]

    in_preparation_list = [
        PreparationOut(
            id="A002",
            preparation_position=2,
            preparation_time=15,
            preparation_status=PreparationStatus.IN_PREPARATION,
            created_at=datetime(2024, 1, 1, 10, 5, 0),
            timestamp=datetime(2024, 1, 1, 10, 5, 0),
        )
    ]

    received_list = [
        PreparationOut(
            id="A003",
            preparation_position=3,
            preparation_time=12,
            preparation_status=PreparationStatus.RECEIVED,
            created_at=datetime(2024, 1, 1, 10, 10, 0),
            timestamp=datetime(2024, 1, 1, 10, 10, 0),
        )
    ]

    repository.get_ready_waiting_list = mocker.AsyncMock(return_value=ready_list)
    repository.get_in_preparation_waiting_list = mocker.AsyncMock(
        return_value=in_preparation_list
    )

    repository.get_received_waiting_list = mocker.AsyncMock(return_value=received_list)

    # When
    waiting_list = await use_case.execute()

    # Then
    assert len(waiting_list) == 3
    assert waiting_list[0].id == "A001"
    assert waiting_list[1].id == "A002"
    assert waiting_list[2].id == "A003"
    repository.get_ready_waiting_list.assert_awaited_once_with()
    repository.get_in_preparation_waiting_list.assert_awaited_once_with()
    repository.get_received_waiting_list.assert_awaited_once_with()
