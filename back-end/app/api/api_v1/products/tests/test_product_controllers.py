import json
from httpx import AsyncClient
import pytest
from app.core.config import settings


@pytest.mark.asyncio
async def test_get_products(client):
    """Test the GET /products endpoint."""

    # Make a request to the `get_products` endpoint
    response = await client.get("/api/v1/products/")

    # Check that the response is OK (200)
    assert response.status_code == 200

    # Check that the response returns an empty list (assuming no products initially)
    assert response.json() == []


@pytest.mark.asyncio
async def test_create_product(client):
    """Test the POST /products endpoint to create a product."""

    # Define a product payload
    product_data = {
        "name": "Test Product",
        "description": "A test product description",
        "price": 9.99,
        "category": "Cheburek",
        "stock_quantity": 25,
        "image_src": "some_img_src",
    }

    # Send a POST request to create a product
    response = await client.post("/api/v1/products/", json=product_data)

    # Check that the response is CREATED (201)
    assert response.status_code == 201

    # Check that the returned product matches the input
    created_product = response.json()
    assert created_product["name"] == "Test Product"
    assert created_product["description"] == "A test product description"
    assert created_product["price"] == 9.99
    assert created_product["category"] == "Cheburek"


@pytest.mark.asyncio
async def test_search_product(client: AsyncClient):
    """Test the GET /products/search endpoint with query parameters."""

    # Define a product payload
    product_data = {
        "name": "Test Product",
        "description": "A test product description",
        "price": 9.99,
        "category": "Cheburek",
        "stock_quantity": 25,
        "image_src": "some_img_src",
    }

    # Send a POST request to create a product
    await client.post("/api/v1/products/", json=product_data)

    # Search for the product by name
    response = await client.get("/api/v1/products/search/", params={"name": "Test"})

    # Check that the response is OK (200)
    assert response.status_code == 200

    # Verify that the product is returned in the search results
    products = response.json()
    assert len(products) > 0
    assert products[0]["name"] == "Test Product"
