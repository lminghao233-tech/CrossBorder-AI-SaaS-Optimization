FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN useradd --create-home --uid 10001 appuser
WORKDIR /app
COPY pyproject.toml README.md ./
COPY core ./core
COPY config ./config
COPY knowledge ./knowledge
RUN pip install --no-cache-dir .
USER appuser
EXPOSE 8000
CMD ["uvicorn", "core.api:app", "--host", "0.0.0.0", "--port", "8000"]
