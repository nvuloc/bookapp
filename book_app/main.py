from typing import Annotated, Union
from datetime import date
from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError
from sqlalchemy.orm import Session

from . import crud, schemas, auth
from .database import SessionLocal


app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def require_authorization(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": 'Bearer'}
    )
    try: 
        token_data = auth.authorize_token(token)
    except (JWTError):
         raise credentials_exception
    
    db_user = crud.get_user_by_email(db, token_data.username)
    if db_user is None:
        raise credentials_exception


@app.get('/')
def hello():
    return {'author': 'Loc Nguyen Vu', 'email': 'nvuloc@gmail.com'}


@app.post('/register', response_model=schemas.User, tags=['auth'])
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        db_user = crud.create_user(db, user)
        return db_user
    except crud.RecordExistedException as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post('/token', response_model=schemas.Token, tags=['auth'])
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db)):
    try:
        user_auth = schemas.UserAuth(email=form_data.username, password=form_data.password)
        crud.get_user_with_authentication(db, user_auth)
    except crud.RecordNotFoundException:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    token = auth.create_access_token(user_auth)
    return {"access_token": token, "token_type": "bearer"}


@app.get("/books", response_model=list[schemas.BookDetail], tags=['book'])
def list_books(page: int = 1, 
               limit: int = 100,
               publish_date: Union[date, None] = None,
               author: Union[str, None] = None,
               db: Session = Depends(get_db)):
    filter = {
        'publish_date': publish_date,
        'author': author
    }
    books = crud.list_books(db, page=page, limit=limit, filter=filter)
    return books


@app.get("/books/{book_id}", response_model=schemas.BookDetail, tags=['book'])
def get_book(book_id: int, db: Session = Depends(get_db)):
    db_book = crud.get_book(db, book_id)
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
    return db_book


@app.post("/books", response_model=schemas.BookDetail, dependencies=[Depends(require_authorization)], tags=['book'])
def create_book(book: schemas.BookCreate, db: Session = Depends(get_db)):
    try:
        db_book = crud.create_book(db, book)
    except crud.RecordExistedException as e:
        raise HTTPException(status_code=400, detail=str(e))
    return db_book


@app.put("/books/{book_id}", response_model=schemas.BookDetail, dependencies=[Depends(require_authorization)], tags=['book'])
def update_book(book_id: int, book: schemas.BookUpdate, db: Session = Depends(get_db)):
    try:
        db_book = crud.update_book(db, book_id, book)
    except crud.RecordNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except crud.BookExistedException as e:
        raise HTTPException(status_code=400, detail=str(e))
    return db_book


@app.delete("/books/{book_id}", dependencies=[Depends(require_authorization)], tags=['book'])
def delete_book(book_id: int, db: Session = Depends(get_db)):
    try:
        crud.delete_book(db, book_id)
    except crud.RecordNotFoundException as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {'status': 'ok'}
