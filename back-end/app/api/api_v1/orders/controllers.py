from typing import Annotated
import uuid

from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models import sql_db_helper, Cart
from app.api.api_v1.cart.dependencies import mongo_cart
from app.api.api_v1.cart.schemas import CartOrder
from .schemas import OrderModel
from .services import OrderService

router = APIRouter(tags=["Orders"])


@router.get(
    "/",
    response_model=list[OrderModel],
    status_code=status.HTTP_200_OK,
)
async def get_orders(
    session: AsyncSession = Depends(sql_db_helper.session_dependency),
):
    orders = await OrderService.get_orders(session=session)
    return orders
    # return await OrderService.serialize_order_response(orders)


@router.post(
    "/",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def make_order(
    cart: Annotated[CartOrder, Depends(mongo_cart)],
    session: AsyncSession = Depends(sql_db_helper.session_dependency),
):
    return await OrderService.make_order(session=session, mongo_cart=cart)


@router.delete(
    "/",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_all_orders(
    session: AsyncSession = Depends(sql_db_helper.session_dependency),
):
    return await OrderService.delete_all_products(session=session)


@router.delete(
    "/{order_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_order(
    order_id: uuid.UUID,
    session: AsyncSession = Depends(sql_db_helper.session_dependency),
):
    return await OrderService.delete_order(session=session, order_id=order_id)
