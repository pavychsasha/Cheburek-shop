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
        "image_src": "sme_img_src",
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


@pytest.mark.asyncio
async def test_create_product_missing_fields(client: AsyncClient):
    """Test POST /products with missing required fields."""

    # Define product payload with missing required field (e.g., "name")
    product_data = {
        "description": "A test product description",
        "price": 9.99,
        "category": "Cheburek",
        "stock_quantity": 25,
        "image_src": "some_img_src",
    }

    # Send a POST request to create a product
    response = await client.post("/api/v1/products/", json=product_data)

    # Check that the response is BAD REQUEST (422)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_product_invalid_price(client: AsyncClient):
    """Test POST /products with an invalid price (negative value)."""

    product_data = {
        "name": "Test Product",
        "description": "A test product description",
        "price": -5.00,  # Invalid price
        "category": "Cheburek",
        "stock_quantity": 25,
        "image_src": "some_img_src",
    }

    response = await client.post("/api/v1/products/", json=product_data)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_search_product_no_results(client: AsyncClient):
    """Test GET /products/search with a query that returns no results."""

    response = await client.get(
        "/api/v1/products/search/", params={"name": "NonExistentProduct"}
    )

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_update_product(client: AsyncClient):
    """Test PUT /products/{product_id} for updating a product."""

    # Create a product first
    product_data = {
        "name": "Old Product",
        "description": "Old description",
        "price": 5.99,
        "category": "SomeCategory",
        "stock_quantity": 10,
        "image_src": "old_img_src",
    }
    create_response = await client.post("/api/v1/products/", json=product_data)
    product_id = create_response.json()["product_id"]

    # Update the product
    updated_data = {
        "name": "Updated Product",
        "description": "Updated description",
        "price": 5.99,
        "category": "SomeCategory",
        "stock_quantity": 10,
        "image_src": "old_img_src",
    }
    response = await client.put(f"/api/v1/products/{product_id}/", json=updated_data)

    assert response.status_code == 200
    updated_product = response.json()
    assert updated_product["name"] == "Updated Product"
    assert updated_product["description"] == "Updated description"

    patch_data = {
        "name": "Patched Product",
        "description": "Patched description",
    }
    response = await client.patch(f"/api/v1/products/{product_id}/", json=patch_data)
    assert response.status_code == 200
    patched_product = response.json()
    assert patched_product["name"] == "Patched Product"
    assert patch_data["description"] == "Patched description"


@pytest.mark.asyncio
async def test_delete_product(client: AsyncClient):
    """Test DELETE /products/{product_id} to delete a product."""

    # Create a product first
    product_data = {
        "name": "Product to delete",
        "description": "Will be deleted",
        "price": 9.99,
        "category": "Cheburek",
        "stock_quantity": 25,
        "image_src": "delete_img_src",
    }
    create_response = await client.post("/api/v1/products/", json=product_data)
    product_id = create_response.json()["product_id"]

    # Delete the product
    response = await client.delete(f"/api/v1/products/{product_id}/")
    assert response.status_code == 204

    # Check that the product is no longer available
    get_response = await client.get(f"/api/v1/products/{product_id}/")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_bulk_create_products(client: AsyncClient):
    """Test POST /products/bulk_product_create/ for bulk creation of products."""

    bulk_product_data = {
        "products": [
            {
                "name": "Bulk Product 1",
                "description": "Bulk product 1 description",
                "price": 12.99,
                "category": "Bulk",
                "stock_quantity": 50,
                "image_src": "bulk_img_src_1",
            },
            {
                "name": "Bulk Product 2",
                "description": "Bulk product 2 description",
                "price": 8.99,
                "category": "Bulk",
                "stock_quantity": 100,
                "image_src": "bulk_img_src_2",
            },
        ]
    }

    response = await client.post(
        "/api/v1/products/bulk_product_create/", json=bulk_product_data
    )

    assert response.status_code == 201
    created_products = response.json()["products"]
    assert len(created_products) == 2
    assert created_products[0]["name"] == "Bulk Product 1"
