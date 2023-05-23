FROM python:3.8

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE 1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED 1

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

ENTRYPOINT [ "python3", "main.py" ]
