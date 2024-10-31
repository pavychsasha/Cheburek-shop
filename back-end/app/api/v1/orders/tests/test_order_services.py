import pytest
import uuid
from app.api.v1.orders.services import OrderService
from app.api.v1.products.services import ProductsService
from app.core.models import Product, Cart, CartItem
from app.core.schemas.orders import ContactData, OrderAddressInfo
from app.core.schemas.cart import CartOrder, CartItemModel


class TestOrderService:

    @pytest.mark.asyncio
    async def test_make_order_with_cart_and_address(self, session, products):
        # Prepare contact data and address
        contact_data = ContactData(email="customer@example.com")
        address = OrderAddressInfo(
            street_name="Main St",
            street_number="123",
            apartment_number="4B",
            zip_code="12345",
            city="Sample City",
            state="Sample State",
            country="Sample Country",
        )

        # Create a cart with items
        cart_items = [
            CartItem(
                product_id=products[0].product_id,
                price=products[0].price,
                count=2,
                total_price=products[0].price * 2,
            ),
            CartItem(
                product_id=products[1].product_id,
                price=products[1].price,
                count=1,
                total_price=products[1].price,
            ),
        ]
        cart = Cart(
            items=cart_items,
            total_count=sum(item.count for item in cart_items),
            total_price=sum(item.total_price for item in cart_items),
        )

        # Make an order with the populated cart and address
        await OrderService.make_order(
            contact_data=contact_data,
            address=address,
            session=session,
            mongo_cart=cart,
        )
        new_order = await OrderService.get_orders(session=session)
        new_order = new_order[0]
        assert new_order.address.street_name == "Main St"
        assert new_order.email == "customer@example.com"
        assert new_order.total_price == cart.total_price
        assert new_order.total_count == cart.total_count
