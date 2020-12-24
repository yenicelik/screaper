"""
    Process downloaded html.

    We will apply NER on some of the htmls that we already downloaded.
    Some of the NER models include:

    - https://spacy.io/models/xx
"""
import tldextract
from numpy.random.mtrand import randint
from url_parser import get_base_url

from screaper.resources.db import Database
from screaper.scraper.scraper import Scraper

scraper = Scraper()
resource_database = Database()

def load_df():
    df = resource_database.get_all_indexed_documents()
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

    scraper.process(html, base_url)

def extract_organizations(html):

    # how to represent graphs in python?

    # Create a tree from the html

    # for each node of the tree, check if any entities are found

    # if no entities are found, delete the graph

    #

    # nlp = spacy.load("xx_ent_wiki_sm")
    pass

if __name__ == "__main__":
    print("Starting to process the collected data")
    # df = load_df()
    # sample_markup = sample_htmls(df)

    with open('/Users/david/screaper/notebooks/notebooks_20201205_process_downloaded_html/sample_21550.html', 'r') as file:
        html = file.read()

    preprocess_html(html)
