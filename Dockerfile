FROM public.ecr.aws/lambda/python:3.9

COPY utils.py requirements.txt pipefy_gsheets_workflow.py google_credentials.json table_ids.json ${LAMBDA_TASK_ROOT}/

RUN pip install --upgrade pip

RUN pip install -r requirements.txt --target ${LAMBDA_TASK_ROOT}/

CMD [ "pipefy_gsheets_workflow.lambda_handler" ]