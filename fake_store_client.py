"""Fake Store API client for fetching product data."""
import httpx
import asyncio

BASE_URL = "https://fakestoreapi.com"


async def fetch_all_products():
    """Fetch all products from Fake Store API."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/products")
        return response.json()


async def fetch_product_by_id(product_id: int):
    """Fetch a single product by ID from Fake Store API."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/products/{product_id}")
        return response.json()


async def fetch_products_by_category(category: str):
    """Fetch products by category from Fake Store API."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/products/category/{category}")
        return response.json()


async def fetch_categories():
    """Fetch all available categories from Fake Store API."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/products/categories")
        return response.json()


# Synchronous wrappers for use in non-async contexts
def get_all_products():
    """Synchronous wrapper to fetch all products."""
    return asyncio.run(fetch_all_products())


def get_product_by_id(product_id: int):
    """Synchronous wrapper to fetch a single product."""
    return asyncio.run(fetch_product_by_id(product_id))


def get_products_by_category(category: str):
    """Synchronous wrapper to fetch products by category."""
    return asyncio.run(fetch_products_by_category(category))


def get_categories():
    """Synchronous wrapper to fetch categories."""
    return asyncio.run(fetch_categories())
