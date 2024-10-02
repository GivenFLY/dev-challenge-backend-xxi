FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

ENV POETRY_VERSION=1.8.0
RUN curl -sSL https://install.python-poetry.org | python3 -

ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app

COPY pyproject.toml ./

RUN poetry config virtualenvs.create false && poetry install --no-root --no-interaction --no-ansi --with linux

COPY . .

EXPOSE 8080

CMD ["poetry", "run", "python", "manage.py", "runserver", "0.0.0.0:8080"]
