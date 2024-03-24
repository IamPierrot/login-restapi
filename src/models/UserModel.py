from typing import Annotated
from bson import ObjectId
from pydantic import BaseModel, Field, SecretBytes, SecretStr


class UserModelDatabase(BaseModel):
    _id: Annotated[str | None, "the auto created unique Id of user's document"] = None
    username: Annotated[SecretStr, "user's name for login/register"]
    password: Annotated[SecretBytes, "hashed and encoded password of user"]
    display_name: str | None = Field(
        default=None, title="display name of user on UI/UX", max_length=12)

class UserModelPost(BaseModel):
    username: Annotated[str, "user's name for login/register"]
    password: Annotated[str, "string password of user"]
    display_name: str | None = Field(
        default=None, title="display name of user on UI/UX", max_length=12)
