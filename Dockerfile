FROM python:3.10.13-bullseye


# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /cashflow/

COPY . /cashflow/



RUN pip install poetry

RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi


WORKDIR /cashflow/cashflow/

EXPOSE 8082

ENV WATCHFILES_FORCE_POLLING=true




