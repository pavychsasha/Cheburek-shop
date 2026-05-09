from typing import Annotated
import uuid

from fastapi import APIRouter, HTTPException, status, Depends, Security
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies.session import current_language
from app.core.models import sql_db_helper
from app.core.dependencies.cart import mongo_cart
from app.core.schemas.cart import CartOrder
from app.core.dependencies.authentication.fastapi_users_dependency import (
    current_active_superuser,
)

from app.core.schemas.orders import (
    order_address_params,
    OrderAddressInfo,
    ContactData,
    contact_data_params,
    OrderResponseModel,
    OrderStatusResponse,
    OrderStatusUpdate,
)
from .services import OrderService

router = APIRouter(tags=["Orders"])


@router.get(
    "/",
    response_model=list[OrderResponseModel],
    status_code=status.HTTP_200_OK,
)
async def get_orders(
    session: Annotated[AsyncSession, Depends(sql_db_helper.session_dependency)],
    language: Annotated[str, Depends(current_language)],
    superuser: Annotated[AsyncSession, Security(current_active_superuser)],
):
    orders = await OrderService.get_orders_response(session=session, language=language)
    return orders


@router.post(
    "/",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def make_order(
    contact_data: Annotated[ContactData, Depends(contact_data_params)],
    address: Annotated[OrderAddressInfo, Depends(order_address_params)],
    cart: Annotated[CartOrder, Depends(mongo_cart)],
    session: Annotated[AsyncSession, Security(sql_db_helper.session_dependency)],
):
    return await OrderService.make_order(
        contact_data=contact_data, address=address, session=session, mongo_cart=cart
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


@router.patch(
    "/{order_id}/status",
    response_model=OrderStatusResponse,
    status_code=status.HTTP_200_OK,
)
async def update_order_status(
    order_id: uuid.UUID,
    status_update: OrderStatusUpdate,
    session: Annotated[AsyncSession, Depends(sql_db_helper.session_dependency)],
    superuser: Annotated[AsyncSession, Security(current_active_superuser)],
):
    try:
        order = await OrderService.update_order_status(
            session=session,
            order_id=order_id,
            status=status_update.status,
        )
        return OrderStatusResponse(order_id=order.order_id, status=order.status)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
