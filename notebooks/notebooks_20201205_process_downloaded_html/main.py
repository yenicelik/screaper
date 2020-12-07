"""
    Process downloaded html
"""
import pandas as pd

from random import randint

from screaper.resources.db import resource_database
from screaper.scraper.scraper import Scraper

scraper = Scraper()

def load_df():
    df = resource_database.get_all_indexed_documents()
    print("df head is: ", len(df))
    print(df.head())
    print("Df memory usage is: ", df.info())

    return df

def sample_htmls():
    row = df.sample()

    print("Row is: ")
    print(row)

    val_id = randint(10000, 99999)
    markup = row['markup'].values[0]

    # print("Markup is: ", markup)
    text_file = open("sample_{}.html".format(val_id), "w")
    text_file.write(markup)
    text_file.close()

    return markup

def preprocess_html(html):
    """
        Remove any occurrences of style and script from html
    """
    scraper.process(html)

if __name__ == "__main__":
    print("Starting to process the collected data")
    df = load_df()
    sample_markup = sample_htmls()
    preprocess_html(sample_markup)
