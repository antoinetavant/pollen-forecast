FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

COPY entrypoint.sh /entrypoint.sh
COPY entrypoint.migrate.sh /entrypoint.migrate.sh

RUN apt-get update && export DEBIAN_FRONTEND=noninteractive  \
    apt-get install -y libpq-dev gcc build-essential curl  gdal-bin libgdal-dev && \
    rm -rf /var/lib/apt/lists/*
    
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --no-install-project --no-dev

ADD . /app

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-dev

RUN curl -o /usr/local/bin/wait-for-it.sh https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh && \
    chmod +x /usr/local/bin/wait-for-it.sh

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000


ENTRYPOINT ["/entrypoint.sh"]
