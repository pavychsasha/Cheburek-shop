import pytest
from api_v1.users.schemas import UserCreate, UserPartialUpdate
from api_v1.users.services import (
    create_user,
    get_users,
    get_user_by_user_id,
    update_user,
    delete_user,
)


@pytest.mark.asyncio
class TestUserService:

    async def test_create_user(self, db_session):
        user_data = UserCreate(
            username="newuser", email="newuser@example.com", password="newpassword"
        )
        user = await create_user(db_session, user_data)
        assert user.username == "newuser"

    async def test_get_users(self, db_session, user_fixture):
        users = await get_users(db_session)
        assert len(users) >= 1

    async def test_get_user_by_user_id(self, db_session, user_fixture):
        user = await get_user_by_user_id(db_session, user_fixture.user_id)
        assert user.email == "test@example.com"

    async def test_update_user_partial(self, db_session, user_fixture):
        updated_data = UserPartialUpdate(email="updated@example.com")
        user = await update_user(db_session, user_fixture, updated_data, partial=True)
        assert user.email == "updated@example.com"

    async def test_delete_user(self, db_session, user_fixture):
        await delete_user(db_session, user_fixture.user_id)
        user = await get_user_by_user_id(db_session, user_fixture.user_id)
        assert user is None
