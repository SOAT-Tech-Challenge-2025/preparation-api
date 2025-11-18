# pylint: disable=W0621

"""Test for SQL Alchemy Preparation Repository implementation"""

from datetime import datetime

import pytest
from pytest_mock import MockerFixture
from sqlalchemy import insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from preparation_api.adapters.out import SAPreparationRepository
from preparation_api.domain.entities import PreparationIn, PreparationOut
from preparation_api.domain.exceptions import NotFound, PersistenceError
from preparation_api.domain.value_objects import PreparationStatus
from preparation_api.infrastructure.orm.models import Preparation as PreparationModel


@pytest.fixture(autouse=True)
async def create_scenario(db_session: AsyncSession):
    """Fixture to create test scenario before each test"""
    preparations = [
        {
            "id": "A008",
            "preparation_position": 3,
            "preparation_time": 15,
            "estimated_ready_time": None,
            "preparation_status": PreparationStatus.RECEIVED,
            "created_at": datetime(2023, 1, 1, 0, 28, 0),
            "timestamp": datetime(2023, 1, 1, 0, 28, 0),
        },
        {
            "id": "A007",
            "preparation_position": 2,
            "preparation_time": 8,
            "estimated_ready_time": None,
            "preparation_status": PreparationStatus.RECEIVED,
            "created_at": datetime(2023, 1, 1, 0, 27, 0),
            "timestamp": datetime(2023, 1, 1, 0, 27, 0),
        },
        {
            "id": "A006",
            "preparation_position": 1,
            "preparation_time": 10,
            "estimated_ready_time": None,
            "preparation_status": PreparationStatus.RECEIVED,
            "created_at": datetime(2023, 1, 1, 0, 26, 0),
            "timestamp": datetime(2023, 1, 1, 0, 26, 0),
        },
        {
            "id": "A005",
            "preparation_position": None,
            "preparation_time": 5,
            "estimated_ready_time": datetime(2023, 1, 1, 0, 32, 0),
            "preparation_status": PreparationStatus.IN_PREPARATION,
            "created_at": datetime(2023, 1, 1, 0, 25, 0),
            "timestamp": datetime(2023, 1, 1, 0, 27, 0),
        },
        {
            "id": "A004",
            "preparation_position": None,
            "preparation_time": 5,
            "estimated_ready_time": datetime(2023, 1, 1, 0, 30, 0),
            "preparation_status": PreparationStatus.IN_PREPARATION,
            "created_at": datetime(2023, 1, 1, 0, 22, 0),
            "timestamp": datetime(2023, 1, 1, 0, 25, 0),
        },
        {
            "id": "A003",
            "preparation_position": None,
            "preparation_time": 5,
            "estimated_ready_time": None,
            "preparation_status": PreparationStatus.READY,
            "created_at": datetime(2023, 1, 1, 0, 20, 0),
            "timestamp": datetime(2023, 1, 1, 0, 30, 0),
        },
        {
            "id": "A002",
            "preparation_position": None,
            "preparation_time": 5,
            "estimated_ready_time": None,
            "preparation_status": PreparationStatus.READY,
            "created_at": datetime(2023, 1, 1, 0, 2, 0),
            "timestamp": datetime(2023, 1, 1, 0, 10, 0),
        },
        {
            "id": "A001",
            "preparation_position": None,
            "preparation_time": 8,
            "estimated_ready_time": None,
            "preparation_status": PreparationStatus.COMPLETED,
            "created_at": datetime(2023, 1, 1, 0, 0, 0),
            "timestamp": datetime(2023, 1, 1, 0, 10, 0),
        },
    ]

    await db_session.execute(insert(PreparationModel), preparations)
    await db_session.commit()


@pytest.fixture
def repository(db_session: AsyncSession) -> SAPreparationRepository:
    """Fixture to create an instance of SAPreparationRepository"""
    return SAPreparationRepository(session=db_session)


async def test_should_insert_new_preparation_when_preparation_does_not_exist(
    repository: SAPreparationRepository,
):
    """Given a preparation that does not exist
    When calling the repository to save a preparation
    Then it should insert the new preparation with correct attributes
    """

    # Given
    preparation_in = PreparationIn(
        id="A009",
        preparation_position=4,
        preparation_time=12,
        preparation_status=PreparationStatus.RECEIVED,
    )

    # When
    preparation = await repository.save(preparation=preparation_in)

    # Then
    assert preparation.id == "A009"
    assert preparation.preparation_time == 12
    assert preparation.preparation_status == PreparationStatus.RECEIVED
    assert preparation.preparation_position == 4


async def test_should_update_existing_preparation_when_preparation_exists(
    repository: SAPreparationRepository,
):
    """Given a preparation that exists
    When calling the repository to save a preparation
    Then it should update the existing preparation with new attributes
    """

    # Given
    preparation_in = PreparationIn(
        id="A008",
        preparation_time=20,
        preparation_status=PreparationStatus.IN_PREPARATION,
        estimated_ready_time=datetime(2023, 1, 1, 0, 45, 0),
    )

    # When
    preparation = await repository.save(preparation=preparation_in)

    # Then
    assert preparation.id == "A008"
    assert preparation.preparation_time == 20
    assert preparation.preparation_status == PreparationStatus.IN_PREPARATION
    assert preparation.estimated_ready_time == datetime(2023, 1, 1, 0, 45, 0)


async def test_should_raise_persistence_error_on_insert_db_issue(
    mocker: MockerFixture,
    repository: SAPreparationRepository,
):
    """Given a database issue
    When calling the repository to save a preparation
    Then it should raise a PersistenceError
    """

    # Given
    preparation_in = PreparationIn(
        id="A010",
        preparation_position=5,
        preparation_time=15,
        preparation_status=PreparationStatus.RECEIVED,
    )

    # Mock exists_by_id to return False (so it tries to insert)
    mocker.patch.object(repository, "exists_by_id", return_value=False)
    mocker.patch.object(
        repository.session,
        "execute",
        side_effect=SQLAlchemyError("Insert constraint violation"),
    )

    # When / Then
    with pytest.raises(PersistenceError) as exc_info:
        await repository.save(preparation=preparation_in)

    assert "Insert constraint violation" in str(exc_info.value)


async def test_should_raise_persistence_error_on_update_db_issue(
    mocker: MockerFixture,
    repository: SAPreparationRepository,
):
    """Given a database issue
    When calling the repository to update a preparation
    Then it should raise a PersistenceError
    """

    # Given
    preparation_in = PreparationIn(
        id="A008",
        preparation_time=20,
        preparation_status=PreparationStatus.IN_PREPARATION,
        estimated_ready_time=datetime(2023, 1, 1, 0, 45, 0),
    )

    # Mock exists_by_id to return True (so it tries to update)
    mocker.patch.object(repository, "exists_by_id", return_value=True)
    mocker.patch.object(
        repository.session,
        "execute",
        side_effect=SQLAlchemyError("Update constraint violation"),
    )

    # When / Then
    with pytest.raises(PersistenceError) as exc_info:
        await repository.save(preparation=preparation_in)

    assert "Update constraint violation" in str(exc_info.value)


async def test_should_return_preparation_by_id(repository: SAPreparationRepository):
    """Given an existing preparation ID
    When calling the repository to get the preparation by ID
    Then the preparation with the given ID should be returned in domain format
    """

    # Given
    preparation_id = "A007"

    # When
    preparation = await repository.find_by_id(preparation_id=preparation_id)

    # Then
    assert preparation == PreparationOut(
        id="A007",
        preparation_position=2,
        preparation_time=8,
        estimated_ready_time=None,
        preparation_status=PreparationStatus.RECEIVED,
        created_at=datetime(2023, 1, 1, 0, 27, 0),
        timestamp=datetime(2023, 1, 1, 0, 27, 0),
    )


async def test_should_raise_not_found_when_preparation_id_does_not_exist(
    repository: SAPreparationRepository,
):
    """Given a non-existing preparation ID
    When calling the repository to get the preparation by ID
    Then it should raise a NotFound exception
    """

    # Given
    preparation_id = "NON_EXISTENT_ID"

    # When / Then
    with pytest.raises(NotFound) as exc_info:
        await repository.find_by_id(preparation_id=preparation_id)

    assert f"No preparation found with ID: {preparation_id}" in str(exc_info.value)


async def test_should_raise_persistence_error_on_db_issue_when_finding_preparation(
    mocker: MockerFixture,
    repository: SAPreparationRepository,
):
    """Given a database issue
    When calling the repository to get the preparation by ID
    Then it should raise a PersistenceError
    """

    # Given
    preparation_id = "A008"

    mocker.patch.object(
        repository.session,
        "execute",
        side_effect=SQLAlchemyError("DB connection error"),
    )

    # When / Then
    with pytest.raises(PersistenceError) as exc_info:
        await repository.find_by_id(preparation_id=preparation_id)

    assert (
        f"Error finding preparation by ID {preparation_id}: DB connection error"
        in str(exc_info.value)
    )


async def test_should_return_true_when_preparation_exists_by_id(
    repository: SAPreparationRepository,
):
    """Given an existing preparation id
    When calling the repository to check if preparation exists by id
    Then True should be returned
    """

    # Given
    preparation_id = "A001"

    # When
    exists = await repository.exists_by_id(preparation_id=preparation_id)

    # Then
    assert exists is True


async def test_should_return_false_when_preparation_does_not_exist_by_id(
    repository: SAPreparationRepository,
):
    """Given a non-existing preparation id
    When calling the repository to check if preparation exists by id
    Then False should be returned
    """

    # Given
    preparation_id = "NON_EXISTING_ID"

    # When
    exists = await repository.exists_by_id(preparation_id=preparation_id)

    # Then
    assert exists is False


async def test_should_raise_persistence_error_on_exists_by_id_db_issue(
    mocker: MockerFixture,
    repository: SAPreparationRepository,
):
    """Given a database issue
    When calling the repository to check if preparation exists by id
    Then a PersistenceError should be raised
    """

    # Given
    preparation_id = "A001"

    mocker.patch.object(
        repository.session,
        "execute",
        side_effect=SQLAlchemyError("Simulated database error"),
    )

    # When / Then
    with pytest.raises(PersistenceError) as exc_info:
        await repository.exists_by_id(preparation_id=preparation_id)

    assert "Simulated database error" in str(exc_info.value)


async def test_should_return_max_preparation_position(
    repository: SAPreparationRepository,
):
    """Given existing preparations with positions
    When calling the repository to get the max preparation position
    Then the correct max preparation position with status RECEIVED should be returned
    """

    # When
    max_position = await repository.find_max_position()

    # Then
    assert max_position == 3


async def test_should_raise_persistence_error_on_db_issue_when_finding_max_position(
    mocker: MockerFixture,
    repository: SAPreparationRepository,
):
    """Given a database issue
    When calling the repository to get the max preparation position
    Then a PersistenceError should be raised
    """

    # Given
    mocker.patch.object(
        repository.session,
        "execute",
        side_effect=SQLAlchemyError("Simulated database error"),
    )

    # When / Then
    with pytest.raises(PersistenceError) as exc_info:
        await repository.find_max_position()

    assert "Simulated database error" in str(exc_info.value)


async def test_should_return_received_preparation_with_min_position(
    repository: SAPreparationRepository,
):
    """Given existing preparations with RECEIVED status
    When calling the repository to get the received preparation with min position
    Then the first preparation in the queue should be returned
    """

    # When
    preparation = await repository.find_received_with_min_position()

    # Then
    assert preparation == PreparationOut(
        id="A006",
        preparation_position=1,
        preparation_time=10,
        estimated_ready_time=None,
        preparation_status=PreparationStatus.RECEIVED,
        created_at=datetime(2023, 1, 1, 0, 26, 0),
        timestamp=datetime(2023, 1, 1, 0, 26, 0),
    )


async def test_should_raise_not_found_error_when_no_received_preparation_exists(
    repository: SAPreparationRepository,
):
    """Given no preparations with RECEIVED status
    When calling the repository to get the received preparation with min position
    Then a NotFound error should be raised
    """

    # Given
    # First, update all RECEIVED preparations to a different status
    preparations = await repository.get_received_waiting_list()
    for prep in preparations:
        prep_in = PreparationIn.model_validate(prep)
        prep_in.preparation_status = PreparationStatus.IN_PREPARATION
        await repository.save(preparation=prep_in)

    # When / Then
    with pytest.raises(NotFound) as exc_info:
        await repository.find_received_with_min_position()

    assert "No received preparation found" in str(exc_info.value)


async def test_should_raise_persistence_error_on_db_issue_when_finding_received_with_min_position(  # noqa: E501
    mocker: MockerFixture,
    repository: SAPreparationRepository,
):
    """Given a database issue
    When calling the repository to get the received preparation with min position
    Then a PersistenceError should be raised
    """

    # Given
    mocker.patch.object(
        repository.session,
        "execute",
        side_effect=SQLAlchemyError("Simulated database error"),
    )

    # When / Then
    with pytest.raises(PersistenceError) as exc_info:
        await repository.find_received_with_min_position()

    assert "Simulated database error" in str(exc_info.value)


async def test_should_decrement_positions_greater_than_given_position(
    repository: SAPreparationRepository,
):
    """Given existing preparations with positions
    When calling the repository to decrement positions greater than a given position
    Then the positions of the affected preparations should be decremented by 1
    """

    # Given
    position_to_decrement = 1

    # When
    await repository.decrement_received_positions_greater_than(
        preparation_position=position_to_decrement
    )

    # Then
    preparations = await repository.get_received_waiting_list()
    positions = {p.id: p.preparation_position for p in preparations}

    assert positions == {
        "A006": 1,  # Unchanged because it will disappear from this query after the use
        # case updates its status to IN_PREPARATION
        "A007": 1,  # This passed from 2 to 1
        "A008": 2,  # And this from 3 to 2
    }


async def test_should_raise_persistence_error_on_db_issue_when_decrementing_positions(
    mocker: MockerFixture,
    repository: SAPreparationRepository,
):
    """Given a database issue
    When calling the repository to decrement positions
    Then a PersistenceError should be raised
    """

    # Given
    mocker.patch.object(
        repository.session,
        "execute",
        side_effect=SQLAlchemyError("Simulated database error"),
    )

    # When / Then
    with pytest.raises(PersistenceError) as exc_info:
        await repository.decrement_received_positions_greater_than(
            preparation_position=1
        )

    assert "Simulated database error" in str(exc_info.value)


async def get_received_waiting_list(
    repository: SAPreparationRepository,
):
    """Given existing preparations with RECEIVED status
    When calling the repository to get the received waiting list
    Then the correct list of preparations should be returned ordered by position
    """

    # When
    preparations = await repository.get_received_waiting_list()

    # Then
    assert preparations == [
        PreparationOut(
            id="A006",
            preparation_position=1,
            preparation_time=10,
            estimated_ready_time=None,
            preparation_status=PreparationStatus.RECEIVED,
            created_at=datetime(2023, 1, 1, 0, 26, 0),
            timestamp=datetime(2023, 1, 1, 0, 26, 0),
        ),
        PreparationOut(
            id="A007",
            preparation_position=2,
            preparation_time=8,
            estimated_ready_time=None,
            preparation_status=PreparationStatus.RECEIVED,
            created_at=datetime(2023, 1, 1, 0, 27, 0),
            timestamp=datetime(2023, 1, 1, 0, 27, 0),
        ),
        PreparationOut(
            id="A008",
            preparation_position=3,
            preparation_time=15,
            estimated_ready_time=None,
            preparation_status=PreparationStatus.RECEIVED,
            created_at=datetime(2023, 1, 1, 0, 28, 0),
            timestamp=datetime(2023, 1, 1, 0, 28, 0),
        ),
    ]


async def test_should_raise_persistence_error_on_db_issue_when_getting_received_waiting_list(  # noqa: E501
    mocker: MockerFixture,
    repository: SAPreparationRepository,
):
    """Given a database issue
    When calling the repository to get the received waiting list
    Then a PersistenceError should be raised
    """

    # Given
    mocker.patch.object(
        repository.session,
        "execute",
        side_effect=SQLAlchemyError("Simulated database error"),
    )

    # When / Then
    with pytest.raises(PersistenceError) as exc_info:
        await repository.get_received_waiting_list()

    assert "Simulated database error" in str(exc_info.value)


async def test_should_return_in_preparation_waiting_list(
    repository: SAPreparationRepository,
):
    """Given existing preparations with IN_PREPARATION status

    When calling the repository to get the in preparation waiting list

    Then the correct list of preparations should be returned ordered by estimated
    ready time
    """

    # When
    preparations = await repository.get_in_preparation_waiting_list()

    # Then
    assert preparations == [
        PreparationOut(
            id="A004",
            preparation_position=None,
            preparation_time=5,
            estimated_ready_time=datetime(2023, 1, 1, 0, 30, 0),
            preparation_status=PreparationStatus.IN_PREPARATION,
            created_at=datetime(2023, 1, 1, 0, 22, 0),
            timestamp=datetime(2023, 1, 1, 0, 25, 0),
        ),
        PreparationOut(
            id="A005",
            preparation_position=None,
            preparation_time=5,
            estimated_ready_time=datetime(2023, 1, 1, 0, 32, 0),
            preparation_status=PreparationStatus.IN_PREPARATION,
            created_at=datetime(2023, 1, 1, 0, 25, 0),
            timestamp=datetime(2023, 1, 1, 0, 27, 0),
        ),
    ]


async def test_should_raise_persistence_error_on_db_issue_when_getting_in_preparation_waiting_list(  # noqa: E501
    mocker: MockerFixture,
    repository: SAPreparationRepository,
):
    """Given a database issue
    When calling the repository to get the in preparation waiting list
    Then a PersistenceError should be raised
    """

    # Given
    mocker.patch.object(
        repository.session,
        "execute",
        side_effect=SQLAlchemyError("Simulated database error"),
    )

    # When / Then
    with pytest.raises(PersistenceError) as exc_info:
        await repository.get_in_preparation_waiting_list()

    assert "Simulated database error" in str(exc_info.value)


async def test_should_return_ready_waiting_list(
    repository: SAPreparationRepository,
):
    """Given existing preparations with READY status
    When calling the repository to get the ready waiting list
    Then the correct list of preparations should be returned ordered by created_at
    """

    # When
    preparations = await repository.get_ready_waiting_list()

    # Then
    assert preparations == [
        PreparationOut(
            id="A002",
            preparation_position=None,
            preparation_time=5,
            estimated_ready_time=None,
            preparation_status=PreparationStatus.READY,
            created_at=datetime(2023, 1, 1, 0, 2, 0),
            timestamp=datetime(2023, 1, 1, 0, 10, 0),
        ),
        PreparationOut(
            id="A003",
            preparation_position=None,
            preparation_time=5,
            estimated_ready_time=None,
            preparation_status=PreparationStatus.READY,
            created_at=datetime(2023, 1, 1, 0, 20, 0),
            timestamp=datetime(2023, 1, 1, 0, 30, 0),
        ),
    ]


async def test_should_raise_persistence_error_on_db_issue_when_getting_ready_waiting_list(  # noqa: E501
    mocker: MockerFixture,
    repository: SAPreparationRepository,
):
    """Given a database issue
    When calling the repository to get the ready waiting list
    Then a PersistenceError should be raised
    """

    # Given
    mocker.patch.object(
        repository.session,
        "execute",
        side_effect=SQLAlchemyError("Simulated database error"),
    )

    # When / Then
    with pytest.raises(PersistenceError) as exc_info:
        await repository.get_ready_waiting_list()

    assert "Simulated database error" in str(exc_info.value)
