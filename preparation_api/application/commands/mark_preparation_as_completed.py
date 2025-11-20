"""Command to mark a preparation as complete"""

from pydantic import BaseModel, Field


class MarkPreparationAsCompletedCommand(BaseModel):
    """Command to mark a preparation as complete"""

    preparation_id: str = Field(
        ..., description="The unique identifier of the preparation"
    )
