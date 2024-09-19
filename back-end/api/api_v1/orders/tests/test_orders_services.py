import pytest
from api.orders.schemas import OrderCreate
from api.orders.services import create_order, get_order, delete_order


@pytest.mark.asyncio
class TestOrderServices:
    async def test_create_order(self, db_session, user_fixture, product_fixture):
        order_data = OrderCreate(
            user_id=user_fixture.user_id,
        )
        order = await create_order(
            session=db_session,
            products_data={
                product_fixture.product_id: product_fixture.price,
            },
            order_create_data=order_data,
        )
        assert order.user_id == user_fixture.user_id

    async def test_get_order(self, db_session, order_fixture):
        order = await get_order(db_session, order_fixture.order_id)
        assert order.status == "pending"

    async def test_delete_order(self, db_session, order_fixture):
        await delete_order(db_session, order_fixture.order_id)
        order = await get_order(db_session, order_fixture.order_id)
        assert order is None
