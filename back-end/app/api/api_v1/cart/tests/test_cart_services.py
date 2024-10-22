import uuid
from unittest.mock import AsyncMock, patch

import pytest
from app.api.api_v1.cart.schemas import CartItemModify
from app.api.api_v1.cart.services import CartService
from app.core.exceptions import ProductCartNotFoundError
from app.core.models import Cart, CartItem
from beanie import PydanticObjectId


class TestCartService:
    @pytest.mark.asyncio
    async def test_merge_carts_non_overlapping_items(self):
        # Create product IDs
        product1_id = uuid.uuid4()
        product2_id = uuid.uuid4()

        # Create session cart item
        session_cart_item = CartItem(
            id=PydanticObjectId(),
            product_id=product1_id,
            name="Product 1",
            price=10.0,
            count=2,
            image_src="image1.jpg",
            total_price=20.0,
        )

        # Create user cart item
        user_cart_item = CartItem(
            id=PydanticObjectId(),
            product_id=product2_id,
            name="Product 2",
            price=15.0,
            count=1,
            image_src="image2.jpg",
            total_price=15.0,
        )

        # Create session cart
        session_cart = Cart(
            id=PydanticObjectId(),
            session_id=uuid.uuid4(),
            items=[session_cart_item],
            total_count=2,
            total_price=20.0,
        )

        # Create user cart
        user_cart = Cart(
            id=PydanticObjectId(),
            user_id=uuid.uuid4(),
            items=[user_cart_item],
            total_count=1,
            total_price=15.0,
        )

        # Mock save and delete methods
        with patch.object(
            Cart, "save", new=AsyncMock()
        ) as mock_cart_save, patch.object(
            Cart, "delete", new=AsyncMock()
        ) as mock_cart_delete:
            merged_cart = await CartService.merge_carts(session_cart, user_cart)

            # Assertions
            assert len(merged_cart.items) == 2
            assert merged_cart.total_count == 3
            assert merged_cart.total_price == 35.0  # 20.0 + 15.0
            mock_cart_delete.assert_awaited_once()
            mock_cart_save.assert_awaited()

    @pytest.mark.asyncio
    async def test_merge_carts_overlapping_items(self):
        # Create product ID
        product_id = uuid.uuid4()

        # Create session cart item
        session_cart_item = CartItem(
            id=PydanticObjectId(),
            product_id=product_id,
            name="Product",
            price=15.0,
            count=2,
            image_src="image.jpg",
            total_price=30.0,
        )

        # Create user cart item
        user_cart_item = CartItem(
            id=PydanticObjectId(),
            product_id=product_id,
            name="Product",
            price=15.0,
            count=3,
            image_src="image.jpg",
            total_price=45.0,
        )

        # Create session cart
        session_cart = Cart(
            id=PydanticObjectId(),
            session_id=uuid.uuid4(),
            items=[session_cart_item],
            total_count=2,
            total_price=30.0,
        )

        # Create user cart
        user_cart = Cart(
            id=PydanticObjectId(),
            user_id=uuid.uuid4(),
            items=[user_cart_item],
            total_count=3,
            total_price=45.0,
        )

        # Mock save and delete methods
        with patch.object(
            Cart, "save", new=AsyncMock()
        ) as mock_cart_save, patch.object(
            Cart, "delete", new=AsyncMock()
        ) as mock_cart_delete:
            merged_cart = await CartService.merge_carts(session_cart, user_cart)

            # Assertions
            assert len(merged_cart.items) == 1
            item = merged_cart.items[0]
            assert item.count == 5  # 2 + 3
            assert item.total_price == 75.0  # 15.0 * 5
            assert merged_cart.total_count == 5
            assert merged_cart.total_price == 75.0
            mock_cart_delete.assert_awaited_once()
            mock_cart_save.assert_awaited()

    @pytest.mark.asyncio
    async def test_get_session_cart_exists(self):
        session_id = uuid.uuid4()
        expected_cart = Cart(
            id=PydanticObjectId(),
            session_id=session_id,
            items=[],
            total_count=0,
            total_price=0.0,
        )

        # Mock Cart.find_one
        with patch.object(
            Cart, "find_one", new=AsyncMock(return_value=expected_cart)
        ) as mock_find_one:
            cart = await CartService.get_session_cart(session_id)
            assert cart == expected_cart
            mock_find_one.assert_awaited_once_with(
                Cart.session_id == session_id, fetch_links=True
            )

    @pytest.mark.asyncio
    async def test_get_session_cart_not_exists(self):
        session_id = uuid.uuid4()
        # Mock Cart.find_one to return None
        with patch.object(
            Cart, "find_one", new=AsyncMock(return_value=None)
        ) as mock_find_one:
            cart = await CartService.get_session_cart(session_id)
            assert cart is None
            mock_find_one.assert_awaited_once_with(
                Cart.session_id == session_id, fetch_links=True
            )

    @pytest.mark.asyncio
    async def test_get_users_cart_exists(self):
        user_id = uuid.uuid4()
        expected_cart = Cart(
            id=PydanticObjectId(),
            user_id=user_id,
            items=[],
            total_count=0,
            total_price=0.0,
        )

        # Mock Cart.find_one
        with patch.object(
            Cart, "find_one", new=AsyncMock(return_value=expected_cart)
        ) as mock_find_one:
            cart = await CartService.get_users_cart(user_id)
            assert cart == expected_cart
            mock_find_one.assert_awaited_once_with(
                Cart.user_id == user_id, fetch_links=True
            )

    @pytest.mark.asyncio
    async def test_get_users_cart_not_exists(self):
        user_id = uuid.uuid4()
        # Mock Cart.find_one to return None
        with patch.object(
            Cart, "find_one", new=AsyncMock(return_value=None)
        ) as mock_find_one:
            cart = await CartService.get_users_cart(user_id)
            assert cart is None
            mock_find_one.assert_awaited_once_with(
                Cart.user_id == user_id, fetch_links=True
            )

    @pytest.mark.asyncio
    async def test_get_cart_no_session_cart_no_user(self):
        session_id = uuid.uuid4()
        # Mock get_session_cart to return None
        with patch.object(
            CartService, "get_session_cart", new=AsyncMock(return_value=None)
        ) as mock_get_session_cart, patch.object(
            Cart, "save", new=AsyncMock()
        ) as mock_cart_save:
            cart = await CartService.get_cart(session_id)
            assert cart.session_id == session_id
            assert cart.items == []
            assert cart.total_count == 0
            assert cart.total_price == 0.0
            mock_get_session_cart.assert_awaited_once_with(session_id=session_id)
            mock_cart_save.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_get_cart_with_session_cart_no_user(self):
        session_id = uuid.uuid4()
        session_cart = Cart(
            id=PydanticObjectId(),
            session_id=session_id,
            items=[],
            total_count=0,
            total_price=0.0,
        )
        # Mock get_session_cart to return session_cart
        with patch.object(
            CartService, "get_session_cart", new=AsyncMock(return_value=session_cart)
        ) as mock_get_session_cart:
            cart = await CartService.get_cart(session_id)
            assert cart == session_cart
            mock_get_session_cart.assert_awaited_once_with(session_id=session_id)

    @pytest.mark.asyncio
    async def test_find_product_in_cart_found(self):
        product_id = uuid.uuid4()
        cart_item = CartItem(
            id=PydanticObjectId(),
            product_id=product_id,
            name="Product",
            price=10.0,
            count=1,
            image_src="image.jpg",
            total_price=10.0,
        )
        cart = Cart(
            id=PydanticObjectId(), items=[cart_item], total_count=1, total_price=10.0
        )
        item = await CartService.find_product_in_cart(cart, product_id)
        assert item == cart_item

    @pytest.mark.asyncio
    async def test_find_product_in_cart_not_found(self):
        product_id = uuid.uuid4()
        cart = Cart(id=PydanticObjectId(), items=[], total_count=0, total_price=0.0)
        item = await CartService.find_product_in_cart(cart, product_id)
        assert item is None

    @pytest.mark.asyncio
    async def test_subtract_product_from_cart_reduce_count(self):
        product_id = uuid.uuid4()
        cart_item = CartItem(
            id=PydanticObjectId(),
            product_id=product_id,
            name="Product",
            price=15.0,
            count=5,
            image_src="image.jpg",
            total_price=75.0,
        )
        cart = Cart(
            id=PydanticObjectId(), items=[cart_item], total_count=5, total_price=75.0
        )
        subtract_product = CartItemModify(product_id=product_id, count=2)

        with patch.object(
            CartItem, "save", new=AsyncMock()
        ) as mock_item_save, patch.object(
            Cart, "save", new=AsyncMock()
        ) as mock_cart_save:
            await CartService.subtract_product_from_cart(cart, subtract_product)

            # Assertions
            assert cart_item.count == 3
            assert cart_item.total_price == 45.0  # 15.0 * 3
            assert cart.total_count == 3
            assert cart.total_price == 45.0
            mock_item_save.assert_awaited_once()
            mock_cart_save.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_subtract_product_from_cart_remove_item(self):
        product_id = uuid.uuid4()
        cart_item = CartItem(
            id=PydanticObjectId(),
            product_id=product_id,
            name="Product",
            price=15.0,
            count=3,
            image_src="image.jpg",
            total_price=45.0,
        )
        cart = Cart(
            id=PydanticObjectId(), items=[cart_item], total_count=3, total_price=45.0
        )
        subtract_product = CartItemModify(product_id=product_id, count=3)

        with patch.object(
            CartService, "delete_product_from_cart", new=AsyncMock()
        ) as mock_delete_product_from_cart:
            await CartService.subtract_product_from_cart(cart, subtract_product)
            mock_delete_product_from_cart.assert_awaited_once_with(
                cart=cart, product_id=product_id
            )

    @pytest.mark.asyncio
    async def test_subtract_product_from_cart_product_not_in_cart(self):
        cart = Cart(id=PydanticObjectId(), items=[], total_count=0, total_price=0.0)
        subtract_product = CartItemModify(product_id=uuid.uuid4(), count=1)

        await CartService.subtract_product_from_cart(cart, subtract_product)
        # Should do nothing

    @pytest.mark.asyncio
    async def test_delete_product_from_cart_not_exists(self):
        cart = Cart(id=PydanticObjectId(), items=[], total_count=0, total_price=0.0)
        product_id = uuid.uuid4()

        with pytest.raises(ProductCartNotFoundError):
            await CartService.delete_product_from_cart(cart, product_id)

    @pytest.mark.asyncio
    async def test_delete_cart_items(self):
        cart = Cart(id=PydanticObjectId(), items=[], total_count=0, total_price=0.0)

        with patch.object(Cart, "delete", new=AsyncMock()) as mock_cart_delete:
            await CartService.delete_cart_items(cart)
            mock_cart_delete.assert_awaited_once()
