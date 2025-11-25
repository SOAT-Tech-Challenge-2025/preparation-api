# pylint: disable=W0621

"""Unit tests for StartNextPreparationUseCase"""

from datetime import datetime, timezone

import pytest
from freezegun import freeze_time
from pytest_mock import MockerFixture

from preparation_api.application.use_cases import StartNextPreparationUseCase
from preparation_api.domain.entities import PreparationIn, PreparationOut
from preparation_api.domain.exceptions import NotFound
from preparation_api.domain.value_objects import PreparationStatus


@pytest.fixture
def use_case(mocker: MockerFixture) -> StartNextPreparationUseCase:
    """Fixture for StartNextPreparationUseCase with mocked dependencies"""
    preparation_repository = mocker.Mock()
    return StartNextPreparationUseCase(preparation_repository=preparation_repository)


@freeze_time("2024-01-01T12:00:00Z")
async def test_should_start_next_preparation_when_received_preparation_exists(
    mocker: MockerFixture,
    use_case: StartNextPreparationUseCase,
):
    """Given that there is a received preparation with minimum position
    When executing the use case to start the next preparation
    Then the preparation should be started and positions should be decremented
    """

    # Given
    found_preparation = PreparationOut(
        id="A123",
        preparation_position=1,
        preparation_time=15,
        preparation_status=PreparationStatus.RECEIVED,
        created_at=datetime(2024, 1, 1, 12, 0, 0),
        timestamp=datetime(2024, 1, 1, 12, 0, 0),
    )

    updated_preparation = PreparationOut(
        id="A123",
        preparation_position=None,
        preparation_time=15,
        estimated_ready_time=datetime(2024, 1, 1, 12, 15, 0),
        preparation_status=PreparationStatus.IN_PREPARATION,
        created_at=datetime(2024, 1, 1, 12, 0, 0),
        timestamp=datetime(2024, 1, 1, 12, 5, 0),
    )

    preparation_in_mock = PreparationIn(
        id="A123",
        preparation_position=None,
        preparation_time=15,
        estimated_ready_time=datetime(2024, 1, 1, 12, 15, 0, tzinfo=timezone.utc),
        preparation_status=PreparationStatus.IN_PREPARATION,
    )

    repository = use_case.preparation_repository
    repository.find_received_with_min_position = mocker.AsyncMock(
        return_value=found_preparation
    )

    repository.save = mocker.AsyncMock(return_value=updated_preparation)
    repository.decrement_received_positions_greater_than = mocker.AsyncMock()

    # When
    result_preparation = await use_case.execute()

    # Then
    assert result_preparation.id == "A123"
    assert result_preparation.preparation_status == PreparationStatus.IN_PREPARATION
    assert result_preparation.preparation_position is None
    repository.find_received_with_min_position.assert_awaited_once_with()
    repository.save.assert_awaited_once_with(preparation=preparation_in_mock)
    repository.decrement_received_positions_greater_than.assert_awaited_once_with(
        preparation_position=1
    )


async def test_should_raise_value_error_when_no_received_preparation_found(
    mocker: MockerFixture,
    use_case: StartNextPreparationUseCase,
):
    """Given that there are no received preparations to start
    When executing the use case to start the next preparation
    Then a ValueError should be raised
    """

    # Given
    repository = use_case.preparation_repository

    repository.find_received_with_min_position = mocker.AsyncMock(
        side_effect=NotFound("No received preparation found")
    )

    repository.save = mocker.AsyncMock()
    repository.decrement_received_positions_greater_than = mocker.AsyncMock()

    # When / Then
    with pytest.raises(ValueError) as exc_info:
        await use_case.execute()

    assert str(exc_info.value) == "No received preparation found to start"

    repository.find_received_with_min_position.assert_awaited_once_with()
    repository.save.assert_not_awaited()
    repository.decrement_received_positions_greater_than.assert_not_awaited()
