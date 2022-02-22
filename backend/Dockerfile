FROM python:3.7 AS base

WORKDIR /usr/srс/backend

RUN apt-get update && apt-get install --no-install-recommends -y \
    gettext \
    wait-for-it

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

FROM base AS dev

COPY . .
