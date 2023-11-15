from typing import Union
from datetime import date, datetime
from pydantic import BaseModel


class BaseBook(BaseModel):
    title: str
    author: str
    publish_date: Union[date, None]
    isbn: str
    price: float


class BookCreate(BaseBook):
    pass


class BookUpdate(BaseBook):
    pass


class BookDetail(BaseBook):
    id: int
    created_at: datetime
    updated_at: datetime

    class ConfigDict :
        from_attributes = True


class User(BaseModel):
    email: str


class UserCreate(User):
    password: str


class UserAuth(UserCreate):
    pass


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str