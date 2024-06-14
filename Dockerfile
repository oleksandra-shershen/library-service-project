FROM python:3.12-alpine
LABEL maintainer="github.com/oleksandra-shershen/library-service-project"

ENV PYTHONUNBUFFERED 1

RUN apk add --no-cache --update \
    build-base \
    postgresql-dev \
    netcat-openbsd

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
