from __future__ import annotations
import re

from pydantic import BaseModel, Field, EmailStr, field_validator
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
import uuid

if TYPE_CHECKING:
    from core.models import Order


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_]+$")
    email: EmailStr
    reward_points: int = Field(0, ge=0)

    @field_validator("username")
    def username_no_whitespace(cls, v):
        if re.search(r"\s", v):
            raise ValueError(
                "Username must not contain whitespace"
            )  # TODO: create custom exception for this
        return v

    @field_validator("email")
    def email_no_whitespace(cls, v):
        if re.search(r"\s", v):
            raise ValueError("Email must not contain whitespace")
        return v


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

    @field_validator("password")
    def password_no_whitespace(cls, v):
        if re.search(r"\s", v):
            raise ValueError("Password must not contain whitespace")
        return v


class UserInDBBase(UserBase):
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class ConfigDict:
        from_attributes = True


class UserUpdate(UserBase):
    user_id: uuid.UUID
    password: Optional[str] = Field(None, min_length=8)

    @field_validator("password")
    def password_no_whitespace(cls, v):
        if v and re.search(r"\s", v):
            raise ValueError("Password must not contain whitespace")
        return v


class UserPartialUpdate(BaseModel):
    username: Optional[str] = Field(
        None, min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_]+$"
    )
    email: Optional[EmailStr] = None
    reward_points: Optional[int] = Field(None, ge=0)
    password: Optional[str] = Field(None, min_length=8)

    @field_validator("username")
    def username_no_whitespace(cls, v):
        if v and re.search(r"\s", v):
            raise ValueError("Username must not contain whitespace")
        return v

    @field_validator("email")
    def email_no_whitespace(cls, v):
        if v and re.search(r"\s", v):
            raise ValueError("Email must not contain whitespace")
        return v

    @field_validator("password")
    def password_no_whitespace(cls, v):
        if v and re.search(r"\s", v):
            raise ValueError("Password must not contain whitespace")
        return v

    class ConfigDict:
        from_attributes = True


class User(UserInDBBase):
    orders: List[Order] = []
