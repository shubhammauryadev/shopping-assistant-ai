"""Business logic services for products and cart."""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from models import ProductCache, Cart, CartItem
from fake_store_client import get_all_products, get_product_by_id, get_products_by_category


class ProductService:
    """Service for product operations - cache and search."""

    @staticmethod
    def sync_product_cache(db: Session):
        """Sync product cache from Fake Store API."""
        products = get_all_products()
        for product in products:
            existing = db.query(ProductCache).filter(
                ProductCache.product_id == product["id"]
            ).first()

            if not existing:
                cache_entry = ProductCache(
                    product_id=product["id"],
                    category=product["category"],
                    title=product["title"],
                    price=product["price"],
                    description=product["description"],
                    image=product["image"],
                    cached_at=datetime.utcnow()
                )
                db.add(cache_entry)
        db.commit()

    @staticmethod
    def get_or_cache_product(product_id: int, db: Session):
        """Get product from cache or fetch from API and cache it."""
        cached = db.query(ProductCache).filter(
            ProductCache.product_id == product_id
        ).first()

        if cached:
            return {
                "id": cached.product_id,
                "category": cached.category,
                "title": cached.title,
                "price": cached.price,
                "description": cached.description,
                "image": cached.image,
            }

        # Fetch from API and cache
        product = get_product_by_id(product_id)
        if product:
            cache_entry = ProductCache(
                product_id=product["id"],
                category=product["category"],
                title=product["title"],
                price=product["price"],
                description=product["description"],
                image=product["image"],
                cached_at=datetime.utcnow()
            )
            db.add(cache_entry)
            db.commit()

        return product

    @staticmethod
    def search_products(query: str, category: str = None, price_range: dict = None, db: Session = None):
        """Search products by query, category, and price range."""
        products = get_all_products()

        # Check if query matches an actual category name (case-insensitive)
        # This prevents filtering out products when user says "electronics" instead of using category param
        query_is_category = False
        if query:
            query_lower = query.lower()
            all_categories = set(p["category"].lower() for p in products)
            if query_lower in all_categories:
                query_is_category = True
                # Use query as category filter if no explicit category provided
                if not category:
                    category = query

        # Filter by query (search in title and description) - only if query is NOT a category name
        if query and not query_is_category:
            query_lower = query.lower()
            products = [p for p in products if query_lower in p["title"].lower() or query_lower in p["description"].lower()]

        # Filter by category (handles both explicit category and query-derived category)
        if category:
            products = [p for p in products if p["category"].lower() == category.lower()]

        # Filter by price range
        if price_range:
            min_price = price_range.get("min", 0)
            max_price = price_range.get("max", float("inf"))
            products = [p for p in products if min_price <= p["price"] <= max_price]

        # Cache all results
        if db:
            for product in products:
                existing = db.query(ProductCache).filter(
                    ProductCache.product_id == product["id"]
                ).first()
                if not existing:
                    cache_entry = ProductCache(
                        product_id=product["id"],
                        category=product["category"],
                        title=product["title"],
                        price=product["price"],
                        description=product["description"],
                        image=product["image"],
                        cached_at=datetime.utcnow()
                    )
                    db.add(cache_entry)
            db.commit()

        return products


class CartService:
    """Service for cart operations."""

    @staticmethod
    def get_or_create_cart(session_id: str, db: Session):
        """Get existing cart or create new one for session."""
        cart = db.query(Cart).filter(Cart.session_id == session_id).first()
        if not cart:
            cart = Cart(session_id=session_id)
            db.add(cart)
            db.commit()
            db.refresh(cart)
        return cart

    @staticmethod
    def add_to_cart(session_id: str, product_id: int, quantity: int, product_title: str, price: float, db: Session):
        """Add item to cart or update quantity if exists."""
        cart = CartService.get_or_create_cart(session_id, db)

        existing_item = db.query(CartItem).filter(
            CartItem.cart_id == cart.id,
            CartItem.product_id == product_id
        ).first()

        if existing_item:
            existing_item.quantity += quantity
        else:
            item = CartItem(
                cart_id=cart.id,
                product_id=product_id,
                product_title=product_title,
                price=price,
                quantity=quantity
            )
            db.add(item)

        cart.updated_at = datetime.utcnow()
        db.commit()

    @staticmethod
    def remove_from_cart(session_id: str, product_id: int, db: Session):
        """Remove item from cart."""
        cart = CartService.get_or_create_cart(session_id, db)

        item = db.query(CartItem).filter(
            CartItem.cart_id == cart.id,
            CartItem.product_id == product_id
        ).first()

        if item:
            db.delete(item)
            cart.updated_at = datetime.utcnow()
            db.commit()

    @staticmethod
    def clear_cart(session_id: str, db: Session):
        """Clear all items from cart."""
        cart = CartService.get_or_create_cart(session_id, db)

        items = db.query(CartItem).filter(CartItem.cart_id == cart.id).all()

        for item in items:
            db.delete(item)

        if items:
            cart.updated_at = datetime.utcnow()
            db.commit()

    @staticmethod
    def get_cart(session_id: str, db: Session):
        """Get cart with all items for a session."""
        cart = CartService.get_or_create_cart(session_id, db)

        items = db.query(CartItem).filter(CartItem.cart_id == cart.id).all()

        return {
            "cart_id": cart.id,
            "session_id": cart.session_id,
            "items": [
                {
                    "product_id": item.product_id,
                    "product_title": item.product_title,
                    "price": item.price,
                    "quantity": item.quantity,
                }
                for item in items
            ],
            "total_items": sum(item.quantity for item in items),
            "total_price": sum(item.price * item.quantity for item in items),
        }
