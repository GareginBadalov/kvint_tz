FROM python:3.11

WORKDIR /app

COPY poetry.lock pyproject.toml /app/

RUN pip install poetry

RUN poetry install --no-root

COPY .. /app

CMD poetry run python main.py