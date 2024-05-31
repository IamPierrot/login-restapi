import json

from src.models.ErrorModel import BadRequest, ErrorDesc, Invalidate
from src.routers import SECRET_KEY
from ..models.UserModel import UserModelDatabase, UserModelPost
from src.security.Hash import Hashing
from src.security import oauth2_scheme
from src.database import LoginDatabase
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from fastapi import APIRouter, Depends, status
from typing import Annotated

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

router = APIRouter(
    prefix='/auth',
    tags=['Login and Register']
)


user_collection = LoginDatabase['account']


def get_list_users() -> list[UserModelDatabase]:
    documents = list(user_collection.find())
    for doc in documents:
        doc["_id"] = str(doc["_id"])
        # doc = UserModelDatabase(**doc)
    return documents


def get_user(username: str):
    result = user_collection.find_one({"username": username})
    if result is None:
        return None
    result["_id"] = str(result["_id"])
    return UserModelDatabase(**result)


async def authenticate_user(username: str, password: str):
    user = get_user(username)
    if user is None:
        return False
    if not Hashing.check_password(user.password.get_secret_value(), password):
        return False
    return user


def generate_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + \
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({'expired': expire.timestamp()})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt, expire


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if datetime.now(timezone.utc) > datetime.fromtimestamp(payload['expired'], timezone.utc):
            raise Invalidate(ErrorDesc.INVALID_TOKEN)
        username = payload.get("sub")
        if username is None:
            raise Invalidate(ErrorDesc.INVALID_TOKEN)
        return get_user(username)
    except JWTError:
        raise Invalidate(ErrorDesc.INVALID_TOKEN)


@router.post('/register')
def create_new_user(user_input: UserModelPost):
    try:
        user_collection.insert_one({
            "username": user_input.username,
            "password": Hashing(user_input.password),
            "display_name": user_input.display_name
        })
    except Exception as e:
        print(e)
        raise BadRequest(detail=e)

    return JSONResponse({"data": user_input.model_dump(), "msg": "Create new account successfully!"})


@router.post('/login')
async def authorization_user(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise Invalidate(ErrorDesc.INVALID_USERNAME_PW)
    access_token, expired = generate_access_token(
        data={"sub": user.username.get_secret_value()})

    return JSONResponse(
        content={
            "accessToken": access_token,
            "tokenType": "bearer",
            "expired": expired.isoformat(sep="/")
        },
        status_code=status.HTTP_202_ACCEPTED
    )


@router.get('/user/me/')
async def get_user_information(current_user: UserModelDatabase = Depends(get_current_user)):
    return JSONResponse({"data": json.loads(current_user.model_dump_json())})


@router.put('user/{username}')
async def modify_user_information(username: str | None, current_user: UserModelDatabase = Depends(get_current_user)):
    if username is None or username != current_user.username:
        raise Invalidate(detail=ErrorDesc.INVALID_USERNAME_PW)


@router.get('/users')
async def get_all_users():
    return get_list_users()
