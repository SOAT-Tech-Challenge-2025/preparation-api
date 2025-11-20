"""Command to create a preparation from a payment"""

from pydantic import BaseModel, Field


class CreatePreparationFromPaymentCommand(BaseModel):
    """Command to create a preparation from a payment"""

    payment_id: str = Field(..., description="The unique identifier of the payment")
