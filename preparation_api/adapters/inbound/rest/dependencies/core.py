"""Core dependencies for the REST adapter"""

import logging
from typing import Annotated, AsyncIterator

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from preparation_api.application.use_cases import (
    GetWaitingListUseCase,
    MarkPreparationAsCompletedUseCase,
    MarkPreparationAsReadyUseCase,
    StartNextPreparationUseCase,
)
from preparation_api.domain.ports import PreparationRepository
from preparation_api.infrastructure import factory

logger = logging.getLogger(__name__)


async def db_session(request: Request) -> AsyncIterator[AsyncSession]:
    """Dependency that provides a database session"""
    async with factory.get_db_session(
        session_manager=request.app.state.session_manager
    ) as session:
        logger.debug("Providing new database session via dependency")
        yield session


DBSessionDep = Annotated[AsyncSession, Depends(db_session)]


def get_preparation_repository(
    session: DBSessionDep,
) -> PreparationRepository:
    """Dependency that provides a PreparationRepository instance"""
    logger.debug("Providing PreparationRepository via dependency")
    return factory.get_preparation_repository(session=session)


PreparationRepositoryDep = Annotated[
    PreparationRepository, Depends(get_preparation_repository)
]


def get_get_waiting_list_use_case(
    preparation_repository: PreparationRepositoryDep,
) -> GetWaitingListUseCase:
    """Dependency that provides a GetWaitingListUseCase instance"""

    logger.debug("Providing GetWaitingListUseCase via dependency")
    return factory.get_waiting_list_use_case(
        preparation_repository=preparation_repository
    )


def get_start_next_preparation_use_case(
    preparation_repository: PreparationRepositoryDep,
) -> StartNextPreparationUseCase:
    """Dependency that provides a StartNextPreparationUseCase instance"""

    logger.debug("Providing StartNextPreparationUseCase via dependency")
    return factory.get_start_next_preparation_use_case(
        preparation_repository=preparation_repository
    )


def get_mark_preparation_as_ready_use_case(
    preparation_repository: PreparationRepositoryDep,
) -> MarkPreparationAsReadyUseCase:
    """Dependency that provides a MarkPreparationAsReadyUseCase instance"""

    logger.debug("Providing MarkPreparationAsReadyUseCase via dependency")
    return factory.get_mark_preparation_as_ready_use_case(
        preparation_repository=preparation_repository
    )


def get_mark_preparation_as_completed_use_case(
    preparation_repository: PreparationRepositoryDep,
) -> MarkPreparationAsCompletedUseCase:
    """Dependency that provides a MarkPreparationAsCompletedUseCase instance"""

    logger.debug("Providing MarkPreparationAsCompletedUseCase via dependency")
    return factory.get_mark_preparation_as_completed_use_case(
        preparation_repository=preparation_repository
    )


GetWaitingListUseCaseDep = Annotated[
    GetWaitingListUseCase, Depends(get_get_waiting_list_use_case)
]

StartNextPreparationUseCaseDep = Annotated[
    StartNextPreparationUseCase, Depends(get_start_next_preparation_use_case)
]

MarkPreparationAsReadyUseCaseDep = Annotated[
    MarkPreparationAsReadyUseCase, Depends(get_mark_preparation_as_ready_use_case)
]

MarkPreparationAsCompletedUseCaseDep = Annotated[
    MarkPreparationAsCompletedUseCase,
    Depends(get_mark_preparation_as_completed_use_case),
]
