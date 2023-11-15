import bcrypt
import os

from datetime import datetime, timedelta
from jose import JWTError, jwt
from .schemas import UserAuth, TokenData

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES'))


def create_access_token(user: UserAuth):
    to_encode = {"sub": user.email}
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def authorize_token(token: str):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    username: str = payload.get("sub")
    if username is None:
        raise JWTError()
    token_data = TokenData(username=username)
    return token_data


def hash_password(password: str) -> str:
    hashed = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())
    return hashed.decode('utf8')


def validate_hash(input: str, hashed: str) -> bool:
    return bcrypt.checkpw(input.encode('utf8'), hashed.encode('utf8'))