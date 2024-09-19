import uuid
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from core.models import Reward
from .schemas import RewardCreate, RewardUpdate, RewardPartialUpdate


async def get_rewards(session: AsyncSession) -> list[Reward]:
    """
    Retrieve all rewards from the database.
    """
    result = await session.execute(select(Reward))
    return result.scalars().all()


async def get_reward(session: AsyncSession, reward_id: uuid.UUID) -> Reward | None:
    """
    Retrieve a specific reward by its ID.
    """
    result = await session.execute(select(Reward).filter_by(reward_id=reward_id))
    return result.scalar_one_or_none()


async def create_reward(session: AsyncSession, reward_create: RewardCreate) -> Reward:
    """
    Create a new reward in the database.
    """
    reward = Reward(**reward_create.model_dump())
    session.add(reward)
    await session.commit()
    return reward


async def update_reward(
    session: AsyncSession,
    reward: Reward,
    reward_update: RewardUpdate | RewardPartialUpdate,
    partial: bool = False,
) -> Reward:
    """
    Update an existing reward in the database.
    """
    for name, value in reward_update.model_dump(exclude_unset=partial).items():
        setattr(reward, name, value)
    await session.commit()
    return reward


async def delete_reward(session: AsyncSession, reward_id: uuid.UUID) -> None:
    """
    Delete a reward from the database by its ID.
    """
    await session.execute(delete(Reward).where(Reward.reward_id == reward_id))
    await session.commit()
