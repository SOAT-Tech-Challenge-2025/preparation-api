"""Preparation repository interface"""

from abc import ABC, abstractmethod

from preparation_api.domain.entities import PreparationIn, PreparationOut


class PreparationRepository(ABC):
    """Abstract base class for preparation repository."""

    @abstractmethod
    async def save(self, preparation: PreparationIn) -> PreparationOut:
        """Saves a preparation entity

        :param: preparation: Preparation entity to be saved
        :type preparation: PreparationIn
        :return: Saved preparation entity
        :rtype: PreparationOut
        :raises PersistenceError: If an error occurs while saving the
            preparation entity
        """

    @abstractmethod
    async def find_by_id(self, preparation_id: str) -> PreparationOut:
        """Finds a preparation by its ID

        :param: preparation_id: Unique identifier for the preparation
        :type preparation_id: str
        :return: Preparation entity
        :rtype: PreparationOut
        :raises NotFound: If the preparation with the given ID does not exist
        :raises PersistenceError: If an error occurs while retrieving the
            preparation entity
        """

    @abstractmethod
    async def exists_by_id(self, preparation_id: str) -> bool:
        """Checks if a preparation exists by its ID

        :param: preparation_id: Unique identifier for the preparation
        :type preparation_id: str
        :return: True if the preparation exists, False otherwise
        :rtype: bool
        :raises PersistenceError: If an error occurs while checking the
            preparation entity existence
        """

    @abstractmethod
    async def find_max_position(self) -> int:
        """Finds the maximum preparation position among preparations

        :return: Maximum preparation position
        :rtype: int
        :raises PersistenceError: If an error occurs while retrieving the
            maximum preparation position
        """

    @abstractmethod
    async def find_received_with_min_position(self) -> PreparationOut:
        """Finds the received preparation with the minimum preparation position

        :return: Preparation entity with the minimum position and status RECEIVED
        :rtype: PreparationOut
        :raises NotFound: If no preparation with status RECEIVED exists
        :raises PersistenceError: If an error occurs while retrieving the
            preparation entity
        """

    @abstractmethod
    async def decrement_received_positions_greater_than(
        self, preparation_position: int
    ) -> None:
        """Decrements the preparation positions of received preparations greater than
        the given position

        :param: preparation_position: Position threshold
        :type preparation_position: int
        :raises PersistenceError: If an error occurs while updating the
            preparation entities
        """

    @abstractmethod
    async def get_received_waiting_list(self) -> list[PreparationOut]:
        """Gets the list of preparations with status RECEIVED

        :return: List of preparations with status RECEIVED
        :rtype: list[PreparationOut]
        :raises PersistenceError: If an error occurs while retrieving the
            preparation entities
        """

    @abstractmethod
    async def get_in_preparation_waiting_list(self) -> list[PreparationOut]:
        """Gets the list of preparations with status IN_PREPARATION

        :return: List of preparations with status IN_PREPARATION
        :rtype: list[PreparationOut]
        :raises PersistenceError: If an error occurs while retrieving the
            preparation entities
        """

    @abstractmethod
    async def get_ready_waiting_list(self) -> list[PreparationOut]:
        """Gets the list of preparations with status READY

        :return: List of preparations with status READY
        :rtype: list[PreparationOut]
        :raises PersistenceError: If an error occurs while retrieving the
            preparation entities
        """
