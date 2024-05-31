from enum import Enum
from typing import Annotated, Any
from fastapi import HTTPException, status


class ErrorDesc(Enum):
    INVALID_TOKEN = "Invalid Token"
    INVALID_USERNAME_PW = "Incorrect username or password"

class Invalidate(HTTPException):
    def __init__(self, detail: Annotated[ErrorDesc | Any, "The description about error"]):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )
        
class BadRequest(HTTPException):
    def __init__(self, detail:  Annotated[ErrorDesc | Any, "The description about error"]):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )
