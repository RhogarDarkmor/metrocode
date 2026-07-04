FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml poetry.lock README.md ./
COPY src /app/src
RUN pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    poetry install --only main --no-interaction --no-ansi

ENV PYTHONPATH=/app/src

ENTRYPOINT ["python", "-m", "metrocode.app"]
