# pylint: disable=W0621

"""Unit tests for OrderInfoProvider adapter"""

import pytest
from httpx import HTTPStatusError, Request
from pytest_mock import MockerFixture

from preparation_api.adapters.out import APIOrderInfoProvider
from preparation_api.domain.exceptions import OrderInfoProviderError
from preparation_api.domain.value_objects import OrderInfo


@pytest.fixture
def order_api_settings(mocker: MockerFixture):
    """Fixture to create a mock OrderAPISettings for testing"""
    mock_settings = mocker.Mock()
    mock_settings.BASE_URL = "http://order-api.service.local"
    return mock_settings


@pytest.fixture
def client(mocker: MockerFixture, order_api_settings) -> APIOrderInfoProvider:
    """Fixture to create APIOrderInfoProvider with mocked dependencies"""
    http_client = mocker.Mock()
    return APIOrderInfoProvider(settings=order_api_settings, http_client=http_client)


async def test_should_get_order_info_when_order_api_responds_successfully(
    mocker: MockerFixture,
    client: APIOrderInfoProvider,
):
    """Given the Order API responds successfully
    When fetching order info
    Then it should return the correct OrderInfo object
    """

    # Given
    order_id = "A001"
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "orderId": "A001",
        "totalOrder": 90.0,
        "preparationTime": 10,
        "clientId": "123e4567-e89b-12d3-a456-426614174000",
        "timestamp": "2025-05-30T01:18:06.339+00:00",
        "products": [
            {"productId": 1, "quantity": 1, "vlUnitProduct": 50.0},
            {"productId": 2, "quantity": 2, "vlUnitProduct": 20.0},
        ],
    }

    client.http_client.get = mocker.AsyncMock(return_value=mock_response)

    # When
    order_info = await client.get(order_id)

    # Then
    expected_order_info = OrderInfo(order_id=order_id, preparation_time=10)
    assert order_info == expected_order_info
    client.http_client.get.assert_awaited_once_with(
        f"{client.base_url}/order/{order_id}"
    )


async def test_should_raise_order_info_provider_error_when_order_api_responds_with_error(  # noqa: E501
    mocker: MockerFixture,
    client: APIOrderInfoProvider,
):
    """Given the Order API responds with an error
    When fetching order info
    Then it should raise OrderInfoProviderError
    """

    # Given
    order_id = "A002"
    mock_request = Request("GET", f"{client.base_url}/order/{order_id}")
    mock_exception = HTTPStatusError(
        message="Not Found",
        request=mock_request,
        response=mocker.Mock(status_code=404),
    )

    client.http_client.get = mocker.AsyncMock(side_effect=mock_exception)

    # When / Then
    with pytest.raises(OrderInfoProviderError) as exc_info:
        await client.get(order_id)

    assert "Failed to make GET request to Order API" in str(exc_info.value)
    client.http_client.get.assert_awaited_once_with(
        f"{client.base_url}/order/{order_id}"
    )
