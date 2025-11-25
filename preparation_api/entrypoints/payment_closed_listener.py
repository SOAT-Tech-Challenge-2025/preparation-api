"""Payment closed event listener entrypoint module"""

import asyncio
import logging
import signal

from preparation_api.infrastructure import factory
from preparation_api.infrastructure.config import (
    AWSSettings,
    DatabaseSettings,
    OrderAPISettings,
    PaymentClosedListenerSettings,
)

logger = logging.getLogger(__name__)


class GracefulShutdown:
    """Handles graceful shutdown on SIGTERM and SIGINT signals"""

    def __init__(self):
        self.shutdown = False
        signal.signal(signal.SIGTERM, self._exit_gracefully)
        signal.signal(signal.SIGINT, self._exit_gracefully)

    def _exit_gracefully(self, signum, frame):
        logger.info("Received shutdown signal %d", signum)
        self.shutdown = True


async def main():
    """Run the order created event listener"""

    shutdown_handler = GracefulShutdown()
    try:
        logger.info("Loading database settings")
        db_settings = DatabaseSettings()
        logger.info("Loading Order API settings")
        order_api_settings = OrderAPISettings()
        logger.info("Loading Payment Closed Listener settings")
        payment_closed_listener_settings = PaymentClosedListenerSettings()
        logger.info("Starting session manager")
        session_manager = factory.get_session_manager(settings=db_settings)
        logger.info("Starting HTTP client")
        http_client = factory.get_http_client()
        logger.info("Starting AWS session")
        aws_settings = AWSSettings()
        logger.info("Starting AWS session")
        aws_session = factory.get_aws_session(settings=aws_settings)
        logger.info("Creating payment closed message handler")
        handler = factory.get_payment_closed_handler(
            session_manager=session_manager,
            order_api_settings=order_api_settings,
            http_client=http_client,
        )

        logger.info("Creating payment closed event listener")
        listener = factory.get_payment_closed_listener(
            session=aws_session,
            handler=handler,
            settings=payment_closed_listener_settings,
        )

        logger.info("Starting payment closed event listener")
        await listener.listen(shutdown_event=shutdown_handler)
    finally:
        logger.info("Closing session manager")
        await session_manager.close()
        logger.info("Closing HTTP client")
        await http_client.aclose()


if __name__ == "__main__":
    import logging.config

    logging.config.fileConfig("logging.ini", disable_existing_loggers=False)
    asyncio.run(main())
