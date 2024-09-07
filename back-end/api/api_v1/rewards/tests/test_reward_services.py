import pytest
from api.rewards.schemas import RewardCreate, RewardUpdate
from api.rewards.services import (
    create_reward,
    get_rewards,
    get_reward,
    update_reward,
    delete_reward,
)


@pytest.mark.asyncio
class TestRewardService:

    async def test_create_reward(self, db_session):
        reward_data = RewardCreate(
            name="new reward", description="new description", points_required=200
        )
        reward = await create_reward(db_session, reward_data)
        assert reward.name == "new reward"
        assert reward.description == "new description"
        assert reward.points_required == 200

    async def test_get_rewards(self, db_session, reward_fixture):
        rewards = await get_rewards(db_session)
        assert len(rewards) >= 1

    async def test_get_reward(self, db_session, reward_fixture):
        reward = await get_reward(db_session, reward_fixture.reward_id)
        assert reward.name == "Test Reward"

    async def test_update_reward(self, db_session, reward_fixture):
        updated_data = RewardUpdate(
            name="updated reward",
            description="updated description",
            points_required=300,
        )
        reward = await update_reward(
            db_session, reward_fixture, updated_data, partial=True
        )
        assert reward.name == "updated reward"
        assert reward.description == "updated description"
        assert reward.points_required == 300

    async def test_delete_reward(self, db_session, reward_fixture):
        await delete_reward(db_session, reward_fixture.reward_id)
        reward = await get_reward(db_session, reward_fixture.reward_id)
        assert reward is None
