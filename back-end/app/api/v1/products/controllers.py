import uuid
from typing import Annotated
from fastapi import APIRouter, status, Depends, Query, Security
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models import sql_db_helper, User, redis_db_helper
from app.core.dependencies.session import current_language
from app.core.dependencies.authentication.fastapi_users_dependency import (
    current_active_superuser,
)

from .services import ProductsService
from app.core.dependencies.products import product_by_id
from app.core.schemas.products import (
    Product,
    ProductCreate,
    ProductUpdate,
    ProductPartialUpdate,
    ProductBulkCreate,
    ProductResponse,
    Pagination,
    pagination_params,
    ProductPaginatedResponse,
)

router = APIRouter(tags=["Products"])


@router.get(
    "/",
    response_model=ProductPaginatedResponse,
    status_code=status.HTTP_200_OK,
)
async def get_products(
    session: Annotated[AsyncSession, Depends(sql_db_helper.session_dependency)],
    current_language: Annotated[str, Depends(current_language)],
    pagination_params: Annotated[Pagination, Depends(pagination_params)],
):
    return await ProductsService.get_all_products_response(
        session=session,
        pagination_params=pagination_params,
        current_language=current_language,
    )


@router.get(
    "/search/", response_model=ProductPaginatedResponse, status_code=status.HTTP_200_OK
)
async def get_product_by_query(
    session: Annotated[AsyncSession, Depends(sql_db_helper.session_dependency)],
    current_language: Annotated[str, Depends(current_language)],
    pagination_params: Annotated[Pagination, Depends(pagination_params)],
    name: Annotated[str | None, Query(max_length=90)] = None,
    category: Annotated[str | None, Query(max_length=30)] = None,
    sort_by: Annotated[str | None, Query(max_length=30)] = None,
    order: Annotated[str | None, Query(max_length=30)] = None,
):
    return await ProductsService.get_searched_products_response(
        session=session,
        category=category,
        sort_by=sort_by,
        order=order,
        name=name,
        current_language=current_language,
        pagination_params=pagination_params,
    )


@router.get(
    "/similar",
    response_model=list[ProductResponse],
    status_code=status.HTTP_200_OK,
)
async def get_similar_products(
    session: Annotated[AsyncSession, Depends(sql_db_helper.session_dependency)],
    current_language: Annotated[str, Depends(current_language)],
    product_ids: Annotated[list[uuid.UUID] | None, Query()] = None,
    limit: Annotated[int, Query(ge=1, le=12)] = 4,
):
    return await ProductsService.get_similar_products_response(
        session=session,
        product_ids=product_ids or [],
        current_language=current_language,
        limit=limit,
    )


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
    return await ProductsService.create_product(session=session, product_in=product_in)


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
    return await ProductsService.bulk_create_product(
        session=session,
        products_in=products_in,
    )


@router.get(
    "/{product_id}/similar",
    response_model=list[ProductResponse],
    status_code=status.HTTP_200_OK,
)
async def get_similar_products_for_product(
    product_id: uuid.UUID,
    session: Annotated[AsyncSession, Depends(sql_db_helper.session_dependency)],
    current_language: Annotated[str, Depends(current_language)],
    limit: Annotated[int, Query(ge=1, le=12)] = 4,
):
    return await ProductsService.get_similar_products_response(
        session=session,
        product_ids=[product_id],
        current_language=current_language,
        limit=limit,
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
    return await ProductsService.update_product(
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
    return await ProductsService.update_product(
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
    await ProductsService.delete_product(session=session, product_id=product_id)


@router.delete(
    "/",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_products(
    product_ids: list[uuid.UUID],
    session: Annotated[AsyncSession, Depends(sql_db_helper.session_dependency)],
    superuser: Annotated[User, Security(current_active_superuser)],
) -> None:
    await ProductsService.delete_products(session=session, product_ids=product_ids)


@router.post("/invalidate_all_cache")
async def invalidate_all_cache(
    superuser: Annotated[User, Security(current_active_superuser)],
):
    await redis_db_helper.cache.remove_all_cache_keys()
