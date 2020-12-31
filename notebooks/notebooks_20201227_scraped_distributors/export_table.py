import os

import psycopg2

import pandas as pd
from dotenv import load_dotenv

load_dotenv()

def import_table():
    query = "SELECT * FROM url, raw_markup WHERE url.id = raw_markup.url_id AND url.url NOT LIKE '%thomasnet.com%' AND url.url NOT LIKE '%tel:%' LIMIT 1024;"
    conn = psycopg2.connect(os.getenv("DatabaseUrl"))

    assert isinstance(query, str), (type(query), query)
    df = pd.read_sql(query, con=conn)

    print("df is: ", df)
    df.to_csv("./dump.csv")

if __name__ == "__main__":
    print("Export table")
    import_table()

