FROM python:3.12

ENV ENVIRONMENT=production

WORKDIR /code

RUN apt update && apt upgrade -y & apt install curl

RUN curl -sSL https://install.python-poetry.org | python3 -

RUN poetry config virtualenvs.create false

COPY ./ ./

RUN poetry install

