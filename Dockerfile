FROM python:3.8

ENV ENVIRONMENT=production

WORKDIR /code

RUN apt update && apt upgrade -y & apt install curl

RUN curl -sSL https://install.python-poetry.org | python3 -

RUN poetry config virtualenvs.create false

COPY poetry.lock pyproject.toml /code/

RUN poetry install

COPY ./ /code/

RUN /code/scripts/download_spacy_model.sh

COPY ./.env.docker ./.env

CMD ["python", "noisemon"]
