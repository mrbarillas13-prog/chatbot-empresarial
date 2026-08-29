from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class OrderItemCreate(BaseModel):
    product_id: UUID
    quantity: int = Field(..., gt=0)
    unit_price: float = Field(..., gt=0)


class OrderCreate(BaseModel):
    customer_name: str = Field(..., min_length=1, max_length=255)
    customer_email: str = Field(..., min_length=1)
    items: list[OrderItemCreate] = []


class OrderUpdate(BaseModel):
    status: Optional[str] = Field(None, pattern="^(pending|shipped|delivered|cancelled)$")


class OrderItemResponse(BaseModel):
    id: UUID
    product_id: UUID
    quantity: int
    unit_price: float

    model_config = {"from_attributes": True}


class OrderResponse(BaseModel):
    id: UUID
    customer_name: str
    customer_email: str
    status: str
    total: float
    created_at: datetime
    items: list[OrderItemResponse] = []

    model_config = {"from_attributes": True}


class OrderList(BaseModel):
    orders: list[OrderResponse]
    total: int
