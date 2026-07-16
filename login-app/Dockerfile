# — Stage 1: compile dependencies ——————————————————————————————
FROM python:3.11-slim-bookworm AS builder
WORKDIR /build

# Install build tools (only needed for compilation)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
# Install to a local folder — copied to runtime stage
RUN pip install --no-cache-dir --user -r requirements.txt

# — Stage 2: test (optional CI gate) ————————————————————————————
FROM builder AS tester
WORKDIR /build
COPY requirements-dev.txt .
RUN pip install --no-cache-dir --user -r requirements-dev.txt
COPY . .
ENV PATH=/root/.local/bin:$PATH
RUN python -m pytest tests/ -q --tb=short
# docker build --target tester .  →  fails the build if tests fail

# — Stage 3: lean runtime image —————————————————————————————————
FROM python:3.11-slim-bookworm AS runtime
WORKDIR /app

# Non-root user
RUN useradd -m -u 1000 appuser

# Copy ONLY installed packages and app code — not gcc/g++
COPY --from=builder /root/.local /home/appuser/.local
COPY --chown=appuser:appuser ./app /app/app
COPY --chown=appuser:appuser ./templates /app/templates
COPY --chown=appuser:appuser ./static /app/static

ENV PATH=/home/appuser/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    APP_USERNAME=admin \
    APP_PASSWORD=password123

USER appuser
EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
