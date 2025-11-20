"""Use case to get the waiting list"""

import logging

from preparation_api.domain.entities import PreparationOut
from preparation_api.domain.ports import PreparationRepository

logger = logging.getLogger(__name__)


class GetWaitingListUseCase:
    """Use case to get the waiting list"""

    def __init__(self, preparation_repository: PreparationRepository):
        self.preparation_repository = preparation_repository

    async def execute(self) -> list[PreparationOut]:
        """Execute the use case to get the waiting list

        :return: The list of PreparationOut entities in the waiting list
        :rtype: list[PreparationOut]
        :raises PersistenceError: If there is an error retrieving the waiting list
        """

        logger.info("Called the use case to get the waiting list")

        # Retrieve the ready preparations retrieved from the repository
        waiting_list = await self.preparation_repository.get_ready_waiting_list()

        # Combine with in-preparation preparations retrieved from the repository
        waiting_list.extend(
            await self.preparation_repository.get_in_preparation_waiting_list()
        )

        # Combine with received preparations retrieved from the repository
        waiting_list.extend(
            await self.preparation_repository.get_received_waiting_list()
        )

        # Return the complete waiting list
        return waiting_list
