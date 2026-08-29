from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    category: Optional[str] = None
    stock: int = Field(default=0, ge=0)


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    category: Optional[str] = None
    stock: Optional[int] = Field(None, ge=0)


class ProductResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    price: float
    category: Optional[str]
    stock: int
    created_at: datetime

    model_config = {"from_attributes": True}


class ProductList(BaseModel):
    products: list[ProductResponse]
    total: int
