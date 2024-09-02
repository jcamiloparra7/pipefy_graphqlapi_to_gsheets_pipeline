FROM python:3.10-slim

ARG pipefy_token

ENV PIPEFY_TOKEN=${pipefy_token}

WORKDIR /app

RUN pip install --upgrade pip

COPY requirements.txt /app/requirements.txt

RUN pip install -r requirements.txt

COPY src/*.py /app/
COPY service_account_key.json /app/service_account_key.json

CMD ["python", "pipes_pipefy_bq_workflow_tipo2.py"]