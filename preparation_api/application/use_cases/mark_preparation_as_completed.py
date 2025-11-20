"""Use case to mark a preparation as completed"""

import logging

from preparation_api.application.commands import MarkPreparationAsCompletedCommand
from preparation_api.domain.entities import PreparationIn, PreparationOut
from preparation_api.domain.exceptions import NotFound
from preparation_api.domain.ports import PreparationRepository

logger = logging.getLogger(__name__)


class MarkPreparationAsCompletedUseCase:
    """Use case to mark a preparation as completed"""

    def __init__(self, preparation_repository: PreparationRepository):
        self.preparation_repository = preparation_repository

    async def execute(
        self, command: MarkPreparationAsCompletedCommand
    ) -> PreparationOut:
        """Execute the use case to mark a preparation as completed

        :param command: The command to mark a preparation as completed
        :type command: MarkPreparationAsCompletedCommand
        :return: The completed PreparationOut entity
        :rtype: PreparationOut
        :raises ValueError: If there is a validation error
        :raises PersistenceError: If there is an error updating the preparation
        """

        logger.info(
            "Called the use case to mark a preparation as completed with ID: %s",
            command.preparation_id,
        )

        # Find the preparation by ID
        try:
            preparation = await self.preparation_repository.find_by_id(
                preparation_id=command.preparation_id
            )
        except NotFound as error:
            raise ValueError(
                f"Preparation with ID {command.preparation_id} not found"
            ) from error

        # The domain logic to mark the preparation as completed
        preparation.complete()

        # Create the updated PreparationIn entity
        preparation_in = PreparationIn(
            id=preparation.id,
            preparation_position=preparation.preparation_position,
            preparation_time=preparation.preparation_time,
            estimated_ready_time=preparation.estimated_ready_time,
            preparation_status=preparation.preparation_status,
        )

        # Save the updated preparation
        updated_preparation = await self.preparation_repository.save(
            preparation=preparation_in
        )

        # Return the updated PreparationOut entity
        return updated_preparation
