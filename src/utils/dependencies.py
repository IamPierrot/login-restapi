from fastapi import Depends
from src.security import oauth2_scheme


def get_token(token: str = Depends(oauth2_scheme)):
    ...
