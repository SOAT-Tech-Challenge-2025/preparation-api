# pylint: disable=W0621

"""Unit tests for preparation entity behaviors"""

from datetime import datetime

import pytest

from preparation_api.domain.entities import PreparationOut
from preparation_api.domain.value_objects import PreparationStatus


@pytest.fixture
def preparation() -> PreparationOut:
    """Fixture to create a sample PreparationOut entity"""
    return PreparationOut(
        id="A022",
        preparation_position=3,
        preparation_time=15,
        estimated_ready_time=None,
        preparation_status=PreparationStatus.RECEIVED,
        created_at=datetime(2024, 1, 1, 12, 0, 0),
        timestamp=datetime(2024, 1, 1, 12, 0, 0),
    )


def test_should_mark_as_ready_when_it_is_in_preparation(
    preparation: PreparationOut,
) -> None:
    """Given a preparation in IN_PREPARATION status,
    when marking it as ready,
    then the status should update to READY.
    """
    preparation.preparation_status = PreparationStatus.IN_PREPARATION
    updated_preparation = preparation.ready()
    assert updated_preparation.preparation_status == PreparationStatus.READY


def test_should_not_mark_as_ready_when_it_is_not_in_preparation(
    preparation: PreparationOut,
) -> None:
    """Given a preparation not in IN_PREPARATION status,
    when marking it as ready,
    then a ValueError should be raised.
    """

    preparation.preparation_status = PreparationStatus.RECEIVED

    with pytest.raises(ValueError) as exc_info:
        preparation.ready()

    assert str(exc_info.value) == (
        "A preparation with status RECEIVED cannot be marked as ready."
    )


def test_should_mark_as_completed_when_it_is_ready(
    preparation: PreparationOut,
) -> None:
    """Given a preparation in READY status,
    when marking it as completed,
    then the status should update to COMPLETED.
    """
    preparation.preparation_status = PreparationStatus.READY
    updated_preparation = preparation.complete()
    assert updated_preparation.preparation_status == PreparationStatus.COMPLETED


def test_should_not_mark_as_completed_when_it_is_not_ready(
    preparation: PreparationOut,
) -> None:
    """Given a preparation not in READY status,
    when marking it as completed,
    then a ValueError should be raised.
    """

    preparation.preparation_status = PreparationStatus.IN_PREPARATION

    with pytest.raises(ValueError) as exc_info:
        preparation.complete()

    assert str(exc_info.value) == (
        "A preparation with status IN_PREPARATION cannot be completed."
    )
