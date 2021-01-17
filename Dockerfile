FROM python:3.9.1

RUN pip install pipenv

COPY ./Pipfile /app/Pipfile
COPY ./Pipfile.lock /app/Pipfile.lock

WORKDIR /app

ENV PYTHONPATH "${PYTHONPATH}:/app"

RUN pipenv install --system --deploy --ignore-pipfile

COPY . /app
