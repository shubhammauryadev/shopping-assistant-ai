"""SQLAlchemy ORM models for SQLite database."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Cart(Base):
    """Cart table - stores shopping carts by session."""
    __tablename__ = "cart"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")


class CartItem(Base):
    """CartItem table - individual items in a cart."""
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True)
    cart_id = Column(Integer, ForeignKey("cart.id"), nullable=False)
    product_id = Column(Integer, nullable=False, index=True)
    product_title = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, default=1, nullable=False)

    cart = relationship("Cart", back_populates="items")


class ConversationMessage(Base):
    """ConversationMessage table - stores chat history."""
    __tablename__ = "conversation_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True, nullable=False)
    role = Column(String, nullable=False)  # "user" or "assistant"
    content = Column(String, nullable=False)  # JSON or text
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class ProductCache(Base):
    """ProductCache table - caches product data from Fake Store API."""
    __tablename__ = "product_cache"

    product_id = Column(Integer, primary_key=True, index=True)
    category = Column(String, nullable=False)
    title = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    description = Column(String, nullable=False)
    image = Column(String, nullable=False)
    cached_at = Column(DateTime, default=datetime.utcnow, nullable=False)
