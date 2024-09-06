import auth.utils as auth_utils

from users.schemas import UserSchema

john = UserSchema(
    username="john",
    password=auth_utils.hash_password("qwerty"),
    email="john@example.com",
)


users_db: dict[str, UserWarning] = {
    john.username: john,
}
