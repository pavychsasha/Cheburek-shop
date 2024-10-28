from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession


async def get_or_create(session: AsyncSession, model, **kwargs):
    """
    Tries to get an existing object or creates a new one if it doesn't exist.

    Args:
        session (AsyncSession): The active database session.
        model (Base): The ORM model class to search/create.
        kwargs: Field values to use when searching for an existing object.

    Returns:
        instance (model): The retrieved or newly created instance.
    """
    # Try to retrieve the object
    query = select(model).filter_by(**kwargs)
    result = await session.execute(query)
    instance = result.scalar_one_or_none()

    if instance:
        return instance  # Return the found instance

    # Object not found, create a new one
    instance = model(**kwargs)
    session.add(instance)
    try:
        await session.flush()  # Use flush to persist without committing
        return instance  # Return the new instance
    except IntegrityError:
        await session.rollback()  # Rollback if there's a race condition
        result = await session.execute(query)
        instance = result.scalar_one_or_none()
        if instance:
            return instance
        else:
            raise ValueError(
                f"Unable to create or retrieve the object for model {model.__name__} with parameters {kwargs}."
            )
