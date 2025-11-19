"""Abstract base class for order information provider"""

from abc import ABC, abstractmethod

from preparation_api.domain.value_objects import OrderInfo


class OrderInfoProvider(ABC):
    """Abstract base class for order information provider"""

    @abstractmethod
    async def get(self, order_id: str) -> OrderInfo:
        """Fetches order information by order ID

        :param: order_id: Unique identifier for the order
        :type order_id: str
        :return: Order information
        :rtype: OrderInfo
        :raises OrderInfoProviderError: If an error occurs while fetching order
            information
        """
