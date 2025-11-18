"""SQL Alchemy implementation of the PreparationRepository port"""

from datetime import datetime

from sqlalchemy import exists, insert, select, update
from sqlalchemy.exc import NoResultFound, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from preparation_api.domain.entities import PreparationIn, PreparationOut
from preparation_api.domain.exceptions import NotFound, PersistenceError
from preparation_api.domain.ports import PreparationRepository
from preparation_api.domain.value_objects import PreparationStatus
from preparation_api.infrastructure.orm.models import Preparation as PreparationModel


class SAPreparationRepository(PreparationRepository):
    """A SQL Alchemy implementation of the PreparationRepository port"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, preparation: PreparationIn) -> PreparationOut:
        if await self.exists_by_id(preparation_id=preparation.id):
            return await self._update(preparation=preparation)
        return await self._insert(preparation=preparation)

    async def find_by_id(self, preparation_id: str) -> PreparationOut:
        try:
            result = await self.session.execute(
                select(PreparationModel).where(PreparationModel.id == preparation_id)
            )

            return PreparationOut.model_validate(result.scalars().one())

        except NoResultFound as error:
            raise NotFound(f"No preparation found with ID: {preparation_id}") from error

        except (SQLAlchemyError, OSError) as error:
            raise PersistenceError(
                f"Error finding preparation by ID {preparation_id}: {str(error)}"
            ) from error

    async def exists_by_id(self, preparation_id: str) -> bool:
        try:
            result = await self.session.execute(
                select(exists().where(PreparationModel.id == preparation_id))
            )

            return result.scalar()

        except (SQLAlchemyError, OSError) as error:
            raise PersistenceError(
                f"Error checking preparation existence by ID {preparation_id}: "
                f"{str(error)}"
            ) from error

    async def find_max_position(self) -> int:
        try:
            result = await self.session.execute(
                select(PreparationModel.preparation_position)
                .where(
                    PreparationModel.preparation_status == PreparationStatus.RECEIVED
                )
                .order_by(PreparationModel.preparation_position.desc())
                .limit(1)
            )

            max_position_preparation = result.scalars().first()
            return max_position_preparation or 0

        except (SQLAlchemyError, OSError) as error:
            raise PersistenceError(
                f"Error finding max preparation position: {str(error)}"
            ) from error

    async def find_received_with_min_position(self) -> PreparationOut:
        try:
            result = await self.session.execute(
                select(PreparationModel)
                .where(
                    PreparationModel.preparation_status == PreparationStatus.RECEIVED
                )
                .order_by(PreparationModel.preparation_position.asc())
                .limit(1)
            )

            return PreparationOut.model_validate(result.scalars().one())

        except NoResultFound as error:
            raise NotFound("No received preparation found") from error

        except (SQLAlchemyError, OSError) as error:
            raise PersistenceError(
                f"Error finding received preparation with min position: {str(error)}"
            ) from error

    async def decrement_received_positions_greater_than(
        self, preparation_position: int
    ) -> None:
        try:
            await self.session.execute(
                update(PreparationModel)
                .where(
                    PreparationModel.preparation_status == PreparationStatus.RECEIVED,
                    PreparationModel.preparation_position > preparation_position,
                )
                .values(
                    preparation_position=PreparationModel.preparation_position - 1,
                    timestamp=datetime.now(),
                )
            )
            await self.session.commit()

        except (SQLAlchemyError, OSError) as error:
            raise PersistenceError(
                f"Error decrementing preparation positions greater than "
                f"{preparation_position}: {str(error)}"
            ) from error

    async def get_received_waiting_list(self) -> list[PreparationOut]:
        try:
            result = await self.session.execute(
                select(PreparationModel)
                .where(
                    PreparationModel.preparation_status == PreparationStatus.RECEIVED
                )
                .order_by(PreparationModel.preparation_position.asc())
            )

            preparations = result.scalars().all()
            return [PreparationOut.model_validate(p) for p in preparations]

        except (SQLAlchemyError, OSError) as error:
            raise PersistenceError(
                f"Error getting received waiting list: {str(error)}"
            ) from error

    async def get_in_preparation_waiting_list(self) -> list[PreparationOut]:
        try:
            result = await self.session.execute(
                select(PreparationModel)
                .where(
                    PreparationModel.preparation_status
                    == PreparationStatus.IN_PREPARATION
                )
                .order_by(PreparationModel.estimated_ready_time.asc())
            )

            preparations = result.scalars().all()
            return [PreparationOut.model_validate(p) for p in preparations]

        except (SQLAlchemyError, OSError) as error:
            raise PersistenceError(
                f"Error getting in preparation waiting list: {str(error)}"
            ) from error

    async def get_ready_waiting_list(self) -> list[PreparationOut]:
        try:
            result = await self.session.execute(
                select(PreparationModel)
                .where(PreparationModel.preparation_status == PreparationStatus.READY)
                .order_by(PreparationModel.timestamp.asc())
            )

            preparations = result.scalars().all()
            return [PreparationOut.model_validate(p) for p in preparations]

        except (SQLAlchemyError, OSError) as error:
            raise PersistenceError(
                f"Error getting ready waiting list: {str(error)}"
            ) from error

    async def _insert(self, preparation: PreparationIn) -> PreparationOut:
        """Insert a new preparation into the repository

        :param preparation: Preparation to be inserted
        :type preparation: PreparationIn
        :return: Inserted Preparation
        :rtype: PreparationOut
        """
        try:
            result = await self.session.execute(
                insert(PreparationModel)
                .values(**preparation.model_dump())
                .returning(PreparationModel)
            )

            inserted_preparation = PreparationOut.model_validate(result.scalars().one())
            await self.session.commit()
            return inserted_preparation

        except (SQLAlchemyError, OSError) as error:
            raise PersistenceError(
                f"Error inserting preparation {preparation.id}: {str(error)}"
            ) from error

    async def _update(self, preparation: PreparationIn) -> PreparationOut:
        """Update an existing preparation in the repository
        :param preparation: Preparation to be updated
        :type preparation: PreparationIn
        :return: Updated Preparation
        :rtype: PreparationOut
        """
        try:
            result = await self.session.execute(
                update(PreparationModel)
                .where(PreparationModel.id == preparation.id)
                .values(**preparation.model_dump())
                .returning(PreparationModel)
            )

            updated_preparation = PreparationOut.model_validate(result.scalars().one())
            await self.session.commit()
            return updated_preparation

        except (SQLAlchemyError, OSError) as error:
            raise PersistenceError(
                f"Error updating preparation {preparation.id}: {str(error)}"
            ) from error
