"""Command to mark a preparation as ready"""

from pydantic import BaseModel, Field


class MarkPreparationAsReadyCommand(BaseModel):
    """Command to mark a preparation as ready"""

    preparation_id: str = Field(
        ..., description="The unique identifier of the preparation"
    )
