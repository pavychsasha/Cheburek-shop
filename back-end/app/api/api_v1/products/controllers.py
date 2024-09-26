import uuid
from typing import Annotated
from fastapi import APIRouter, status, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models import sql_db_helper
from . import services
from .dependencies import product_by_id
from .schemas import (
    Product,
    ProductCreate,
    ProductUpdate,
    ProductPartialUpdate,
    ProductBulkCreate,
)

router = APIRouter(tags=["Products"])


@router.get(
    "/",
    response_model=list[Product],
    status_code=status.HTTP_200_OK,
)
async def get_products(
    session: AsyncSession = Depends(sql_db_helper.session_dependency),
):
    return await services.get_products(session=session)


@router.get("/search/", response_model=list[Product], status_code=status.HTTP_200_OK)
async def get_product_by_query(
    name: Annotated[str | None, Query(max_length=90)] = None,
    category: Annotated[str | None, Query(max_length=30)] = None,
    sort_by: Annotated[str | None, Query(max_length=30)] = None,
    order: Annotated[str | None, Query(max_length=30)] = None,
    session: AsyncSession = Depends(sql_db_helper.session_dependency),
):
    return await services.search_products(
        session=session,
        category=category,
        sort_by=sort_by,
        order=order,
        name=name,
    )


@router.post(
    "/",
    response_model=Product,
    status_code=status.HTTP_201_CREATED,
)
async def create_product(
    product_in: ProductCreate,
    session: AsyncSession = Depends(sql_db_helper.session_dependency),
):
    return await services.create_product(session=session, product_in=product_in)


@router.post(
    "/bulk_product_create/",
    response_model=ProductBulkCreate,
    status_code=status.HTTP_201_CREATED,
)
async def create_bulk_product(
    products_in: ProductBulkCreate,
    session: AsyncSession = Depends(sql_db_helper.session_dependency),
):
    return await services.bulk_create_product(
        session=session,
        products_in=products_in,
    )


@router.get(
    "/{product_id}/",
    response_model=Product,
    status_code=status.HTTP_200_OK,
)
async def get_product(
    product: Product = Depends(product_by_id),
):
    return product


@router.put(
    "/{product_id}/",
    status_code=status.HTTP_200_OK,
)
async def update_product(
    product_update: ProductUpdate,
    product: Product = Depends(product_by_id),
    session: AsyncSession = Depends(sql_db_helper.session_dependency),
):
    return await services.update_product(
        session=session,
        product=product,  # type: ignore
        product_update=product_update,
    )


@router.patch(
    "/{product_id}/",
    status_code=status.HTTP_200_OK,
)
async def update_product_partial(
    product_update: ProductPartialUpdate,
    product: Product = Depends(product_by_id),
    session: AsyncSession = Depends(sql_db_helper.session_dependency),
):
    return await services.update_product(
        session=session,
        product=product,  # type: ignore
        product_update=product_update,
        partial=True,
    )


@router.delete(
    "/{product_id}/",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_product(
    product_id: uuid.UUID,
    session: AsyncSession = Depends(sql_db_helper.session_dependency),
) -> None:
    await services.delete_product(session=session, product_id=product_id)
