# pylint: disable=W0621

"""Unit tests for CreatePreparationFromPaymentUseCase"""

from datetime import datetime

import pytest
from pytest_mock import MockerFixture

from preparation_api.application.commands import CreatePreparationFromPaymentCommand
from preparation_api.application.use_cases import CreatePreparationFromPaymentUseCase
from preparation_api.domain.entities import PreparationIn, PreparationOut
from preparation_api.domain.value_objects import OrderInfo, PreparationStatus


@pytest.fixture
def use_case(mocker: MockerFixture) -> CreatePreparationFromPaymentUseCase:
    """Fixture for CreatePreparationFromPaymentUseCase with mocked dependencies"""
    preparation_repository = mocker.Mock()
    order_info_provider = mocker.Mock()
    return CreatePreparationFromPaymentUseCase(
        preparation_repository=preparation_repository,
        order_info_provider=order_info_provider,
    )


@pytest.fixture
def command() -> CreatePreparationFromPaymentCommand:
    """Fixture to create a sample CreatePreparationFromPaymentCommand"""
    return CreatePreparationFromPaymentCommand(payment_id="A001")


@pytest.fixture
def order_info() -> OrderInfo:
    """Fixture to create a sample OrderInfo"""
    return OrderInfo(order_id="A001", preparation_time=15)


async def test_should_create_preparation_from_payment_when_it_does_not_exist(
    mocker: MockerFixture,
    use_case: CreatePreparationFromPaymentUseCase,
    command: CreatePreparationFromPaymentCommand,
    order_info: OrderInfo,
):
    """Given a valid command to create a preparation from a payment
    When executing the use case and the preparation does not already exist
    Then a new preparation should be created and returned
    """

    # Given
    max_position = 5
    expected_position = 6
    preparation_in_mock = PreparationIn(
        id="A001",
        preparation_position=expected_position,
        preparation_time=15,
        preparation_status=PreparationStatus.RECEIVED,
    )

    preparation_out_mock = PreparationOut.model_validate(
        {
            **preparation_in_mock.model_dump(),
            "created_at": datetime(2024, 1, 1, 12, 0, 0),
            "timestamp": datetime(2024, 1, 1, 12, 0, 0),
        }
    )

    use_case.preparation_repository.exists_by_id = mocker.AsyncMock(return_value=False)
    use_case.order_info_provider.get = mocker.AsyncMock(return_value=order_info)
    use_case.preparation_repository.find_max_position = mocker.AsyncMock(
        return_value=max_position
    )

    use_case.preparation_repository.save = mocker.AsyncMock(
        return_value=preparation_out_mock
    )

    # When
    created_preparation = await use_case.execute(command=command)

    # Then
    assert created_preparation.id == command.payment_id
    assert created_preparation.preparation_position == expected_position
    assert created_preparation.preparation_time == 15
    assert created_preparation.preparation_status == PreparationStatus.RECEIVED
    assert isinstance(created_preparation.created_at, datetime)
    assert isinstance(created_preparation.timestamp, datetime)

    use_case.preparation_repository.exists_by_id.assert_awaited_once_with(
        command.payment_id
    )

    use_case.order_info_provider.get.assert_awaited_once_with(
        order_id=command.payment_id
    )

    use_case.preparation_repository.find_max_position.assert_awaited_once_with()
    use_case.preparation_repository.save.assert_awaited_once_with(
        preparation=preparation_in_mock
    )


async def test_should_not_create_preparation_when_it_already_exists(
    mocker: MockerFixture,
    use_case: CreatePreparationFromPaymentUseCase,
    command: CreatePreparationFromPaymentCommand,
):
    """Given a valid command to create a preparation from a payment
    When executing the use case and the preparation already exists
    Then a ValueError should be raised
    """

    # Given
    use_case.preparation_repository.exists_by_id = mocker.AsyncMock(return_value=True)
    use_case.order_info_provider.get = mocker.AsyncMock()
    use_case.preparation_repository.find_max_position = mocker.AsyncMock()
    use_case.preparation_repository.save = mocker.AsyncMock()

    # When / Then
    with pytest.raises(ValueError) as exc_info:
        await use_case.execute(command=command)

    assert (
        str(exc_info.value)
        == f"Preparation for payment ID {command.payment_id} already exists"
    )

    use_case.preparation_repository.exists_by_id.assert_awaited_once_with(
        command.payment_id
    )

    use_case.order_info_provider.get.assert_not_awaited()
    use_case.preparation_repository.find_max_position.assert_not_awaited()
    use_case.preparation_repository.save.assert_not_awaited()
