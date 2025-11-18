"""The preparation ORM model"""

from datetime import datetime

from sqlalchemy import func, types
from sqlalchemy.orm import Mapped, mapped_column

from preparation_api.domain.value_objects import PreparationStatus

from .base import BaseModel


class Preparation(BaseModel):
    """The preparation ORM model"""

    __tablename__ = "tb_pagamento"

    id: Mapped[str] = mapped_column(
        types.String, primary_key=True, unique=True, nullable=False
    )

    preparation_position: Mapped[int | None] = mapped_column(
        types.Integer, name="posicao_preparacao", nullable=True
    )

    preparation_time: Mapped[int] = mapped_column(
        types.Integer, name="tempo_de_preparacao", nullable=False
    )

    estimated_ready_time: Mapped[datetime | None] = mapped_column(
        types.TIMESTAMP, name="estimativa_de_pronto", nullable=True
    )

    preparation_status: Mapped[PreparationStatus] = mapped_column(
        types.Enum(PreparationStatus, native_enum=False),
        name="st_preparacao",
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        types.TIMESTAMP,
        name="dt_inclusao",
        default=func.now(),  # pylint: disable=E1102
        nullable=False,
    )

    timestamp: Mapped[datetime] = mapped_column(
        types.TIMESTAMP,
        name="timestamp",
        default=func.now(),  # pylint: disable=E1102
        onupdate=func.now(),  # pylint: disable=E1102
        nullable=False,
    )

    def __repr__(self):
        return f"{type(self).__name__}[{self.id}]"
