from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import SecretBytes, SecretStr

from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt

from src.database import LoginDatabase
from src.utils.Hash import Hashing
from src.utils.dependencies import get_token, oauth2_scheme

from ..models.UserModel import UserModelDatabase, UserModelPost

router = APIRouter(
    prefix='/auth', tags=['Login and Register'])

user_collection = LoginDatabase['account']
temporatory_access: list[SecretBytes] = []

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def get_list_users():
    documents = list(user_collection.find())
    for doc in documents:
        doc["_id"] = str(doc["_id"])
    return documents


async def get_user(username: str):
    result = None
    try:
        result = user_collection.find_one({"username": username})
    except Exception as e:
        print(f'there was an error when try to find document: {e}')
    if result is None:
        return None
    result["_id"] = str(result["_id"])
    return UserModelDatabase(**result)


async def authenticate_user(username: str, password: str):
    user = await get_user(username)
    if user is None:
        return False
    if not Hashing.check_password(user.password.get_secret_value(), password):
        return False
    return user


def generate_temporary_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({'expired': expire.timestamp()})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt, expire


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await get_user(username)
    if user is None:
        raise credentials_exception
    return user


@router.post('/register')
async def create_new_user(user_input: UserModelPost):
    try:
        user_collection.insert_one({
            "username": user_input.username,
            "password": Hashing(user_input.password),
            "display_name": user_input.display_name
        }
        )
    except Exception as e:
        print(e)
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail={
            "error": str(e)
        })

    return JSONResponse({"data":user_input, "msg":f"Create new account successfully!"})


@router.post('/login')
async def authorization_user(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"content": "Incorrect username or password"},
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token, expired = generate_temporary_access_token(
        data={"sub": user.username.get_secret_value()})

    return JSONResponse(content={
        "accessToken": access_token,
        "tokenType": "bearer",
        "time_limit": expired.isoformat()
    })


@router.get('/user/me/')
async def modify_user_information(current_user: UserModelDatabase = Depends(get_current_user)):
    return JSONResponse({"data": current_user.model_dump_json()})


@router.get('/users')
async def get_all_users():
    return get_list_users()
