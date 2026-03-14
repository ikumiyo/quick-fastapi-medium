FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock* README.md ./

RUN pip install --no-cache-dir uv \
    && (uv sync --frozen --no-dev --no-install-project || uv sync --no-dev --no-install-project)

COPY . .

RUN uv sync --frozen --no-dev || uv sync --no-dev

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
