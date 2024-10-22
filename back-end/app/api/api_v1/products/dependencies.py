from typing import Annotated
import uuid

from fastapi import Path, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models import sql_db_helper, Product

from . import services


async def product_by_id(
    product_id: Annotated[uuid.UUID, Path],
    session: Annotated[AsyncSession, Depends(sql_db_helper.session_dependency)],
) -> Product:
    product = await services.get_product(session=session, product_id=product_id)
    if product is not None:
        return product

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Product {product_id} not found!",
    )
