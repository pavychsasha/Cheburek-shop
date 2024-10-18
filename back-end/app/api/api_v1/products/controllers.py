import uuid
from typing import Annotated
from fastapi import APIRouter, status, Depends, Query, Security
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models import sql_db_helper, User
from app.api.dependencies.session import current_language
from app.api.dependencies.authentication.fastapi_users import current_active_superuser

from . import services
from .dependencies import product_by_id
from .schemas import (
    Product,
    ProductCreate,
    ProductUpdate,
    ProductPartialUpdate,
    ProductBulkCreate,
    ProductResponse
)

router = APIRouter(tags=["Products"])


@router.get(
    "/",
    response_model=list[ProductResponse],
    status_code=status.HTTP_200_OK,
)
async def get_products(
    session: Annotated[AsyncSession, Depends(sql_db_helper.session_dependency)],
    current_language: Annotated[str, Depends(current_language)],
):
    products = await services.get_products(session=session)
    return await services.localize_products_list(products=products, language=current_language)


@router.get("/search/", response_model=list[ProductResponse], status_code=status.HTTP_200_OK)
async def get_product_by_query(
    session: Annotated[AsyncSession, Depends(sql_db_helper.session_dependency)],
    current_language: Annotated[str, Depends(current_language)],
    name: Annotated[str | None, Query(max_length=90)] = None,
    category: Annotated[str | None, Query(max_length=30)] = None,
    sort_by: Annotated[str | None, Query(max_length=30)] = None,
    order: Annotated[str | None, Query(max_length=30)] = None,
):
    products = await services.search_products(
        session=session,
        category=category,
        sort_by=sort_by,
        order=order,
        name=name,
    )
    return await services.localize_products_list(products=products, language=current_language)


@router.post(
    "/",
    response_model=Product,
    status_code=status.HTTP_201_CREATED,
)
async def create_product(
    product_in: ProductCreate,
    session: Annotated[AsyncSession, Depends(sql_db_helper.session_dependency)],
    superuser: Annotated[User, Security(current_active_superuser)],
):
    return await services.create_product(session=session, product_in=product_in)


@router.post(
    "/bulk_product_create/",
    response_model=ProductBulkCreate,
    status_code=status.HTTP_201_CREATED,
)
async def create_bulk_product(
    products_in: ProductBulkCreate,
    session: Annotated[AsyncSession, Depends(sql_db_helper.session_dependency)],
    superuser: Annotated[User, Security(current_active_superuser)],
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
    product: Annotated[Product, Depends(product_by_id)],
):
    return product


@router.put(
    "/{product_id}/",
    status_code=status.HTTP_200_OK,
)
async def update_product(
    product_id: uuid.UUID,
    product_update: ProductUpdate,
    session: Annotated[AsyncSession, Depends(sql_db_helper.session_dependency)],
    superuser: Annotated[User, Security(current_active_superuser)],
):
    return await services.update_product(
        product_id=product_id,
        product_update=product_update,
        session=session,
    )


@router.patch(
    "/{product_id}/",
    status_code=status.HTTP_200_OK,
)
async def update_product_partial(
    product_id: uuid.UUID,
    product_update: ProductPartialUpdate,
    session: Annotated[AsyncSession, Depends(sql_db_helper.session_dependency)],
    superuser: Annotated[User, Security(current_active_superuser)],
):
    return await services.update_product(
        session=session,
        product_id=product_id,  # type: ignore
        product_update=product_update,
        partial=True,
    )


@router.delete(
    "/{product_id}/",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_product(
    product_id: uuid.UUID,
    session: Annotated[AsyncSession, Depends(sql_db_helper.session_dependency)],
    superuser: Annotated[User, Security(current_active_superuser)],
) -> None:
    await services.delete_product(session=session, product_id=product_id)


@router.delete(
    "/",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_products(
    product_ids: list[uuid.UUID],
    session: Annotated[AsyncSession, Depends(sql_db_helper.session_dependency)],
    superuser: Annotated[User, Security(current_active_superuser)],
) -> None:
    await services.delete_products(session=session, product_ids=product_ids)
