"""Use case to start the next preparation"""

import logging
from datetime import datetime, timedelta, timezone

from preparation_api.domain.entities import PreparationIn, PreparationOut
from preparation_api.domain.exceptions import NotFound
from preparation_api.domain.ports import PreparationRepository
from preparation_api.domain.value_objects import PreparationStatus

logger = logging.getLogger(__name__)


class StartNextPreparationUseCase:
    """Use case to start the next preparation"""

    def __init__(self, preparation_repository: PreparationRepository):
        self.preparation_repository = preparation_repository

    async def execute(self) -> PreparationOut:
        """Execute the use case to start the next preparation

        :return: The started PreparationOut entity
        :rtype: PreparationOut
        :raises ValueError: If there is a validation error
        :raises PersistenceError: If there is an error updating the preparation
        """

        logger.info("Called the use case to start the next preparation")

        # Find the received preparation with the minimum position
        try:
            preparation_out = (
                await self.preparation_repository.find_received_with_min_position()
            )
        except NotFound as error:
            raise ValueError("No received preparation found to start") from error

        # Save the old preparation position to decrease positions later
        old_preparation_position = preparation_out.preparation_position

        # Calculate the estimated datetime to the preparation be ready
        estimated_ready_time = datetime.now(timezone.utc) + timedelta(
            minutes=preparation_out.preparation_time
        )

        # Create the updated PreparationIn entity
        preparation_in = PreparationIn(
            id=preparation_out.id,
            preparation_position=None,  # Remove position when in preparation
            preparation_time=preparation_out.preparation_time,
            estimated_ready_time=estimated_ready_time,
            preparation_status=PreparationStatus.IN_PREPARATION,
        )

        # Save the updated preparation
        updated_preparation_out = await self.preparation_repository.save(
            preparation=preparation_in
        )

        # Decrease the position of all received preparations with position greater
        # than the old preparation position
        if old_preparation_position is not None:
            await self.preparation_repository.decrement_received_positions_greater_than(
                preparation_position=old_preparation_position
            )

        # Return the started PreparationOut entity
        return updated_preparation_out
