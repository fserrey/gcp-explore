from ftplib import FTP
from google.cloud import storage
from google.cloud import bigquery

import os
from io import StringIO, BytesIO
from datetime import datetime, timedelta
import pandas as pd
from dotenv import load_dotenv
load_dotenv()

FTP_HOST = os.getenv("FTP_HOST")
FTP_USER = os.getenv("FTP_USER")
FTP_PASS = os.getenv("FTP_PASS")

bucket_name = "my-bucket"
bucket_path = 'gs://' + bucket_name

project_id = "my_project"
dataset_id = "my_dataset"
table_name = "my_table"

yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')

def get_ftp(FTP_HOST, FTP_USER, FTP_PASS, yesterday):
    # initialize FTP session
    ftp = FTP(FTP_HOST, FTP_USER, FTP_PASS)
    # force UTF-8 encoding
    ftp.encoding = "utf-8"
    # switch to the directory we want
    ftp.cwd("my_directory")

    all_files = []

    for file_name in ftp.nlst():
        file_size = "N/A"
        try:
            ftp.cwd(file_name)      
        except Exception as e:
            ftp.voidcmd("TYPE I")
            file_size = ftp.size(file_name)
        # print(f"{file_name:20} -- {file_size} -- {ftp.size(file_name)}")
        all_files.append(file_name)

    for filename in all_files:
        date_ = filename.split("_")[1][:-4]
        file_date = datetime.strptime(date_, '%Y%m%d').date().isoformat().replace('-','')
        if file_date == yesterday:
            buffer = BytesIO() # We use BytesIO as we don't want to store locally the file, we just want it to be transformed and saved as .csv at Storage
            ftp.retrbinary(f"RETR {filename}", buffer.write)
            data = buffer.getvalue()
        else:
            pass 

    # store information as dict and dataframe previous to upload to gcp
    dict_ = {"date":file_date, "metric":int(data)}
    df = pd.DataFrame(data=dict_, index=[0])
    metric_filename = f"metric{file_date}.csv"
    return df, metric_filename

# GCP Storage
# On GCP -> 
client_storage = storage.Client()

def upload_storage(bucket_name, client_storage):
    aux = get_ftp(FTP_HOST, FTP_USER, FTP_PASS, yesterday)
    df = aux[0]
    global metric_filename 
    metric_filename = aux[1]
    
    bucket = client_storage.get_bucket(bucket_name)
    bucket.blob(f'{metric_filename}').upload_from_string(df.to_csv(index=False), 'text/csv')
    print("File uploaded into Storage")
    return metric_filename


# GCP Bigquery
client_bigquery = bigquery.Client()

def to_bq(project_id, dataset_id, table_name, client_bigquery):
    # define a BigQuery table    
    table_id = f"{project_id}.{dataset_id}.{table_name}"

    job_config = bigquery.LoadJobConfig(
        schema=[
            bigquery.SchemaField("date", "STRING"),
            bigquery.SchemaField("metric", "INTEGER"),
        ],
        skip_leading_rows=1,
        source_format=bigquery.SourceFormat.CSV,
    )

    uri = f"{bucket_path}/{metric_filename}"

    load_job = client_bigquery.load_table_from_uri(
        uri, table_id, job_config=job_config
    )  # Make an API request.

    load_job.result()  # Waits for the job to complete.

    destination_table = client_bigquery.get_table(table_id)  # Make an API request.
    print("Loaded {} rows.".format(destination_table.num_rows))
    print("File loaded in BQ")
    
def run_all(*args, **kwargs):
    #get_ftp(FTP_HOST, FTP_USER, FTP_PASS)
    upload_storage(bucket_name, client_storage)
    to_bq(project_id, dataset_id, table_name, client_bigquery)