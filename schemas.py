"""Pydantic models for API request/response validation."""
from pydantic import BaseModel
from typing import Optional


class ChatRequest(BaseModel):
    """Request body for /chat endpoint."""
    message: str
    session_id: str


class CartItem(BaseModel):
    """Cart item in response."""
    product_id: int
    product_title: str
    price: float
    quantity: int


class CartResponse(BaseModel):
    """Cart response structure."""
    cart_id: int
    session_id: str
    items: list[CartItem]
    total_items: int
    total_price: float


class ProductInfo(BaseModel):
    """Product information in responses."""
    id: int
    title: str
    price: float
    category: str
    image: Optional[str] = None
    description: Optional[str] = None
