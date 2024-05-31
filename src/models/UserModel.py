from typing import Annotated, Any, Mapping
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, SecretBytes, SecretStr
from starlette.background import BackgroundTask


class UserModelDatabase(BaseModel):
    _id: Annotated[str | None,
                   "the auto created unique Id of user's document"] = None
    username: Annotated[SecretStr, "user's name for login/register"]
    password: Annotated[SecretBytes, "hashed and encoded password of user"]
    display_name: str | None = Field(
        default=None, title="display name of user on UI/UX", max_length=12)


class UserModelPost(BaseModel):
    username: Annotated[str, "user's name for login/register"]
    password: Annotated[str, "string password of user"]
    display_name: str | None = Field(
        default=None, title="display name of user on UI/UX", max_length=12)


class UserCreated(JSONResponse):
    def __init__(
        self,
            content: Any,
            status_code: int = 201,
            headers: Mapping[str, str] | None = None,
            media_type: str | None = None,
            background: BackgroundTask | None = None) -> None:
        super().__init__(
            content,
            status_code,
            headers,
            media_type,
            background
        )


class UserFound(JSONResponse):
    def __init__(
        self,
            content: Any,
            status_code: int = 201,
            headers: Mapping[str, str] | None = None,
            media_type: str | None = None,
            background: BackgroundTask | None = None) -> None:
        super().__init__(
            content,
            status_code,
            headers,
            media_type,
            background
        )
