ARG pipefy_token

FROM python:3.10-slim

ENV PIPEFY_TOKEN=$pipefy_token

COPY src/*.py /

COPY service_account_key.json /service_account_key.json

COPY requirements_2.txt /requirements.txt

RUN pip install --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "./tables_pipefy_bq_workflow.py" ]