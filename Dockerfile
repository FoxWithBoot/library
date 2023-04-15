FROM python:3.10-alpine

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app/biblioteka


ENV PYTHONUNBUFFERED 1

RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev

COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY . .
