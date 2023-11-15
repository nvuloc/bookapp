FROM python:3.9-alpine

WORKDIR /srv
EXPOSE 8900

COPY setup.py /srv
COPY book_app /srv/book_app

RUN apk add --update musl-dev gcc cargo \
    && pip install -e .

ENTRYPOINT uvicorn book_app.main:app --host 0.0.0.0 --port 8900