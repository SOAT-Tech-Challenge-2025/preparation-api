# pylint: disable=W0621

"""Unit tests for MarkPreparationAsCompletedUseCase"""

from datetime import datetime

import pytest
from pytest_mock import MockerFixture

from preparation_api.application.commands import MarkPreparationAsCompletedCommand
from preparation_api.application.use_cases import MarkPreparationAsCompletedUseCase
from preparation_api.domain.entities import PreparationIn, PreparationOut
from preparation_api.domain.exceptions import NotFound
from preparation_api.domain.value_objects import PreparationStatus


@pytest.fixture
def use_case(mocker: MockerFixture) -> MarkPreparationAsCompletedUseCase:
    """Fixture for MarkPreparationAsCompletedUseCase with mocked dependencies"""
    preparation_repository = mocker.Mock()
    return MarkPreparationAsCompletedUseCase(
        preparation_repository=preparation_repository
    )


@pytest.fixture
def command() -> MarkPreparationAsCompletedCommand:
    """Fixture to create a sample MarkPreparationAsCompletedCommand"""
    return MarkPreparationAsCompletedCommand(preparation_id="A123")


async def test_should_mark_preparation_as_completed_when_it_exists(
    mocker: MockerFixture,
    use_case: MarkPreparationAsCompletedUseCase,
    command: MarkPreparationAsCompletedCommand,
):
    """Given a valid command to mark a preparation as completed
    When executing the use case and the preparation exists and is ready
    Then the preparation should be marked as completed and returned
    """

    # Given
    found_preparation = PreparationOut(
        id="A123",
        preparation_position=1,
        preparation_time=15,
        preparation_status=PreparationStatus.READY,
        created_at=datetime(2024, 1, 1, 12, 0, 0),
        timestamp=datetime(2024, 1, 1, 12, 0, 0),
    )

    updated_preparation = PreparationOut(
        id="A123",
        preparation_position=1,
        preparation_time=15,
        preparation_status=PreparationStatus.COMPLETED,
        created_at=datetime(2024, 1, 1, 12, 0, 0),
        timestamp=datetime(2024, 1, 1, 12, 20, 0),
    )

    preparation_in_mock = PreparationIn(
        id="A123",
        preparation_position=1,
        preparation_time=15,
        preparation_status=PreparationStatus.COMPLETED,
    )

    use_case.preparation_repository.find_by_id = mocker.AsyncMock(
        return_value=found_preparation
    )

    use_case.preparation_repository.save = mocker.AsyncMock(
        return_value=updated_preparation
    )

    # When
    result_preparation = await use_case.execute(command=command)

    # Then
    assert result_preparation.id == command.preparation_id
    assert result_preparation.preparation_status == PreparationStatus.COMPLETED
    use_case.preparation_repository.find_by_id.assert_awaited_once_with(
        preparation_id=command.preparation_id
    )

    use_case.preparation_repository.save.assert_awaited_once_with(
        preparation=preparation_in_mock
    )


async def test_should_raise_value_error_when_preparation_not_found(
    mocker: MockerFixture,
    use_case: MarkPreparationAsCompletedUseCase,
    command: MarkPreparationAsCompletedCommand,
):
    """Given a valid command to mark a preparation as completed
    When executing the use case and the preparation does not exist
    Then a ValueError should be raised
    """

    # Given
    use_case.preparation_repository.find_by_id = mocker.AsyncMock(
        side_effect=NotFound("Preparation not found")
    )

    use_case.preparation_repository.save = mocker.AsyncMock()

    # When / Then
    with pytest.raises(ValueError) as exc_info:
        await use_case.execute(command=command)

    assert (
        str(exc_info.value) == f"Preparation with ID {command.preparation_id} not found"
    )

    use_case.preparation_repository.find_by_id.assert_awaited_once_with(
        preparation_id=command.preparation_id
    )

    use_case.preparation_repository.save.assert_not_awaited()
