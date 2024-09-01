import json
import os
import re
import time
import io
from typing import Any, Dict, List

import pandas as pd
import requests

BASE_URL = "https://api.pipefy.com/graphql"
TOKEN = os.environ['PIPEFY_TOKEN']


def get_data_from_pipefy(table_id: int) -> pd.DataFrame:
    """
    Retrieves data from a Pipefy table and returns it as a pandas DataFrame.

    Args:
    table_id: An integer representing the ID of the table to retrieve data from.

    Returns:
    A pandas DataFrame containing the full table data.
    """
    # Initialize variables for pagination and API headers
    pages: List[pd.DataFrame] = []
    has_next_page: bool = True
    cursor_query: str = ""
    headers: dict = {
        "accept": "application/json",
        "Authorization":f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }

    # Retrieve data from the Pipefy API in chunks of up to 50 records
    while has_next_page:
        # Build and execute the GraphQL query to retrieve the next chunk of data
        query = '{{ table_records(table_id: {table_id} {cursor_query}){{ edges {{ node {{ record_fields{{ name value }} }} }} pageInfo {{ hasNextPage endCursor }} }} }}'
        payload = {"query": query.format(table_id=table_id, cursor_query=cursor_query)}
        response = requests.post(BASE_URL, json=payload, headers=headers)
        response_dict = json.loads(response.text)

        # Convert the response to a pandas DataFrame and append it to the list of pages
        df = convert_response_to_df(response_dict=response_dict)
        pages.append(df)

        # Check if there are more pages of data to retrieve
        has_next_page = response_dict['data']['table_records']['pageInfo']['hasNextPage']
        last_page_cursor = response_dict['data']['table_records']['pageInfo']['endCursor']
        cursor_query = f'after: "{last_page_cursor}"'

    # Combine all pages of data into a single pandas DataFrame and return it
    result = pd.concat(pages)
    return result


def convert_response_to_df(response_dict: Dict[str, Any]) -> pd.DataFrame:
    """
    Converts a response from a Pipefy GraphQL API call for table_records into a pandas DataFrame.

    Args:
    response_dict: A dictionary containing the response from the GraphQL API.

    Returns:
    A pandas DataFrame containing the table_records.

    """
    edges_list = response_dict['data']['table_records']['edges']
    records_list: List[Dict] = []
    for edge in edges_list:
        record_fields = edge['node']['record_fields']
        record_dict = {}
        for field in record_fields:
            record_dict[field['name']] = field['value']
        records_list.append(record_dict)

    df_response = pd.DataFrame.from_records(records_list)
    return df_response


def make_valid_bq_field_names(df):
    """
    Transforms the column names of a pandas DataFrame into valid BigQuery field names.
    
    Parameters:
    df (pd.DataFrame): The input DataFrame with original column names.
    
    Returns:
    pd.DataFrame: A new DataFrame with transformed column names.
    """
    def _sanitize_column_name(name):
        # Replace invalid characters with underscores
        name = re.sub(r'[^a-zA-Z0-9_]', '_', name)
        # Ensure the name starts with a letter or underscore
        if not re.match(r'^[a-zA-Z_]', name):
            name = '_' + name
        return name
    
    # Apply the transformation to each column name
    new_columns = [_sanitize_column_name(col) for col in df.columns]
    df.columns = new_columns
    return df


def get_data_pipes_from_pipefy(pipe_id, informe_id):

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }

    # First request to export the pipe report
    payload = {
        "query": f"""
            mutation {{
                exportPipeReport(input: {{pipeId: {pipe_id}, pipeReportId: {informe_id}}}) {{
                    pipeReportExport {{id}}
                }}
            }}
        """
    }

    response = requests.post(BASE_URL, json=payload, headers=headers)
    dict_response = response.json()
    id_response = dict_response['data']['exportPipeReport']['pipeReportExport']['id']

    # Second request to get the file URL
    payload = {
        "query": f"""
            {{
                pipeReportExport(id: "{id_response}") {{
                    fileURL
                    state
                    startedAt
                    requestedBy {{id}}
                }}
            }}
        """
    }

    response = requests.post(BASE_URL, json=payload, headers=headers)
    dict_response = response.json()
    URL_download = dict_response['data']['pipeReportExport']['fileURL']

    # Download the file with retries
    tries = 0
    while tries < 10:
        response = requests.get(URL_download, stream=True)
        if response.status_code == 404:
            time.sleep(10)
            tries += 1
        else:
            break

    file_content = response.content
    bytes_io = io.BytesIO(file_content)

    # Read the Excel file using pandas
    df = pd.read_excel(bytes_io, engine='openpyxl')
    df = df.replace(r'\[([^]]+)\]', value=r'\1', regex=True)
    df = df.replace(r'\[|\]', value=r'', regex=True)

    return df

