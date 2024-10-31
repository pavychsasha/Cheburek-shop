import logging
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

# Setup logging
logger = logging.getLogger(__name__)


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
    # Try to retrieve the object first
    query = select(model).filter_by(**kwargs)
    result = await session.execute(query)
    instance = result.scalar_one_or_none()

    if instance:
        logger.info(f"Retrieved existing {model.__name__} with parameters {kwargs}.")
        return instance  # Return the found instance

    # Object not found; attempt to create a new one
    instance = model(**kwargs)
    session.add(instance)
    try:
        # Use flush to persist immediately without committing the transaction
        await session.flush()
        logger.info(f"Created new {model.__name__} with parameters {kwargs}.")
        return instance
    except IntegrityError as e:
        # Roll back in case of a race condition or other constraint issues
        await session.rollback()
        logger.warning(
            f"IntegrityError encountered: {e}. Retrying to retrieve {model.__name__}."
        )

        # Retry the query in case another transaction created it in the meantime
        result = await session.execute(query)
        instance = result.scalar_one_or_none()
        if instance:
            logger.info(
                f"Retrieved {model.__name__} on retry after IntegrityError with parameters {kwargs}."
            )
            return instance
        else:
            # Raise an error if the object cannot be created or retrieved
            logger.error(
                f"Failed to create or retrieve {model.__name__} with parameters {kwargs}."
            )
            raise ValueError(
                f"Unable to create or retrieve the object for model {model.__name__} with parameters {kwargs}. "
                f"Ensure foreign key dependencies are correct and try again."
            )
