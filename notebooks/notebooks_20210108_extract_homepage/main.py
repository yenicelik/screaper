"""
    Extract all homepages from the database.
    We will then create a graph of entities from these pages
"""
import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

load_dotenv()

db_url = os.getenv('DatabaseUrl')
engine = create_engine(db_url, encoding='utf8', pool_size=5, max_overflow=10)  # pool_timeout=1

# self.engine = screaper.resources.entities.engine
Session = scoped_session(sessionmaker(autocommit=False, autoflush=True, expire_on_commit=False, bind=self.engine))
# Session.configure()
session = Session()

def import_homepages():
    """
        Naive http / https identifiers.
        Completely ignores entities marked by urls like:
        - mailto:info@hi-tech-products.com
        - mailto:info@azseal.com
        - mailto:%20info@greenheck.com
    :return:
    """

    # https://raw.githubusercontent.com/datasets/top-level-domain-names/master/top-level-domain-names.csv
    df = pd.read_csv("./top-level-domain-names.csv")
    print(df.head())

    top_level_domain_names = df['Domain'].tolist()

    # TODO: Ignore arabic for now?
    # TODO: Do some sort of language identification for processes

    top_level_domain_names.extend([
        ".de", ".gov", ".com.tr", ".org", ".net", ".int", ".edu", ".gov", ".mil", ".arpa",
    ])
    print(type(top_level_domain_names), len(top_level_domain_names), top_level_domain_names)

    top_level_domain_names = [x for x in top_level_domain_names if x[0] == "."]
    # top_level_domain_names = top_level_domain_names[:]

    regex = "((https:\/\/|http:\/\/)?[-a-zA-Z0-9+&#%~_|!:,.;]*(\.com|{})(\/)?)".format("|".join(top_level_domain_names))

    print("regex is: ")
    print(regex)

    query = "SELECT DISTINCT tpl[1] AS domain, tpl[2] AS protocol, tpl[3] AS top_level_domain_name  FROM ( SELECT regexp_matches(url.url, '((https:\/\/|http:\/\/)?[-a-zA-Z0-9+&#%~_|!:,.;]*(\.com)(\/)?)') AS tpl FROM url) a;"

    print("Query is: ", query)

if __name__ == "__main__":
    print("Homepage extractor starting")

    import_homepages()
