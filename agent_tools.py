"""LangChain tool definitions for the shopping assistant agent."""
import json
from langchain_core.tools import tool
from sqlalchemy.orm import Session
from services import ProductService, CartService
from database import SessionLocal
from conversation_state import get_session_state

# Global session reference for tools (set by agent before execution)
_current_session: Session = None
_current_session_id: str = None


def set_session_context(session: Session, session_id: str):
    """Set the current database session for tool execution."""
    global _current_session, _current_session_id
    _current_session = session
    _current_session_id = session_id


@tool
def search_products(query: str, category: str = None, price_range: str = None) -> str:
    """
    Search for products by query, optionally filtered by category and price range.

    Args:
        query: Product search query (e.g., "laptop", "shoes")
        category: Optional category filter (e.g., "electronics", "clothing")
        price_range: Optional price range as JSON string (e.g., '{"min": 10, "max": 100}')

    Returns:
        JSON string of matching products
    """
    db = _current_session or SessionLocal()
    try:
        price_filter = None
        if price_range:
            try:
                price_filter = json.loads(price_range)
            except json.JSONDecodeError:
                return json.dumps({"error": "Invalid price_range format. Use JSON: {\"min\": X, \"max\": Y}"})

        results = ProductService.search_products(query, category, price_filter, db)

        # Return top 5 results
        top_results = results[:5]

        # Store results in conversation state for reference resolution
        state = get_session_state(_current_session_id)
        state.store_search_results(top_results)

        return json.dumps([
            {
                "id": p["id"],
                "title": p["title"],
                "price": p["price"],
                "category": p["category"],
                "image": p["image"],
            }
            for p in top_results
        ])
    finally:
        if not _current_session and db:
            db.close()


@tool
def get_product_details(product_id: int) -> str:
    """
    Get detailed information about a specific product.

    Args:
        product_id: The product ID

    Returns:
        JSON string with product details
    """
    db = _current_session or SessionLocal()
    try:
        product = ProductService.get_or_cache_product(product_id, db)

        if not product:
            return json.dumps({"error": f"Product {product_id} not found"})

        return json.dumps({
            "id": product["id"],
            "title": product["title"],
            "price": product["price"],
            "category": product["category"],
            "description": product["description"],
            "image": product["image"],
        })
    finally:
        if not _current_session and db:
            db.close()


@tool
def add_to_cart(product_id: int = None, quantity: int = 1, reference: str = None) -> str:
    """
    Add a product to the shopping cart.

    Args:
        product_id: The product ID to add (optional if using reference)
        quantity: Number of items to add (default 1)
        reference: Ordinal/comparative reference like "first", "cheaper one" (optional)

    Returns:
        JSON string with operation result
    """
    db = _current_session or SessionLocal()
    try:
        # Resolve reference if provided (e.g., "the cheaper one")
        actual_product_id = product_id
        if reference and not product_id:
            state = get_session_state(_current_session_id)
            resolved = state.resolve_product_reference(reference)
            if resolved:
                actual_product_id = resolved["id"]
            else:
                return json.dumps({
                    "error": f"Could not resolve reference '{reference}'. "
                    "Please search for products first or specify a product ID."
                })

        if not actual_product_id:
            return json.dumps({"error": "Product ID or reference required"})

        # Get product details first
        product = ProductService.get_or_cache_product(actual_product_id, db)

        if not product:
            return json.dumps({"error": f"Product {actual_product_id} not found"})

        CartService.add_to_cart(
            _current_session_id,
            actual_product_id,
            quantity,
            product["title"],
            product["price"],
            db
        )

        return json.dumps({
            "success": True,
            "message": f"Added {quantity} of '{product['title']}' to cart",
            "product_id": actual_product_id,
            "quantity": quantity,
        })
    finally:
        if not _current_session and db:
            db.close()


@tool
def remove_from_cart(product_id: int) -> str:
    """
    Remove a product from the shopping cart.

    Args:
        product_id: The product ID to remove

    Returns:
        JSON string with operation result
    """
    db = _current_session or SessionLocal()
    try:
        CartService.remove_from_cart(_current_session_id, product_id, db)

        return json.dumps({
            "success": True,
            "message": f"Removed product {product_id} from cart",
            "product_id": product_id,
        })
    finally:
        if not _current_session and db:
            db.close()


@tool
def get_cart() -> str:
    """
    Get the current shopping cart for the session.

    Returns:
        JSON string with cart contents and totals
    """
    db = _current_session or SessionLocal()
    try:
        cart = CartService.get_cart(_current_session_id, db)
        return json.dumps(cart)
    finally:
        if not _current_session and db:
            db.close()


@tool
def compare_products(reference: str = None, product_ids: str = None) -> str:
    """
    Compare multiple products side-by-side.

    Args:
        reference: Ordinal reference like "first two", "top three" (optional)
        product_ids: Comma-separated product IDs to compare (optional)

    Returns:
        JSON string with comparison data
    """
    db = _current_session or SessionLocal()
    try:
        products_to_compare = []

        # Resolve reference if provided (e.g., "first two")
        if reference:
            state = get_session_state(_current_session_id)
            indices = state.resolve_product_indices(reference)
            if indices:
                products_to_compare = [
                    state.last_search_results[i] for i in indices
                    if i < len(state.last_search_results)
                ]
            else:
                return json.dumps({
                    "error": f"Could not resolve reference '{reference}'. "
                    "Try 'first two' or 'top three' after searching."
                })

        # Or use explicit product IDs
        elif product_ids:
            ids = [int(x.strip()) for x in product_ids.split(",")]
            for product_id in ids:
                product = ProductService.get_or_cache_product(product_id, db)
                if product:
                    products_to_compare.append({
                        "id": product["id"],
                        "title": product["title"],
                        "price": product["price"],
                        "category": product.get("category", ""),
                    })

        if not products_to_compare:
            return json.dumps({
                "error": "No products to compare. Search for products first."
            })

        # Store compared products for reference resolution
        state = get_session_state(_current_session_id)
        state.store_compared_products(products_to_compare)

        # Build comparison
        comparison = {
            "products": products_to_compare,
            "count": len(products_to_compare),
            "text": f"Comparing {len(products_to_compare)} products:",
        }

        # Add analysis
        if len(products_to_compare) >= 2:
            prices = [p["price"] for p in products_to_compare]
            cheapest = min(products_to_compare, key=lambda p: p["price"])
            most_expensive = max(products_to_compare, key=lambda p: p["price"])
            price_diff = most_expensive["price"] - cheapest["price"]

            analysis = {
                "cheapest": cheapest,
                "most_expensive": most_expensive,
                "price_difference": price_diff,
                "savings": f"Save ${price_diff:.2f} by choosing '{cheapest['title']}'",
            }
            comparison["analysis"] = analysis

        return json.dumps(comparison)

    finally:
        if not _current_session and db:
            db.close()


@tool
def clear_cart() -> str:
    """
    Clear all items from the shopping cart.

    Returns:
        JSON string with operation result
    """
    db = _current_session or SessionLocal()
    try:
        CartService.clear_cart(_current_session_id, db)

        return json.dumps({
            "success": True,
            "message": "Cart cleared",
        })
    finally:
        if not _current_session and db:
            db.close()


# List of all tools for binding to agent
TOOLS = [search_products, get_product_details, add_to_cart, remove_from_cart, get_cart, compare_products, clear_cart]
