"""Client for interacting with the Order API"""

import logging

from httpx import AsyncClient, HTTPError, HTTPStatusError

from preparation_api.domain.exceptions import OrderInfoProviderError
from preparation_api.domain.ports import OrderInfoProvider
from preparation_api.domain.value_objects import OrderInfo
from preparation_api.infrastructure.config import OrderAPISettings

logger = logging.getLogger(__name__)


class APIOrderInfoProvider(OrderInfoProvider):
    """A implementantion based on the Order API to fetch order information"""

    def __init__(self, settings: OrderAPISettings, http_client: AsyncClient):
        self.base_url = settings.BASE_URL
        self.timeout = settings.TIMEOUT
        self.http_client = http_client

    async def get(self, order_id: str) -> OrderInfo:
        url = f"{self.base_url}/order/{order_id}"
        err_prefix = f"[GET] {url} - Failed to make GET request to Order API: "
        try:
            response = await self.http_client.get(url, timeout=self.timeout)
            logger.debug("Response %s %s -> %s", "GET", url, response.status_code)
            response.raise_for_status()
        except (HTTPStatusError, HTTPError) as exc:
            raise OrderInfoProviderError(f"{err_prefix}{str(exc)}") from exc

        order_data = response.json()
        return OrderInfo.model_validate(
            {
                "order_id": order_data["orderId"],
                "preparation_time": order_data["preparationTime"],
            }
        )
