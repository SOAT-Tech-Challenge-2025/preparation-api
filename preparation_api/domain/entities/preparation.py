"""Preparation entity module"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from preparation_api.domain.value_objects import PreparationStatus


class PreparationIn(BaseModel):
    """Preparation input entity"""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(description="Unique identifier for the preparation")
    preparation_position: int | None = Field(
        None, description="Position of the preparation in the queue"
    )

    preparation_time: int = Field(
        description="Time required for the preparation in minutes"
    )

    estimated_ready_time: datetime | None = Field(
        None, description="Estimated time when the preparation will be ready"
    )

    preparation_status: PreparationStatus = Field(
        PreparationStatus.RECEIVED, description="Status of the preparation"
    )

    def ready(self) -> "PreparationIn":
        """Mark the preparation as ready"""

        if self.preparation_status != PreparationStatus.IN_PREPARATION:
            raise ValueError(
                f"A preparation with status {self.preparation_status.value} "
                "cannot be marked as ready."
            )

        self.preparation_status = PreparationStatus.READY
        return self

    def complete(self) -> "PreparationIn":
        """Mark the preparation as completed"""

        if self.preparation_status != PreparationStatus.READY:
            raise ValueError(
                f"A preparation with status {self.preparation_status.value} "
                "cannot be completed."
            )

        self.preparation_status = PreparationStatus.COMPLETED
        return self


class PreparationOut(PreparationIn):
    """Preparation output entity"""

    created_at: datetime = Field(
        description="Creation date and time of the preparation"
    )

    timestamp: datetime = Field(
        description="Last update date and time of the preparation"
    )
