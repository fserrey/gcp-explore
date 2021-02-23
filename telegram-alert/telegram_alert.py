from google.cloud import bigquery
import pandas as pd
from datetime import datetime, timedelta
import requests

TOKEN = "my_TOKEN"
chat_id = "000000000"
bq_client = bigquery.Client()

def query_table(bq_client = bq_client):    
    Q = """SELECT 
             my_metric AS yesterday_metric,
            (SELECT SUM(my_metric) FROM `project.dataset.table`) AS total_metric,
           FROM `project.dataset.table`
           WHERE date = FORMAT_DATE('%Y%m%d',DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY))"""

    query_job = bq_client.query(Q, location='EU').result()
    df = query_job.to_dataframe()
    return df

def send_message(message, TOKEN = TOKEN, chat_id = chat_id):
    send_text = 'https://api.telegram.org/bot' + TOKEN + '/sendMessage?chat_id=' + chat_id + '&parse_mode=Markdown&text=' + message
    response = requests.get(send_text)

    return response.json()


def app_results():
    df = query_table()
    
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%d-%m-%Y')
    yesterday_num = int(df.yesterday_metric)
    total_num = int(df.total_metric)
    
    message = f"""
Good morning!
Here is your daily performance on this matter: {yesterday_num:,} on {yesterday} and {total_num:,} since the start date. 
Cheers"""
    
    send_message(message)