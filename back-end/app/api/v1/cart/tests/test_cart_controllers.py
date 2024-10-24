import urllib.parse
import uuid
from gettext import translation

import pytest
from httpx import AsyncClient
import urllib


class TestMongoService:

    @pytest.mark.asyncio
    async def test_get_cart(self, client: AsyncClient):
        response = await client.get("/api/v1/cart/")
        assert response.status_code == 200
        cart_dict = response.json()
        assert cart_dict["items"] == []
        assert cart_dict["total_count"] == 0
        assert cart_dict["total_price"] == 0.0

    @pytest.mark.asyncio
    async def test_add_and_get_cart(self, client: AsyncClient, products):
        product = products[0]
        product_id = product.product_id
        payload = {
            "product_id": str(product_id),
            "count": 5,
        }
        response = await client.patch("/api/v1/cart/add", json=payload)
        assert response.status_code == 204

        response = await client.get("/api/v1/cart/")
        cart_dict = response.json()
        assert cart_dict["items"][0]["product_id"] == str(product_id)

        assert cart_dict["items"][0]["name"] in [
            translation.product_name for translation in product.translations
        ]

        assert cart_dict["items"][0]["price"] == product.price
        assert cart_dict["items"][0]["image_src"] == product.image_src
        assert cart_dict["items"][0]["total_price"] == product.price * 5
        assert cart_dict["total_price"] == product.price * 5
        assert cart_dict["total_count"] == 5

    @pytest.mark.asyncio
    async def test_add_duplicate_item(self, client: AsyncClient, products):
        product = products[0]
        payload = {
            "product_id": str(product.product_id),
            "count": 3,
        }
        response = await client.patch("/api/v1/cart/add", json=payload)
        assert response.status_code == 204

        # Add the same product again
        response = await client.patch("/api/v1/cart/add", json=payload)
        assert response.status_code == 204

        # Check the updated cart
        response = await client.get("/api/v1/cart/")
        cart_dict = response.json()
        assert cart_dict["items"][0]["count"] == 6
        assert cart_dict["total_count"] == 6

    @pytest.mark.asyncio
    async def test_add_item_with_zero_or_negative_quantity(
        self, client: AsyncClient, products
    ):
        product = products[0]

        # Add item with zero count
        payload_zero = {
            "product_id": str(product.product_id),
            "count": 0,
        }
        response = await client.patch("/api/v1/cart/add", json=payload_zero)
        assert response.status_code == 422

        # Add item with negative count
        payload_negative = {
            "product_id": str(product.product_id),
            "count": -1,
        }
        response = await client.patch("/api/v1/cart/add", json=payload_negative)
        assert response.status_code == 422  # Expecting failure due to negative quantity

    @pytest.mark.asyncio
    async def test_remove_non_existent_product(self, client: AsyncClient):
        non_existent_product_id = uuid.uuid4()  # Random non-existent UUID
        response = await client.delete(
            f"/api/v1/cart/product/{non_existent_product_id}"
        )
        assert response.status_code == 404  # Product not found in the cart

    @pytest.mark.asyncio
    async def test_delete_cart(self, client: AsyncClient, products):
        payload1 = {
            "product_id": str(products[0].product_id),
            "count": 5,
        }
        response = await client.patch("/api/v1/cart/add", json=payload1)
        assert response.status_code == 204

        payload2 = {
            "product_id": str(products[1].product_id),
            "count": 3,
        }
        response = await client.patch("/api/v1/cart/add", json=payload2)
        assert response.status_code == 204

        response = await client.delete(f"/api/v1/cart/product/{products[0].product_id}")
        assert response.status_code == 204

        response = await client.get("/api/v1/cart/")
        cart_dict = response.json()
        assert len(cart_dict["items"]) == 1
        assert cart_dict["items"][0]["product_id"] == str(products[1].product_id)
        assert cart_dict["items"][0]["count"] == 3

        # Deleting entire cart
        response = await client.delete("/api/v1/cart/")
        assert response.status_code == 204

        response = await client.get("/api/v1/cart/")
        cart_dict = response.json()
        assert len(cart_dict["items"]) == 0
        assert cart_dict["total_count"] == 0
        assert cart_dict["total_price"] == 0

    @pytest.mark.asyncio
    async def test_subtract_nonadded_item_in_cart(self, client: AsyncClient, products):
        # Add first product
        payload1 = {
            "product_id": str(products[0].product_id),
            "count": 2,
        }
        response = await client.patch("/api/v1/cart/add", json=payload1)
        assert response.status_code == 204

        # subtract product with another one that is not in the cart
        payload_subtract = {
            "product_id": str(products[1].product_id),
            "count": 4,
        }
        response = await client.patch(
            "/api/v1/cart/subtract_product", json=payload_subtract
        )
        assert response.status_code == 204

        # Check if substitution was successful
        response = await client.get("/api/v1/cart/")
        cart_dict = response.json()
        assert len(cart_dict["items"]) == 1
        assert cart_dict["items"][0]["product_id"] == str(products[0].product_id)
        assert cart_dict["items"][0]["count"] == 2
        assert cart_dict["total_count"] == 2
        assert cart_dict["total_price"] == products[0].price * 2

        payload_subtract = {
            "product_id": str(products[0].product_id),
            "count": 1,
        }
        response = await client.patch(
            "/api/v1/cart/subtract_product", json=payload_subtract
        )
        assert response.status_code == 204

        response = await client.get("/api/v1/cart/")
        cart_dict = response.json()
        assert len(cart_dict["items"]) == 1
        assert cart_dict["items"][0]["product_id"] == str(products[0].product_id)
        assert cart_dict["items"][0]["count"] == 1  # subtractd count
        assert cart_dict["total_count"] == 1
        assert cart_dict["total_price"] == products[0].price

        payload_subtract = {
            "product_id": str(products[0].product_id),
            "count": 10,  # more than in cart
        }

        response = await client.patch(
            "/api/v1/cart/subtract_product", json=payload_subtract
        )
        assert response.status_code == 204

        response = await client.get("/api/v1/cart/")
        cart_dict = response.json()
        assert len(cart_dict["items"]) == 0
        assert cart_dict["total_count"] == 0
        assert cart_dict["total_price"] == 0

    @pytest.mark.asyncio
    async def test_remove_product_from_empty_cart(self, client: AsyncClient):
        product_id = uuid.uuid4()  # Random non-existent product
        response = await client.delete(f"/api/v1/cart/product/{product_id}")
        assert response.status_code == 404  # Expecting not found

    @pytest.mark.asyncio
    async def test_add_multiple_items_to_cart(self, client: AsyncClient, products):
        payload1 = {
            "product_id": str(products[0].product_id),
            "count": 2,
        }
        response = await client.patch("/api/v1/cart/add", json=payload1)
        assert response.status_code == 204

        payload2 = {
            "product_id": str(products[1].product_id),
            "count": 3,
        }
        response = await client.patch("/api/v1/cart/add", json=payload2)
        assert response.status_code == 204

        response = await client.get("/api/v1/cart/")
        cart_dict = response.json()
        assert len(cart_dict["items"]) == 2
        assert cart_dict["total_count"] == 5

    @pytest.mark.asyncio
    async def test_clear_cart(self, client: AsyncClient, products):
        # Add products to cart
        payload1 = {
            "product_id": str(products[0].product_id),
            "count": 3,
        }
        response = await client.patch("/api/v1/cart/add", json=payload1)
        assert response.status_code == 204

        payload2 = {
            "product_id": str(products[1].product_id),
            "count": 2,
        }
        response = await client.patch("/api/v1/cart/add", json=payload2)
        assert response.status_code == 204

        # Clear the cart
        response = await client.delete("/api/v1/cart/")
        assert response.status_code == 204

        response = await client.get("/api/v1/cart/")
        cart_dict = response.json()
        assert len(cart_dict["items"]) == 0
        assert cart_dict["total_count"] == 0
        assert cart_dict["total_price"] == 0.0

    @pytest.mark.asyncio
    async def test_add_nonexistent_product_to_cart(self, client: AsyncClient):
        """Test adding a product that doesn't exist in the database to the cart."""
        non_existent_product_id = uuid.uuid4()
        payload = {
            "product_id": str(non_existent_product_id),
            "count": 2,
        }
        response = await client.patch("/api/v1/cart/add", json=payload)
        assert (
            response.status_code == 404
        )  # Expecting a not found error for the product

    @pytest.mark.asyncio
    async def test_subtract_product_insufficient_count(
        self, client: AsyncClient, products
    ):
        """Test substituting product with insufficient count in the cart."""
        # Add product 1 to the cart with count 3
        payload1 = {
            "product_id": str(products[0].product_id),
            "count": 3,
        }
        response = await client.patch("/api/v1/cart/add", json=payload1)
        assert response.status_code == 204

        # subtract with count higher than the count in the cart
        payload_subtract = {
            "product_id": str(products[0].product_id),
            "count": 5,  # Trying to subtract more than available
        }
        response = await client.patch(
            "/api/v1/cart/subtract_product", json=payload_subtract
        )
        assert response.status_code == 204

        # Check that the product was removed since the count to subtract was higher
        response = await client.get("/api/v1/cart/")
        cart_dict = response.json()
        assert len(cart_dict["items"]) == 0
        assert cart_dict["total_count"] == 0
        assert cart_dict["total_price"] == 0.0

    @pytest.mark.asyncio
    async def test_clear_cart_after_adding_items(self, client: AsyncClient, products):
        """Test clearing the cart after adding multiple items."""
        # Add products to cart
        payload1 = {
            "product_id": str(products[0].product_id),
            "count": 3,
        }
        response = await client.patch("/api/v1/cart/add", json=payload1)
        assert response.status_code == 204

        payload2 = {
            "product_id": str(products[1].product_id),
            "count": 2,
        }
        response = await client.patch("/api/v1/cart/add", json=payload2)
        assert response.status_code == 204

        # Clear the cart
        response = await client.delete("/api/v1/cart/")
        assert response.status_code == 204

        # Verify cart is empty
        response = await client.get("/api/v1/cart/")
        cart_dict = response.json()
        assert len(cart_dict["items"]) == 0
        assert cart_dict["total_count"] == 0
        assert cart_dict["total_price"] == 0.0

    @pytest.mark.asyncio
    async def test_clear_cart_merge(self, client: AsyncClient, products):
        payload1 = {
            "product_id": str(products[0].product_id),
            "count": 3,
        }
        response = await client.patch("/api/v1/cart/add", json=payload1)
        assert response.status_code == 204

        # logging in, the cart should be the same
        register_payload = {
            "email": "user@example.com",
            "password": "string",
            "is_active": True,
            "is_superuser": False,
            "is_verified": False,
            "username": "string",
        }

        register_response = await client.post(
            "/api/v1/auth/register", json=register_payload
        )
        assert register_response.status_code == 201

        login_payload = {"username": "user@example.com", "password": "string"}

        login_response = await client.post(
            "/api/v1/auth/login",
            data=login_payload,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert login_response.status_code == 204

        cart_response = await client.get("/api/v1/cart/")
        cart_dict = cart_response.json()
        product = products[0]

        assert cart_dict["items"][0]["total_price"] == product.price * 3
        assert cart_dict["total_price"] == product.price * 3
        assert cart_dict["total_count"] == 3

        payload1 = {
            "product_id": str(products[3].product_id),
            "count": 5,
        }
        response = await client.patch("/api/v1/cart/add", json=payload1)
        assert response.status_code == 204

        product = products[3]
        cart_response = await client.get("/api/v1/cart/")
        cart_dict = cart_response.json()

        assert cart_dict["total_price"] == products[3].price * 5 + products[0].price * 3
        assert cart_dict["total_count"] == 8

        logout_response = await client.post(
            "api/v1/auth/logout",
        )
        assert logout_response.status_code == 204

        cart_response = await client.get("/api/v1/cart/")
        cart_dict = cart_response.json()

        # after logout - cleared cart
        assert cart_dict["total_price"] == 0
        assert cart_dict["total_count"] == 0

        # add more products to see that they have been added to the user_id stored cart
        response = await client.patch("/api/v1/cart/add", json=payload1)
        assert response.status_code == 204

        login_response = await client.post(
            "/api/v1/auth/login",
            data=login_payload,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert login_response.status_code == 204

        cart_response = await client.get("/api/v1/cart/")
        cart_dict = cart_response.json()

        # after logout - cleared cart
        assert (
            cart_dict["total_price"] == products[3].price * 10 + products[0].price * 3
        )
        assert cart_dict["total_count"] == 13
