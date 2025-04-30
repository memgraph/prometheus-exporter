FROM python:3.9

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

RUN apt-get update \
  && apt-get -y upgrade \
  && python3 -m pip install --upgrade pip \
  && apt-get install -y curl \
  && curl -sSL https://install.python-poetry.org | python3 -

ENV PATH="/root/.local/bin:$PATH"

WORKDIR /code

COPY . .

RUN rm -rf .venv \
  && poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi

# Set an environment variable default to standalone
ENV DEPLOYMENT_TYPE=HA
ENV CONFIG_FILE=/code/ha_config.yaml

# Run main.py when the container launches
ENTRYPOINT ["sh", "-c", "python3 mg_exporter.py --type=$DEPLOYMENT_TYPE --config-file=$CONFIG_FILE"]
