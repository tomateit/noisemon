FROM python:3.8

ENV ENVIRONMENT=production

WORKDIR /code

RUN apt update && apt upgrade -y

RUN pip install 'poetry==1.1.7'

RUN poetry config virtualenvs.create false

COPY poetry.lock pyproject.toml /code/

RUN poetry install --no-dev

COPY ./ /code/

RUN /code/scripts/download_spacy_model.sh

COPY ./.env.docker ./.env

CMD ["python", "noisemon"]
