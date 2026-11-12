from typing import Optional
from pydantic import BaseModel, Field, field_validator
from constants.roles import Roles

EMAIL_PATTERN = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"


class TestUser(BaseModel):
    email: str = Field(..., pattern=EMAIL_PATTERN)
    fullName: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=8, max_length=20)
    passwordRepeat: str = Field(..., min_length=8, max_length=20)
    roles: list[Roles] = [Roles.USER]
    verified: Optional[bool] = None
    banned: Optional[bool] = None

    @field_validator("passwordRepeat")
    @classmethod
    def check_password_repeat(cls, value: str, info) -> str:
        if "password" in info.data and value != info.data["password"]:
            raise ValueError("passwordRepeat не совпадает с password")
        return value