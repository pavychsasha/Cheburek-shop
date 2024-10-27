from typing import Annotated
import uuid

from fastapi import APIRouter, status, Depends, Security, Form
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models import sql_db_helper
from app.core.dependencies.cart import mongo_cart
from app.core.schemas.cart import CartOrder
from app.core.dependencies.authentication.fastapi_users_dependency import (
    current_active_superuser,
)

from app.core.schemas.orders import OrderModel, OrderAddress, order_address_params
from .services import OrderService

router = APIRouter(tags=["Orders"])


@router.get(
    "/",
    response_model=list[OrderModel],
    status_code=status.HTTP_200_OK,
)
async def get_orders(
    session: Annotated[AsyncSession, Depends(sql_db_helper.session_dependency)],
    superuser: Annotated[AsyncSession, Security(current_active_superuser)],
):
    orders = await OrderService.get_orders(session=session)
    return orders


@router.post(
    "/",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def make_order(
    address: Annotated[OrderAddress, Depends(order_address_params)],
    cart: Annotated[CartOrder, Depends(mongo_cart)],
    session: Annotated[AsyncSession, Security(sql_db_helper.session_dependency)],
):
    return await OrderService.make_order(
        address=address, session=session, mongo_cart=cart
    )


@router.delete(
    "/",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_all_orders(
    session: Annotated[AsyncSession, Depends(sql_db_helper.session_dependency)],
    superuser: Annotated[AsyncSession, Security(current_active_superuser)],
):
    return await OrderService.delete_all_products(session=session)


@router.delete(
    "/{order_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_order(
    order_id: uuid.UUID,
    session: Annotated[AsyncSession, Depends(sql_db_helper.session_dependency)],
    superuser: Annotated[AsyncSession, Security(current_active_superuser)],
):
    return await OrderService.delete_order(session=session, order_id=order_id)
