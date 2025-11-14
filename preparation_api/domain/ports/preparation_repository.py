"""Preparation repository interface"""

from abc import ABC, abstractmethod

from preparation_api.domain.entities import PreparationIn, PreparationOut


class PreparationRepository(ABC):
    """Abstract base class for preparation repository."""

    @abstractmethod
    async def save(self, preparation: PreparationIn) -> PreparationOut:
        """Saves a preparation entity"""

    @abstractmethod
    async def find_by_id(self, preparation_id: str) -> PreparationOut:
        """Finds a preparation by its ID"""

    @abstractmethod
    async def exists_by_id(self, preparation_id: str) -> bool:
        """Checks if a preparation exists by its ID"""

    @abstractmethod
    async def find_max_position(self) -> int:
        """Finds the maximum preparation position among preparations"""

    @abstractmethod
    async def find_received_with_min_position(self) -> PreparationOut:
        """Finds the received preparation with the minimum preparation position"""

    @abstractmethod
    async def decrement_received_positions_greater_than(
        self, preparation_position: int
    ) -> None:
        """Decrements the preparation positions of received preparations greater than
        the given position"""

    @abstractmethod
    async def get_received_waiting_list(self) -> list[PreparationOut]:
        """Gets the list of preparations with status RECEIVED"""

    @abstractmethod
    async def get_in_preparation_waiting_list(self) -> list[PreparationOut]:
        """Gets the list of preparations with status IN_PREPARATION"""

    @abstractmethod
    async def get_ready_waiting_list(self) -> list[PreparationOut]:
        """Gets the list of preparations with status READY"""
