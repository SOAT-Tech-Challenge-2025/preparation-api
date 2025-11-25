"""Listener for payment closed events from SQS"""

import json
import logging
from typing import Callable

from aioboto3 import Session as AIOBoto3Session
from botocore.exceptions import ClientError as BotoCoreClientError
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from preparation_api.application.commands import CreatePreparationFromPaymentCommand
from preparation_api.application.use_cases import CreatePreparationFromPaymentUseCase
from preparation_api.infrastructure.config import PaymentClosedListenerSettings
from preparation_api.infrastructure.orm import SessionManager

logger = logging.getLogger(__name__)


class PaymentClosedMessage(BaseModel):
    """Model for payment closed SQS message"""

    payment_id: str = Field(description="Unique identifier for the closed payment")


class PaymentClosedHandler:
    """Handler for processing payment closed messages"""

    def __init__(
        self,
        session_manager: SessionManager,
        use_case_factory: Callable[[AsyncSession], CreatePreparationFromPaymentUseCase],
    ):
        self.session_manager = session_manager
        self.use_case_factory = use_case_factory

    async def handle(self, message):
        """Handle the payment closed message"""

        body = await message.body
        message_id = await message.message_id
        logger.info("Received message: %s: %s", message_id, body)
        async with self.session_manager.session() as db_session:
            use_case = self.use_case_factory(db_session)
            body_dict = json.loads(body)
            payment_message = PaymentClosedMessage.model_validate_json(
                body_dict["Message"]
            )

            command = CreatePreparationFromPaymentCommand(
                payment_id=payment_message.payment_id
            )

            await use_case.execute(command=command)
            await message.delete()
            logger.info("Successfully processed and deleted message ID: %s", message_id)


class PaymentClosedListener:
    """Listener for handling payment closed events from SQS"""

    def __init__(
        self,
        session: AIOBoto3Session,
        handler: PaymentClosedHandler,
        settings: PaymentClosedListenerSettings,
    ):
        self.session = session
        self.handler = handler
        self.queue_name = settings.QUEUE_NAME
        self.wait_time = settings.WAIT_TIME_SECONDS
        self.visibility_timeout = settings.VISIBILITY_TIMEOUT_SECONDS
        self.max_messages = settings.MAX_NUMBER_OF_MESSAGES_PER_BATCH

    async def listen(self, shutdown_event=None):
        """Listen for payment closed events and process them"""

        async with self.session.resource("sqs") as sqs_client:
            logger.info("Listening for messages on queue: %s", self.queue_name)
            queue = await sqs_client.get_queue_by_name(QueueName=self.queue_name)
            while True:
                if shutdown_event and shutdown_event.shutdown:
                    logger.info("Shutdown requested, stopping listener")
                    break

                messages = await self._consume(queue=queue)
                if not messages:
                    logger.debug("No messages received in %d seconds", self.wait_time)
                    continue

    async def _consume(self, queue):
        try:
            messages = await queue.receive_messages(
                MessageAttributeNames=["All"],
                MaxNumberOfMessages=self.max_messages,
                WaitTimeSeconds=self.wait_time,
                VisibilityTimeout=self.visibility_timeout,
            )

        except BotoCoreClientError as error:
            logger.error(
                "Couldn't receive messages from queue: %s", queue, exc_info=True
            )

            raise error

        for msg in messages:
            message_id = await msg.message_id
            try:
                await self.handler.handle(message=msg)
            except Exception:  # pylint: disable=W0718
                logger.error(
                    "Failed to process message ID: %s",
                    message_id,
                    exc_info=True,
                )

                await msg.delete()
                logger.warning("Deleted message ID: %s to avoid retries", message_id)
                # TODO: Implement a dead-letter queue to handle failed messages

        return messages
