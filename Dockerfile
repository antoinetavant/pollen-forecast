FROM python:3.12-slim-bookworm

WORKDIR /app

RUN apt update && export DEBIAN_FRONTEND=noninteractive  && \
    apt install -y libpq-dev gcc build-essential curl  gdal-bin libgdal-dev && \
    rm -rf /var/lib/apt/lists/*

COPY entrypoint.sh /entrypoint.sh
COPY entrypoint.migrate.sh /entrypoint.migrate.sh

COPY requirements.txt /tmp
RUN --mount=type=cache,target=/root/.cache \
    pip install -r /tmp/requirements.txt

ADD . /app

RUN --mount=type=cache,target=/root/.cache \
    pip install /app

RUN curl -o /usr/local/bin/wait-for-it.sh https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh && \
    chmod +x /usr/local/bin/wait-for-it.sh

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
