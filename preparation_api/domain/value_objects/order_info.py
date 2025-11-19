"""Order info value object definition"""

from pydantic import BaseModel, Field


class OrderInfo(BaseModel):
    """Enumeration of possible payment statuses."""

    order_id: str = Field(..., description="Unique identifier for the order")
    preparation_time: int = Field(..., description="Preparation time in minutes")
