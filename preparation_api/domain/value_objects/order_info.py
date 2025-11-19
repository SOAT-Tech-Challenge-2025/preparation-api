"""Order info value object definition"""

from pydantic import BaseModel, Field


class OrderInfo(BaseModel):
    """Order information value object"""

    order_id: str = Field(..., description="Unique identifier for the order")
    preparation_time: int = Field(..., description="Preparation time in minutes")
