"""Use case to create a preparation from a payment"""

import logging

from preparation_api.application.commands import CreatePreparationFromPaymentCommand
from preparation_api.domain.entities import PreparationIn, PreparationOut
from preparation_api.domain.ports import OrderInfoProvider, PreparationRepository
from preparation_api.domain.value_objects import PreparationStatus

logger = logging.getLogger(__name__)


class CreatePreparationFromPaymentUseCase:
    """Use case to create a preparation from a payment"""

    def __init__(
        self,
        preparation_repository: PreparationRepository,
        order_info_provider: OrderInfoProvider,
    ):
        self.preparation_repository = preparation_repository
        self.order_info_provider = order_info_provider

    async def execute(
        self, command: CreatePreparationFromPaymentCommand
    ) -> PreparationOut:
        """Execute the use case to create a preparation from a payment

        :param command: The command containing the payment ID
        :type command: CreatePreparationFromPaymentCommand
        :return: The created PreparationOut entity
        :rtype: PreparationOut
        :raises OrderInfoProviderError: If there is an error fetching order information
        :raises PersistenceError: If there is an error saving the preparation
        :raises ValueError: If there is a validation error
        """

        logger.info(
            "Called the use case to create a preparation from payment ID %s",
            command.payment_id,
        )

        # Validate
        if await self.preparation_repository.exists_by_id(command.payment_id):
            raise ValueError(
                f"Preparation for payment ID {command.payment_id} already exists"
            )

        # Get order info from the OrderInfoProvider
        order_info = await self.order_info_provider.get(order_id=command.payment_id)

        # Find the next preparation position
        preparation_position = await self.preparation_repository.find_max_position() + 1

        # Create the PreparationIn entity
        preparation_in = PreparationIn(
            id=order_info.order_id,
            preparation_position=preparation_position,
            preparation_time=order_info.preparation_time,
            preparation_status=PreparationStatus.RECEIVED,
        )

        # Save the preparation using the repository
        preparation_out = await self.preparation_repository.save(
            preparation=preparation_in
        )

        # Return the created PreparationOut entity
        return preparation_out
