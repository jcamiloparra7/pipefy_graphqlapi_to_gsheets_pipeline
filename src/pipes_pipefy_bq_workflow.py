import gspread
from google.oauth2.service_account import Credentials
from gspread_dataframe import get_as_dataframe
import pandas_gbq
from utils import make_valid_bq_field_names, get_data_pipes_from_pipefy

def main():
    credentials = Credentials.from_service_account_file(
            filename='service_account_key.json',
            scopes=['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/bigquery']
        )

    config_gsheet_id = '1hHZjxrYlgdXTHr6OWI2TM8kwWFmfp4M1oYJsqnwuou0'

    gc = gspread.authorize(credentials)

    config_base_datos = gc.open_by_key(config_gsheet_id).get_worksheet(1)

    db_config_df = get_as_dataframe(config_base_datos)

    for index, row in db_config_df.iterrows():
        if row['Valid']:
            slug_pipefy = int(row['Slug PIPEFY'])
            slug_informe = int(row['Slug INFORME'])
            tabla_id_bigquery = row['Tabla_id BIGQUERY']
            project_id_bigquery = row['Project_id BIGQUERY']

            df = get_data_pipes_from_pipefy(slug_pipefy, slug_informe)
            bq_df = make_valid_bq_field_names(df)

            pandas_gbq.to_gbq(bq_df, tabla_id_bigquery, project_id_bigquery, if_exists='replace', credentials=credentials)
            print(f"Data from Pipefy table {row['Nombre tabla']} has been uploaded")


if __name__ == "__main__":
    main()