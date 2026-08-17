FROM python:3.14.7-slim-bookworm@sha256:23c59390fc717bf09f9336908199a0ae75d9c4264bf296123f94ad772fea3b52 AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_ROOT_USER_ACTION=ignore

WORKDIR /build

COPY pyproject.toml README.md LICENSE ./
COPY galileo ./galileo

RUN python -m pip wheel --wheel-dir /wheels .


FROM python:3.14.7-slim-bookworm@sha256:23c59390fc717bf09f9336908199a0ae75d9c4264bf296123f94ad772fea3b52 AS runtime

ARG APP_UID=10001
ARG APP_GID=10001

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    GALILEO_ROOT=/app \
    PIP_ROOT_USER_ACTION=ignore \
    TZ=Asia/Shanghai

RUN groupadd --gid "${APP_GID}" galileo \
    && useradd --uid "${APP_UID}" --gid galileo --no-create-home --shell /usr/sbin/nologin galileo

WORKDIR /app

COPY --from=builder /wheels /wheels
RUN python -m pip install --no-cache-dir /wheels/* \
    && rm -rf /wheels

COPY --chown=galileo:galileo app.py ./
COPY --chown=galileo:galileo content ./content
COPY --chown=galileo:galileo static ./static
COPY --chown=galileo:galileo templates ./templates

USER galileo

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/healthz', timeout=3)"]

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--threads", "4", "--timeout", "30", "--worker-tmp-dir", "/tmp", "--no-control-socket", "--access-logfile", "-", "--error-logfile", "-", "app:app"]
