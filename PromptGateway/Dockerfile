FROM python:3.11-slim

# Prevents Python from buffering stdout/stderr, so logs appear immediately.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN groupadd -r gateway && useradd -r -g gateway gateway

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN mkdir -p logs && chown -R gateway:gateway /app

USER gateway

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health', timeout=3)" || exit 1

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
