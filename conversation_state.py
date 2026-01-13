"""Lightweight conversation state for multi-turn references.

This module manages conversation context for resolving ordinal and comparative
references without requiring complex state machines or databases.

Example:
  - User: "Search under $500"
  - Agent stores: last_search_results = [product1, product2, ...]

  - User: "Compare first two"
  - Agent resolves: products[0] and products[1] from last_search_results

  - User: "Add the cheaper one"
  - Agent resolves: min(product1, product2) by price
"""

import json
from typing import Optional, List, Dict, Any

# In-memory storage for session conversation state
# Format: {session_id: ConversationState}
_session_states: Dict[str, "ConversationState"] = {}


class ConversationState:
    """Manages conversation context for a single session."""

    def __init__(self, session_id: str):
        """Initialize conversation state for a session.

        Args:
            session_id: Unique identifier for the session
        """
        self.session_id = session_id
        self.last_search_results: List[Dict[str, Any]] = []
        self.last_compared_products: List[Dict[str, Any]] = []

    def store_search_results(self, products: List[Dict[str, Any]]) -> None:
        """Store search results for reference resolution.

        Args:
            products: List of products with at least id, title, price
        """
        self.last_search_results = [
            {
                "id": p["id"],
                "title": p["title"],
                "price": p["price"],
                "category": p.get("category", ""),
            }
            for p in products
        ]
        self.last_compared_products = []

    def store_compared_products(self, products: List[Dict[str, Any]]) -> None:
        """Store products that were last compared.

        Args:
            products: List of products being compared
        """
        self.last_compared_products = [
            {
                "id": p["id"],
                "title": p["title"],
                "price": p["price"],
            }
            for p in products
        ]

    def resolve_product_reference(self, reference: str) -> Optional[Dict[str, Any]]:
        """Resolve ordinal or comparative references to products.

        Handles references like:
          - "first" / "first product" → index 0
          - "second" / "second product" → index 1
          - "first two" → returns None (needs comparison tools)
          - "cheaper one" / "cheaper product" → min by price from compared
          - "more expensive one" → max by price from compared

        Args:
            reference: User's reference string (lowercased)

        Returns:
            Product dict with id, title, price or None if not resolvable
        """
        reference = reference.lower().strip()

        # Handle ordinal references (first, second, third, etc.)
        ordinal_map = {
            "first": 0,
            "second": 1,
            "third": 2,
            "fourth": 3,
            "fifth": 4,
        }

        for ordinal, index in ordinal_map.items():
            if ordinal in reference and "two" not in reference:  # "first two" is special
                if index < len(self.last_search_results):
                    return self.last_search_results[index]
                return None

        # Handle comparative references (cheaper, more expensive, etc.)
        if "cheaper" in reference or "cheapest" in reference or "lowest" in reference:
            if self.last_compared_products:
                return min(self.last_compared_products, key=lambda p: p["price"])
            if self.last_search_results:
                return min(self.last_search_results, key=lambda p: p["price"])
            return None

        if "expensive" in reference or "highest" in reference or "most" in reference:
            if self.last_compared_products:
                return max(self.last_compared_products, key=lambda p: p["price"])
            if self.last_search_results:
                return max(self.last_search_results, key=lambda p: p["price"])
            return None

        return None

    def resolve_product_indices(self, reference: str) -> Optional[List[int]]:
        """Resolve references to multiple products (for comparison).

        Handles references like:
          - "first two" → [0, 1]
          - "all" → [0, 1, 2, ...]

        Args:
            reference: User's reference string (lowercased)

        Returns:
            List of indices or None if not resolvable
        """
        reference = reference.lower().strip()

        if "first two" in reference or "top two" in reference:
            return [0, 1] if len(self.last_search_results) >= 2 else None

        if "top three" in reference or "first three" in reference:
            return [0, 1, 2] if len(self.last_search_results) >= 3 else None

        if reference in ["all", "everything"]:
            return list(range(len(self.last_search_results)))

        return None

    def to_json(self) -> str:
        """Serialize state to JSON for debugging."""
        return json.dumps(
            {
                "session_id": self.session_id,
                "last_search_results": self.last_search_results,
                "last_compared_products": self.last_compared_products,
            },
            indent=2,
        )


def get_session_state(session_id: str) -> ConversationState:
    """Get or create conversation state for a session.

    Args:
        session_id: Unique identifier for the session

    Returns:
        ConversationState for the session
    """
    if session_id not in _session_states:
        _session_states[session_id] = ConversationState(session_id)
    return _session_states[session_id]


def clear_session_state(session_id: str) -> None:
    """Clear conversation state for a session.

    Args:
        session_id: Unique identifier for the session
    """
    if session_id in _session_states:
        del _session_states[session_id]
