from datetime import date
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from ..database import Base
from ..main import app, get_db
from .. import schemas

SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)
test_user = schemas.UserCreate(email="deadpool@example.com", password="chimichangas4life")
test_book = schemas.BookCreate(
    title="Introduction to Bash",
    author="Loc Nguyen Vu",
    publish_date=date(year=2023, month=10, day=11),
    isbn="1234567890123",
    price=10.99,
)


def test_user_register():
    """This test case checks whether the registration endpoint (/register) successfully registers a user with valid information.
    Steps:
        Sends a POST request to the /register endpoint with a valid email and password.
        Asserts that the response status code is 200.
        Parses the response JSON and asserts that the registered email matches the provided email.
    """
    response = client.post(
        "/register",
        json={"email": test_user.email, "password": test_user.password},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["email"] == "deadpool@example.com"


def test_user_login():
    """This test case checks whether the login endpoint (/token) successfully generates an access token for a user with correct credentials.
    Steps:
        Sends a POST request to the /token endpoint with a valid email and password.
        Asserts that the response status code is 200.
        Parses the response JSON and asserts the presence of the access token and token type.
    """
    response = client.post(
        "/token",
        data={"username": test_user.email, "password": test_user.password}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data


def test_user_login_wrong_password():
    """This test case checks whether the login endpoint (/token) returns a 400 status code when an incorrect password is provided.
    Steps:
        Sends a POST request to the /token endpoint with a valid email and an incorrect password.
        Asserts that the response status code is 400.
    """
    response = client.post(
        "/token",
        data={"username": test_user.email, "password": test_user.password + 'incorrect'}
    )
    assert response.status_code == 400, response.text


def test_list_books():
    """This test case checks whether the endpoint for listing books (/books) returns a 200 status code and a valid JSON list.
    Steps:
        Sends a GET request to the /books endpoint.
        Asserts that the response status code is 200.
        Asserts that the response contains a JSON list.
    """
    response = client.get("/books")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_book_without_authentication():
    """This test case checks whether creating a book without authentication returns a 401 status code.
    Steps:
        Sends a POST request to the /books endpoint without providing authentication.
        Asserts that the response status code is 401.
    """
    response = client.post(
        "/books",
        json=test_book.model_dump_json()
    )
    assert response.status_code == 401


def test_create_book_with_authentication():
    """This test case checks whether creating a book with valid authentication returns a 200 status code and the expected book details.
    Steps:
        Authenticates using a valid user's credentials.
        Sends a POST request to the /books endpoint with valid book details and authentication.
        Asserts that the response status code is 200.
        Asserts that the response contains the expected book details.
    """
    authresponse = client.post(
        "/token",
        data={"username": test_user.email, "password": test_user.password}
    )
    authdata = authresponse.json()
    
    bookresponse = client.post(
        "/books",
        json={
            "title": test_book.title,
            "author": test_book.author,
            "publish_date": test_book.publish_date.isoformat(),
            "isbn": test_book.isbn,
            "price": test_book.price},
        headers={
            "Authorization": "Bearer {token}".format(token=authdata['access_token']), 
            "Content-Type": "application/json; charset=utf-8"
        }
    )
    assert bookresponse.status_code == 200
    bookdata = bookresponse.json()
    assert "title" in bookdata
    assert bookdata['title'] == test_book.title
    


def test_create_book_with_authentication_duplicated():
    """This test case checks whether attempting to create a book with duplicated details returns a 400 status code with the appropriate error message.
    Steps:
        Authenticates using a valid user's credentials.
        Sends a POST request to the /books endpoint with book details that already exist.
        Asserts that the response status code is 400.
        Asserts that the response contains the expected error detail.
    """
    authresponse = client.post(
        "/token",
        data={"username": test_user.email, "password": test_user.password}
    )
    authdata = authresponse.json()
    
    bookresponse = client.post(
        "/books",
        json={
            "title": test_book.title,
            "author": test_book.author,
            "publish_date": test_book.publish_date.isoformat(),
            "isbn": test_book.isbn,
            "price": test_book.price},
        headers={
            "Authorization": "Bearer {token}".format(token=authdata['access_token']), 
            "Content-Type": "application/json; charset=utf-8"
        }
    )
    assert bookresponse.status_code == 400
    bookdata = bookresponse.json()
    assert "detail" in bookdata
    assert bookdata['detail'] == 'Book with title: Introduction to Bash, author: Loc Nguyen Vu existed'


def test_list_books():
    """This test case checks whether listing books after creating a book returns a list with at least one book.
    Steps:
        Authenticates using a valid user's credentials.
        Creates a book using a POST request to the /books endpoint.
        Sends a GET request to the /books endpoint.
        Asserts that the response status code is 200.
        Asserts that the response contains a JSON list with at least one book.
    """
    authresponse = client.post(
        "/token",
        data={"username": test_user.email, "password": test_user.password}
    )
    authdata = authresponse.json()
    
    bookresponse = client.post(
        "/books",
        json={
            "title": test_book.title + ' (1)',
            "author": test_book.author,
            "publish_date": test_book.publish_date.isoformat(),
            "isbn": test_book.isbn,
            "price": test_book.price},
        headers={
            "Authorization": "Bearer {token}".format(token=authdata['access_token']), 
            "Content-Type": "application/json; charset=utf-8"
        }
    )
    book = bookresponse.json()

    listresponse = client.get("/books")
    booklist = listresponse.json()
    assert listresponse.status_code == 200
    assert (len(booklist)) > 0


    detailresponse = client.get("/books/{id}".format(id=book['id']))
    book_1 = detailresponse.json()
    assert detailresponse.status_code == 200
    assert book_1['id'] == book['id']


def test_update_book():
    """This test case checks whether updating a book with valid authentication returns a 200 status code and updates the book details.
    Steps:
        Authenticates using a valid user's credentials.
        Creates a book using a POST request to the /books endpoint.
        Attempts to update the book using a PUT request to the /books/{id} endpoint with valid details and authentication.
        Asserts that the response status code is 200.
        Asserts that the updated book details match the expected values.
    """
    authresponse = client.post(
        "/token",
        data={"username": test_user.email, "password": test_user.password}
    )
    authdata = authresponse.json()
    
    bookresponse = client.post(
        "/books",
        json={
            "title": test_book.title + ' (2)',
            "author": test_book.author,
            "publish_date": test_book.publish_date.isoformat(),
            "isbn": test_book.isbn,
            "price": test_book.price
        },
        headers={
            "Authorization": "Bearer {token}".format(token=authdata['access_token']), 
            "Content-Type": "application/json; charset=utf-8"
        }
    )
    book = bookresponse.json()

    bookupdate_error = client.put(
        "/books/{id}".format(id=book['id']),
        json={
            "title": test_book.title + ' (2)',
            "author": test_book.author,
            "publish_date": date(2023, 1, 1).isoformat(),
            "isbn": test_book.isbn,
            "price": test_book.price}
    )
    assert bookupdate_error.status_code == 401

    bookupdate_success = client.put(
        "/books/{id}".format(id=book['id']),
        json={
            "title": test_book.title + ' (2)',
            "author": test_book.author,
            "publish_date": date(2023, 1, 1).isoformat(),
            "isbn": test_book.isbn,
            "price": test_book.price
        },
        headers={
            "Authorization": "Bearer {token}".format(token=authdata['access_token']), 
            "Content-Type": "application/json; charset=utf-8"
        }
    )
    assert bookupdate_success.status_code == 200
    bookupdated = bookupdate_success.json()
    assert bookupdated['publish_date'] == '2023-01-01'


def test_delete_book():
    """This test case checks whether deleting a book with valid authentication returns a 200 status code and the book is no longer accessible.
    Steps:
        Authenticates using a valid user's credentials.
        Creates a book using a POST request to the /books endpoint.
        Deletes the book using a DELETE request to the /books/{id} endpoint with valid authentication.
        Asserts that the response status code is 200.
        Attempts to retrieve the deleted book, and asserts that the response status code is 404.
    """
    authresponse = client.post(
        "/token",
        data={"username": test_user.email, "password": test_user.password}
    )
    authdata = authresponse.json()
    
    bookresponse = client.post(
        "/books",
        json={
            "title": test_book.title + ' (3)',
            "author": test_book.author,
            "publish_date": test_book.publish_date.isoformat(),
            "isbn": test_book.isbn,
            "price": test_book.price
        },
        headers={
            "Authorization": "Bearer {token}".format(token=authdata['access_token']), 
            "Content-Type": "application/json; charset=utf-8"
        }
    )
    book = bookresponse.json()

    bookdelete_error = client.delete(
        "/books/{id}".format(id=book['id'])
    )
    assert bookdelete_error.status_code == 401

    bookdelete_success = client.delete(
        "/books/{id}".format(id=book['id']),
        headers={
            "Authorization": "Bearer {token}".format(token=authdata['access_token']), 
            "Content-Type": "application/json; charset=utf-8"
        }
    )
    assert bookdelete_success.status_code == 200


    bookdetail_error = client.get("/books/{id}".format(id=book['id']))
    assert bookdetail_error.status_code == 404