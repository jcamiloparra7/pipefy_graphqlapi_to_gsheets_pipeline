import json
import os
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