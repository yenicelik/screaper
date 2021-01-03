"""
    Process downloaded html.

    We will apply NER on some of the htmls that we already downloaded.
    Some of the NER models include:

    - https://spacy.io/models/xx
"""
import tldextract
from numpy.random.mtrand import randint

from screaper_resources.resources.db import Database
from screaper_entity_extraction.scraper.scraper import Scraper

scraper = Scraper()

raise NotImplementedError, "Need to implement another, non-asynchronous process for this"

resource_database = Database()

def load_df():
    df = resource_database.get_all_indexed_markups()
    print("df head is: ", len(df))
    print(df.head())
    print("Df memory usage is: ", df.info())

    return df

def sample_htmls(df):
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
    base_url = "https://thomasnet.com"
    base_url = tldextract.extract(base_url)

    processed_html = scraper.process(html, base_url)

    populate_index(processed_html=processed_html)

def populate_index(processed_html):

    # Iterate through processed html, collect all NERs,
    # Save all NERs into the database
    pass

if __name__ == "__main__":
    print("Starting to process the collected data")
    # df = load_df()
    # sample_markup = sample_htmls(df)

    with open('/Users/david/screaper/notebooks/notebooks_20201205_process_downloaded_html/sample_21550.html', 'r') as file:
        html = file.read()

    preprocess_html(html)
