FROM python:3.12-slim-bookworm

# OCI metadata
LABEL org.opencontainers.image.source="https://github.com/Nunii/claude-saas"

# Install minimal runtime deps + tini
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        tini \
        && \
    rm -rf /var/lib/apt/lists/*

# Non-root user
RUN groupadd --system --gid 10001 appuser && \
    useradd --system --uid 10001 --gid appuser --no-create-home --shell /sbin/nologin appuser

WORKDIR /app

# Install Python deps (good cache ordering: requirements before code)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY --chown=appuser:appuser app/ ./app/

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/healthz', timeout=2)" || exit 1

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
