from pydantic import BaseModel


class AdminCreate(BaseModel):
    email: str
    password: str
    model_config = {"extra": "forbid"}
