# import pytest
# from api_v1..schemas import RewardCreate
# from your_package.services import create_reward, get_rewards, get_reward, delete_reward


# @pytest.mark.asyncio
# async def test_create_reward(db_session):
#     reward_data = RewardCreate(
#         name="newreward", description="new description", points_required=100
#     )
#     reward = await create_reward(db_session, reward_data)
#     assert reward.name == "newreward"


# @pytest.mark.asyncio
# async def test_get_rewards(db_session, reward_fixture):
#     rewards = await get_rewards(db_session)
#     assert len(rewards) == 1


# @pytest.mark.asyncio
# async def test_get_reward(db_session, reward_fixture):
#     reward = await get_reward(db_session, reward_fixture.reward_id)
#     assert reward.name == "Test Reward"


# @pytest.mark.asyncio
# async def test_delete_reward(db_session, reward_fixture):
#     await delete_reward(db_session, reward_fixture.reward_id)
#     reward = await get_reward(db_session, reward_fixture.reward_id)
#     assert reward is None
