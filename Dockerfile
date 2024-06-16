FROM python:3.11.6-alpine3.18
LABEL maintainer="hornet240204@gmail.com"

ENV PYTHONNBUFFERED 1

RUN apk add --no-cache --update \
    build-base \
    postgresql-dev \
    netcat-openbsd \
    linux-headers

WORKDIR app/

COPY requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

RUN adduser \
    --disabled-password \
    --no-create-home \
    my_user

USER my_user
