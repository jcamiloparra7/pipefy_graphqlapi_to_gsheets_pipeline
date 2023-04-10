import json

import gspread
import gspread_dataframe as gsdf
from google.oauth2.service_account import Credentials

from utils import get_data_from_pipefy

credentials = Credentials.from_service_account_file(
    filename='./google_credentials.json',
    scopes=['https://www.googleapis.com/auth/spreadsheets']
)

gc = gspread.authorize(credentials)

with open('./table_ids.json', 'r') as json_file:
    table_ids = json.loads(json_file.read())


def lambda_handler(event, context):
    for table_name, table_identifiers in table_ids.items():
        df = get_data_from_pipefy(table_identifiers[0])
        sheet = gc.open_by_key(table_identifiers[1]).sheet1
        gsdf.set_with_dataframe(sheet, df)
        print(f'Succesfully uploaded table: {table_name}')
