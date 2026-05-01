FROM python:3.13 AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_VERSION=1.8.5 \
    POETRY_HOME=/opt/poetry \
    POETRY_NO_INTERACTION=1

RUN apt-get update \
  && apt-get -y upgrade \
  && apt-get install -y --no-install-recommends curl \
  && rm -rf /var/lib/apt/lists/* \
  && curl -sSL https://install.python-poetry.org | python3 -

ENV PATH="$POETRY_HOME/bin:$PATH"

WORKDIR /build

COPY pyproject.toml poetry.lock ./

RUN poetry export --without dev --without-hashes --format requirements.txt --output requirements.txt \
  && pip install --no-cache-dir --target=/install --requirement requirements.txt


FROM gcr.io/distroless/python3-debian13:nonroot

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/code/site-packages \
    DEPLOYMENT_TYPE=HA \
    CONFIG_FILE=/code/ha_config.yaml

WORKDIR /code

COPY --from=builder --chown=nonroot:nonroot /install /code/site-packages
COPY --chown=nonroot:nonroot \
     mg_exporter.py \
     standalone_main.py standalone_model.py standalone_config.yaml \
     ha_main.py ha_model.py ha_config.yaml \
     ./
COPY --chown=nonroot:nonroot metrics /code/metrics

USER nonroot:nonroot

ENTRYPOINT ["python3", "/code/mg_exporter.py"]
