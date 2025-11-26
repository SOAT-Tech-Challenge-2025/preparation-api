"""Factory module for manual dependency injection"""

from contextlib import asynccontextmanager
from typing import AsyncIterator

from aioboto3 import Session as AIOBoto3Session
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from preparation_api.adapters.inbound.listeners import (
    PaymentClosedHandler,
    PaymentClosedListener,
)
from preparation_api.adapters.out import APIOrderInfoProvider, SAPreparationRepository
from preparation_api.application.use_cases import (
    CreatePreparationFromPaymentUseCase,
    GetWaitingListUseCase,
    MarkPreparationAsCompletedUseCase,
    MarkPreparationAsReadyUseCase,
    StartNextPreparationUseCase,
)
from preparation_api.domain.ports import OrderInfoProvider, PreparationRepository
from preparation_api.infrastructure.config import (
    AWSSettings,
    DatabaseSettings,
    OrderAPISettings,
    PaymentClosedListenerSettings,
)
from preparation_api.infrastructure.orm import SessionManager


def get_session_manager(settings: DatabaseSettings) -> SessionManager:
    """Return a SessionManager instance"""

    return SessionManager(settings=settings)


@asynccontextmanager
async def get_db_session(
    session_manager: SessionManager,
) -> AsyncIterator[AsyncSession]:
    """Get a database session"""

    async with session_manager.session() as session:
        yield session


def get_http_client() -> AsyncClient:
    """Return an AsyncClient instance"""

    return AsyncClient(timeout=10.0)  # Default timeout of 10 seconds


def get_order_info_provider(
    settings: OrderAPISettings,
    http_client: AsyncClient,
) -> OrderInfoProvider:
    """Return an OrderInfoProvider instance"""

    return APIOrderInfoProvider(settings=settings, http_client=http_client)


def get_preparation_repository(session: AsyncSession) -> PreparationRepository:
    """Return a PreparationRepository instance"""

    return SAPreparationRepository(session=session)


def get_aws_session(settings: AWSSettings) -> AIOBoto3Session:
    """Return an AIOBoto3Session instance"""

    return AIOBoto3Session(
        aws_access_key_id=settings.ACCESS_KEY_ID,
        aws_secret_access_key=settings.SECRET_ACCESS_KEY,
        region_name=settings.REGION_NAME,
        aws_account_id=settings.ACCOUNT_ID,
    )


def get_create_preparation_from_payment_use_case(
    preparation_repository: PreparationRepository,
    order_info_provider: OrderInfoProvider,
) -> CreatePreparationFromPaymentUseCase:
    """Return a CreatePreparationFromPaymentUseCase instance"""

    return CreatePreparationFromPaymentUseCase(
        preparation_repository=preparation_repository,
        order_info_provider=order_info_provider,
    )


def get_waiting_list_use_case(
    preparation_repository: PreparationRepository,
) -> GetWaitingListUseCase:
    """Return a GetWaitingListUseCase instance"""

    return GetWaitingListUseCase(preparation_repository=preparation_repository)


def get_start_next_preparation_use_case(
    preparation_repository: PreparationRepository,
) -> StartNextPreparationUseCase:
    """Return a StartNextPreparationUseCase instance"""

    return StartNextPreparationUseCase(preparation_repository=preparation_repository)


def get_mark_preparation_as_ready_use_case(
    preparation_repository: PreparationRepository,
) -> MarkPreparationAsReadyUseCase:
    """Return a MarkPreparationAsReadyUseCase instance"""

    return MarkPreparationAsReadyUseCase(preparation_repository=preparation_repository)


def get_mark_preparation_as_completed_use_case(
    preparation_repository: PreparationRepository,
) -> MarkPreparationAsCompletedUseCase:
    """Return a MarkPreparationAsCompletedUseCase instance"""

    return MarkPreparationAsCompletedUseCase(
        preparation_repository=preparation_repository
    )


def create_preparation_from_payment_use_case_factory(
    order_api_settings: OrderAPISettings,
    http_client: AsyncClient,
):
    """Create a factory function for creating use cases with sessions"""

    def use_case_factory(session: AsyncSession) -> CreatePreparationFromPaymentUseCase:
        repository = get_preparation_repository(session=session)
        order_info_provider = get_order_info_provider(
            settings=order_api_settings,
            http_client=http_client,
        )

        return get_create_preparation_from_payment_use_case(
            preparation_repository=repository,
            order_info_provider=order_info_provider,
        )

    return use_case_factory


def get_payment_closed_handler(
    session_manager: SessionManager,
    order_api_settings: OrderAPISettings,
    http_client: AsyncClient,
) -> PaymentClosedHandler:
    """Create a PaymentClosedHandler instance"""

    return PaymentClosedHandler(
        session_manager=session_manager,
        use_case_factory=create_preparation_from_payment_use_case_factory(
            order_api_settings=order_api_settings, http_client=http_client
        ),
    )


def get_payment_closed_listener(
    session: AIOBoto3Session,
    handler: PaymentClosedHandler,
    settings: PaymentClosedListenerSettings,
) -> PaymentClosedListener:
    """Create a PaymentClosedListener instance"""

    return PaymentClosedListener(session=session, handler=handler, settings=settings)
