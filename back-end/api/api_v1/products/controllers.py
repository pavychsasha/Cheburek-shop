import uuid
from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import db_helper
from . import services
from .dependencies import product_by_id
from .schemas import Product, ProductCreate, ProductUpdate

router = APIRouter(tags=["Products"])


@router.get(
    "/",
    response_model=list[Product],
    status_code=status.HTTP_200_OK,
)
async def get_products(
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    return await services.get_products(session=session)


@router.post(
    "/",
    response_model=Product,
    status_code=status.HTTP_201_CREATED,
)
async def create_product(
    product_in: ProductCreate,
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    return await services.create_product(session=session, product_in=product_in)


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
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    return await services.update_product(
        session=session,
        product=product,
        product_update=product_update,
    )


@router.patch(
    "/{product_id}/",
    status_code=status.HTTP_200_OK,
)
async def update_product_partial(
    product_update,
    product: Product = Depends(product_by_id),
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    return await services.update_product(
        session=session,
        product=product,
        product_update=product_update,
        partial=True,
    )


@router.delete(
    "/{product_id}/",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_product(
    product_id: uuid.UUID,
    session: AsyncSession = Depends(db_helper.session_dependency),
) -> None:
    await services.delete_product(session=session, product_id=product_id)
