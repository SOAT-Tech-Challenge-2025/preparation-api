"""V1 Preparation REST API endpoint module"""

import logging

from fastapi import APIRouter, HTTPException

from preparation_api.adapters.inbound.rest.dependencies.core import (
    GetWaitingListUseCaseDep,
    MarkPreparationAsCompletedUseCaseDep,
    MarkPreparationAsReadyUseCaseDep,
    StartNextPreparationUseCaseDep,
)
from preparation_api.adapters.inbound.rest.v1.schemas import (
    PreparationListV1,
    PreparationV1,
)
from preparation_api.application.commands import (
    MarkPreparationAsCompletedCommand,
    MarkPreparationAsReadyCommand,
)
from preparation_api.domain.exceptions import PersistenceError

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/v1/preparation", tags=["preparation"])


@router.post("/start-next", response_model=PreparationV1)
async def start_next(
    start_next_preparation_use_case: StartNextPreparationUseCaseDep,
):
    """Start the next received preparation in the waiting list"""

    try:
        preparation = await start_next_preparation_use_case.execute()
    except ValueError as e:
        logger.error(
            "Value error occurred when starting next preparation", exc_info=True
        )

        raise HTTPException(status_code=400, detail=str(e)) from e
    except PersistenceError as e:
        logger.error(
            "Persistence error occurred when starting next preparation",
            exc_info=True,
        )

        raise HTTPException(status_code=500, detail="Internal server error") from e

    logger.info("Next preparation started successfully id=%s", preparation.id)
    return PreparationV1.model_validate(preparation.model_dump())


@router.post("/{preparation_id}/ready", response_model=PreparationV1)
async def mark_as_ready(
    preparation_id: str,
    mark_preparation_as_ready_use_case: MarkPreparationAsReadyUseCaseDep,
):
    """Mark an in progress preparation as ready"""

    command = MarkPreparationAsReadyCommand(preparation_id=preparation_id)
    try:
        preparation = await mark_preparation_as_ready_use_case.execute(command)
    except ValueError as e:
        logger.error(
            "Value error occurred when marking preparation as ready id=%s",
            preparation_id,
            exc_info=True,
        )

        raise HTTPException(status_code=400, detail=str(e)) from e
    except PersistenceError as e:
        logger.error(
            "Persistence error occurred when marking preparation as ready id=%s",
            preparation_id,
            exc_info=True,
        )

        raise HTTPException(status_code=500, detail="Internal server error") from e

    logger.info("Preparation marked as ready successfully id=%s", preparation.id)
    return PreparationV1.model_validate(preparation.model_dump())


@router.post("/{preparation_id}/complete", response_model=PreparationV1)
async def mark_as_completed(
    preparation_id: str,
    mark_preparation_as_completed_use_case: MarkPreparationAsCompletedUseCaseDep,
):
    """Mark a ready preparation as completed"""

    command = MarkPreparationAsCompletedCommand(preparation_id=preparation_id)
    try:
        preparation = await mark_preparation_as_completed_use_case.execute(command)
    except ValueError as e:
        logger.error(
            "Value error occurred when marking preparation as completed id=%s",
            preparation_id,
            exc_info=True,
        )

        raise HTTPException(status_code=400, detail=str(e)) from e
    except PersistenceError as e:
        logger.error(
            "Persistence error occurred when marking preparation as completed id=%s",
            preparation_id,
            exc_info=True,
        )

        raise HTTPException(status_code=500, detail="Internal server error") from e

    logger.info("Preparation marked as completed successfully id=%s", preparation.id)
    return PreparationV1.model_validate(preparation.model_dump())


@router.get("/waiting-list", response_model=PreparationListV1)
async def get_waiting_list(
    get_waiting_list_use_case: GetWaitingListUseCaseDep,
):
    """Get the current waiting list of preparations"""

    try:
        preparations = await get_waiting_list_use_case.execute()
    except PersistenceError as e:
        logger.error(
            "Persistence error occurred when retrieving waiting list", exc_info=True
        )

        raise HTTPException(status_code=500, detail="Internal server error") from e

    logger.info("Waiting list retrieved successfully, count=%d", len(preparations))
    return PreparationListV1.model_validate(
        {"items": [preparation.model_dump() for preparation in preparations]}
    )
