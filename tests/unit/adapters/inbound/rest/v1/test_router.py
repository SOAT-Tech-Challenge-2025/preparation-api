# pylint: disable=W0621

"""Unit tests for Preparation API v1 routes"""

from datetime import datetime

from httpx import AsyncClient
from pytest_mock import MockerFixture

from preparation_api.application.commands import (
    MarkPreparationAsCompletedCommand,
    MarkPreparationAsReadyCommand,
)
from preparation_api.domain.entities import PreparationOut
from preparation_api.domain.exceptions import PersistenceError
from preparation_api.domain.value_objects import PreparationStatus


class TestStartNextRoute:
    """Test cases for the POST /v1/preparation/start-next route"""

    async def test_should_start_next_preparation_successfully(
        self,
        test_app_client: AsyncClient,
        payment_use_cases_mock: dict,
        mocker: MockerFixture,
    ):
        """Given preparations in the waiting list
        When starting the next preparation via POST endpoint
        Then the preparation should be started and returned with status 200
        """

        # Given
        expected_preparation = PreparationOut(
            id="A001",
            preparation_position=None,
            preparation_time=15,
            estimated_ready_time=datetime(2025, 11, 26, 14, 30, 0),
            preparation_status=PreparationStatus.IN_PREPARATION,
            created_at=datetime(2025, 11, 26, 14, 0, 0),
            timestamp=datetime(2025, 11, 26, 14, 15, 0),
        )

        payment_use_cases_mock["start_next"].execute = mocker.AsyncMock(
            return_value=expected_preparation
        )

        # When
        response = await test_app_client.post("/v1/preparation/start-next")

        # Then
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["id"] == "A001"
        assert (
            response_data["preparation_status"]
            == PreparationStatus.IN_PREPARATION.value
        )
        assert response_data["preparation_time"] == 15
        payment_use_cases_mock["start_next"].execute.assert_awaited_once()

    async def test_should_return_400_when_no_preparations_in_waiting_list(
        self,
        test_app_client: AsyncClient,
        payment_use_cases_mock: dict,
        mocker: MockerFixture,
    ):
        """Given no preparations in the waiting list
        When starting the next preparation via POST endpoint
        Then a 400 error should be returned
        """

        # Given
        error_message = "No preparations available in the waiting list"
        payment_use_cases_mock["start_next"].execute = mocker.AsyncMock(
            side_effect=ValueError(error_message)
        )

        # When
        response = await test_app_client.post("/v1/preparation/start-next")

        # Then
        assert response.status_code == 400
        assert response.json()["detail"] == error_message
        payment_use_cases_mock["start_next"].execute.assert_awaited_once()

    async def test_should_return_500_when_persistence_error_occurs(
        self,
        test_app_client: AsyncClient,
        payment_use_cases_mock: dict,
        mocker: MockerFixture,
    ):
        """Given a persistence error occurs
        When starting the next preparation via POST endpoint
        Then a 500 error should be returned
        """

        # Given
        payment_use_cases_mock["start_next"].execute = mocker.AsyncMock(
            side_effect=PersistenceError("Database connection failed")
        )

        # When
        response = await test_app_client.post("/v1/preparation/start-next")

        # Then
        assert response.status_code == 500
        assert response.json()["detail"] == "Internal server error"
        payment_use_cases_mock["start_next"].execute.assert_awaited_once()


class TestMarkAsReadyRoute:
    """Test cases for the POST /v1/preparation/{preparation_id}/ready route"""

    async def test_should_mark_preparation_as_ready_successfully(
        self,
        test_app_client: AsyncClient,
        payment_use_cases_mock: dict,
        mocker: MockerFixture,
    ):
        """Given a valid preparation ID in preparation status
        When marking as ready via POST endpoint
        Then the preparation should be marked as ready and returned with status 200
        """

        # Given
        preparation_id = "A001"
        expected_preparation = PreparationOut(
            id=preparation_id,
            preparation_position=None,
            preparation_time=15,
            estimated_ready_time=None,
            preparation_status=PreparationStatus.READY,
            created_at=datetime(2025, 11, 26, 14, 0, 0),
            timestamp=datetime(2025, 11, 26, 14, 30, 0),
        )

        payment_use_cases_mock["mark_as_ready"].execute = mocker.AsyncMock(
            return_value=expected_preparation
        )

        # When
        response = await test_app_client.post(f"/v1/preparation/{preparation_id}/ready")

        # Then
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["id"] == preparation_id
        assert response_data["preparation_status"] == PreparationStatus.READY.value
        expected_command = MarkPreparationAsReadyCommand(preparation_id=preparation_id)
        payment_use_cases_mock["mark_as_ready"].execute.assert_awaited_once_with(
            expected_command
        )

    async def test_should_return_400_when_preparation_cannot_be_marked_as_ready(
        self,
        test_app_client: AsyncClient,
        payment_use_cases_mock: dict,
        mocker: MockerFixture,
    ):
        """Given a preparation with invalid status
        When marking as ready via POST endpoint
        Then a 400 error should be returned
        """

        # Given
        preparation_id = "A001"
        error_message = (
            f"A preparation with status {PreparationStatus.RECEIVED.value} "
            "cannot be marked as ready."
        )
        payment_use_cases_mock["mark_as_ready"].execute = mocker.AsyncMock(
            side_effect=ValueError(error_message)
        )

        # When
        response = await test_app_client.post(f"/v1/preparation/{preparation_id}/ready")

        # Then
        assert response.status_code == 400
        assert response.json()["detail"] == error_message
        expected_command = MarkPreparationAsReadyCommand(preparation_id=preparation_id)
        payment_use_cases_mock["mark_as_ready"].execute.assert_awaited_once_with(
            expected_command
        )

    async def test_should_return_500_when_persistence_error_occurs_marking_ready(
        self,
        test_app_client: AsyncClient,
        payment_use_cases_mock: dict,
        mocker: MockerFixture,
    ):
        """Given a persistence error occurs
        When marking as ready via POST endpoint
        Then a 500 error should be returned
        """

        # Given
        preparation_id = "A001"
        payment_use_cases_mock["mark_as_ready"].execute = mocker.AsyncMock(
            side_effect=PersistenceError("Database connection failed")
        )

        # When
        response = await test_app_client.post(f"/v1/preparation/{preparation_id}/ready")

        # Then
        assert response.status_code == 500
        assert response.json()["detail"] == "Internal server error"
        expected_command = MarkPreparationAsReadyCommand(preparation_id=preparation_id)
        payment_use_cases_mock["mark_as_ready"].execute.assert_awaited_once_with(
            expected_command
        )


class TestMarkAsCompletedRoute:
    """Test cases for the POST /v1/preparation/{preparation_id}/complete route"""

    async def test_should_mark_preparation_as_completed_successfully(
        self,
        test_app_client: AsyncClient,
        payment_use_cases_mock: dict,
        mocker: MockerFixture,
    ):
        """Given a valid preparation ID in ready status
        When marking as completed via POST endpoint
        Then the preparation should be marked as completed and returned with status 200
        """

        # Given
        preparation_id = "A001"
        expected_preparation = PreparationOut(
            id=preparation_id,
            preparation_position=None,
            preparation_time=15,
            estimated_ready_time=None,
            preparation_status=PreparationStatus.COMPLETED,
            created_at=datetime(2025, 11, 26, 14, 0, 0),
            timestamp=datetime(2025, 11, 26, 14, 45, 0),
        )

        payment_use_cases_mock["mark_as_completed"].execute = mocker.AsyncMock(
            return_value=expected_preparation
        )

        # When
        response = await test_app_client.post(
            f"/v1/preparation/{preparation_id}/complete"
        )

        # Then
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["id"] == preparation_id
        assert response_data["preparation_status"] == PreparationStatus.COMPLETED.value
        expected_command = MarkPreparationAsCompletedCommand(
            preparation_id=preparation_id
        )
        payment_use_cases_mock["mark_as_completed"].execute.assert_awaited_once_with(
            expected_command
        )

    async def test_should_return_400_when_preparation_cannot_be_completed(
        self,
        test_app_client: AsyncClient,
        payment_use_cases_mock: dict,
        mocker: MockerFixture,
    ):
        """Given a preparation with invalid status
        When marking as completed via POST endpoint
        Then a 400 error should be returned
        """

        # Given
        preparation_id = "A001"
        error_message = (
            f"A preparation with status {PreparationStatus.IN_PREPARATION.value} "
            "cannot be completed."
        )

        payment_use_cases_mock["mark_as_completed"].execute = mocker.AsyncMock(
            side_effect=ValueError(error_message)
        )

        # When
        response = await test_app_client.post(
            f"/v1/preparation/{preparation_id}/complete"
        )

        # Then
        assert response.status_code == 400
        assert response.json()["detail"] == error_message
        expected_command = MarkPreparationAsCompletedCommand(
            preparation_id=preparation_id
        )
        payment_use_cases_mock["mark_as_completed"].execute.assert_awaited_once_with(
            expected_command
        )

    async def test_should_return_500_when_persistence_error_occurs_marking_completed(
        self,
        test_app_client: AsyncClient,
        payment_use_cases_mock: dict,
        mocker: MockerFixture,
    ):
        """Given a persistence error occurs
        When marking as completed via POST endpoint
        Then a 500 error should be returned
        """

        # Given
        preparation_id = "A001"
        payment_use_cases_mock["mark_as_completed"].execute = mocker.AsyncMock(
            side_effect=PersistenceError("Database connection failed")
        )

        # When
        response = await test_app_client.post(
            f"/v1/preparation/{preparation_id}/complete"
        )

        # Then
        assert response.status_code == 500
        assert response.json()["detail"] == "Internal server error"
        expected_command = MarkPreparationAsCompletedCommand(
            preparation_id=preparation_id
        )
        payment_use_cases_mock["mark_as_completed"].execute.assert_awaited_once_with(
            expected_command
        )


class TestGetWaitingListRoute:
    """Test cases for the GET /v1/preparation/waiting-list route"""

    async def test_should_return_waiting_list_successfully(
        self,
        test_app_client: AsyncClient,
        payment_use_cases_mock: dict,
        mocker: MockerFixture,
    ):
        """Given preparations in the waiting list
        When retrieving the waiting list via GET endpoint
        Then the list should be returned with status 200
        """

        # Given
        preparation1 = PreparationOut(
            id="A001",
            preparation_position=1,
            preparation_time=15,
            estimated_ready_time=None,
            preparation_status=PreparationStatus.RECEIVED,
            created_at=datetime(2025, 11, 26, 14, 0, 0),
            timestamp=datetime(2025, 11, 26, 14, 0, 0),
        )
        preparation2 = PreparationOut(
            id="A002",
            preparation_position=2,
            preparation_time=20,
            estimated_ready_time=None,
            preparation_status=PreparationStatus.RECEIVED,
            created_at=datetime(2025, 11, 26, 14, 5, 0),
            timestamp=datetime(2025, 11, 26, 14, 5, 0),
        )

        expected_preparations = [preparation1, preparation2]
        payment_use_cases_mock["waiting_list"].execute = mocker.AsyncMock(
            return_value=expected_preparations
        )

        # When
        response = await test_app_client.get("/v1/preparation/waiting-list")

        # Then
        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data["items"]) == 2
        assert response_data["items"][0]["id"] == "A001"
        assert response_data["items"][1]["id"] == "A002"
        assert response_data["items"][0]["preparation_position"] == 1
        assert response_data["items"][1]["preparation_position"] == 2
        payment_use_cases_mock["waiting_list"].execute.assert_awaited_once()

    async def test_should_return_empty_waiting_list(
        self,
        test_app_client: AsyncClient,
        payment_use_cases_mock: dict,
        mocker: MockerFixture,
    ):
        """Given no preparations in the waiting list
        When retrieving the waiting list via GET endpoint
        Then an empty list should be returned with status 200
        """

        # Given
        payment_use_cases_mock["waiting_list"].execute = mocker.AsyncMock(
            return_value=[]
        )

        # When
        response = await test_app_client.get("/v1/preparation/waiting-list")

        # Then
        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data["items"]) == 0
        payment_use_cases_mock["waiting_list"].execute.assert_awaited_once()

    async def test_should_return_500_when_persistence_error_occurs_getting_waiting_list(
        self,
        test_app_client: AsyncClient,
        payment_use_cases_mock: dict,
        mocker: MockerFixture,
    ):
        """Given a persistence error occurs
        When retrieving the waiting list via GET endpoint
        Then a 500 error should be returned
        """

        # Given
        payment_use_cases_mock["waiting_list"].execute = mocker.AsyncMock(
            side_effect=PersistenceError("Database connection failed")
        )

        # When
        response = await test_app_client.get("/v1/preparation/waiting-list")

        # Then
        assert response.status_code == 500
        assert response.json()["detail"] == "Internal server error"
        payment_use_cases_mock["waiting_list"].execute.assert_awaited_once()
