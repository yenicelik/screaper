"""
    Extract all homepages from the database.
    We will then create a graph of entities from these pages
"""
import asyncio
import lxml
import os
import pandas as pd
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from lxml import html
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from screaper.core.main import Main
from screaper_resources.resources.db import Database
from screaper_resources.resources.entities import RawMarkup, URLEntity

load_dotenv()

db_url = os.getenv('DatabaseUrl')
engine = create_engine(db_url, encoding='utf8', pool_size=5, max_overflow=10)  # pool_timeout=1

Session = scoped_session(sessionmaker(autocommit=False, autoflush=True, expire_on_commit=False, bind=engine))
# Session.configure()
session = Session()

database = Database()

def import_homepages(reload=False):
    """
        Naive http / https identifiers.
        Completely ignores entities marked by urls like:
        - mailto:info@hi-tech-products.com
        - mailto:info@azseal.com
        - mailto:%20info@greenheck.com

        # TODO: Ignore arabic for now?
        # TODO: Do some sort of language identification for processes

    :return:
    """

    if os.path.isfile("./domain_entities.csv") and not reload:
        out = pd.read_csv("./domain_entities.csv")
        print(out[:15])
        print(len(out))

        print(out.columns)

        out = out['url'].tolist()

        return out

    # https://raw.githubusercontent.com/datasets/top-level-domain-names/master/top-level-domain-names.csv
    df = pd.read_csv("./top-level-domain-names.csv")
    print(df.head())

    top_level_domain_names = df['Domain'].tolist()
    top_level_domain_names.extend([
        ".de", ".gov", ".com.tr", ".org", ".net", ".int", ".edu", ".gov", ".mil", ".arpa",
    ])

    print(type(top_level_domain_names), len(top_level_domain_names), top_level_domain_names)

    top_level_domain_names = [x for x in top_level_domain_names if x[0] == "."]
    top_level_domain_names = ["\\" + x for x in top_level_domain_names if x[0] == "."]
    print("Top level domains are: ", top_level_domain_names[:3])

    regex = "((https:\/\/|http:\/\/)?[-a-zA-Z0-9+&#%~_|!:,.;]*(\.com|{})(\/)?)$".format("|".join(top_level_domain_names))
    print("regex is: ")
    print(regex)

    # query = "SELECT DISTINCT tpl[1] AS domain, tpl[2] AS protocol, tpl[3] AS top_level_domain_name  FROM ( SELECT regexp_matches(url.url, '((https:\/\/|http:\/\/)?[-a-zA-Z0-9+&#%~_|!:,.;]*(\.com)(\/)?)') AS tpl FROM url) a;"

    query = "SELECT * FROM url WHERE url.url ~ '{}';".format(regex)

    print("Query is: ", query)

    df = pd.read_sql_query(query, con=engine)

    print("Dataframe head is: ", df.head())
    print("Dataframe head is: ", len(df))

    df.to_csv("./domain_entities.csv")

    # return df['domain'].tolist()

def fetch_nonexistent_url_markups(url_list):
    # Fetch the markups for these URLs if not fetched
    # Add URLs to queue

    # Make it not skip the homepages!
    """
        UPDATE url_queue SET crawler_skip = FALSE WHERE url_queue.url_id IN (SELECT url_queue.url_id FROM url, url_queue WHERE url.url ~ '((https:\/\/|http:\/\/)?[-a-zA-Z0-9+&#%~_|!:,.;]*(\.com)(\/)?)$' AND url_queue.url_id = url.id);
    """

    database.create_url_entity(url_list)
    query_input_triplet_dict = dict((x, ("/", 0, 0)) for x in url_list)
    referral_input_triplet_dict = dict((x, "/") for x in url_list)
    print("Queue Input triplet dict is: ", list(query_input_triplet_dict.items())[:3])
    print("Queue Input triplet dict is: ", len(query_input_triplet_dict))
    print("Referral Input triplet dict is: ", list(referral_input_triplet_dict.items())[:3])
    print("Referral Input triplet dict is: ", len(referral_input_triplet_dict))

    database.create_url_queue_entity(url_skip_score_depth_tuple_dict=query_input_triplet_dict)
    database.create_referral_entity(target_url_referrer_url_tuple_list=referral_input_triplet_dict)

    # Run the main method for a bit:
    # (Dont forget to modify the queue accordingly!!!)
    main_obj = Main(database=database)
    asyncio.run(main_obj.run_main_loop())

def identify_entities(url_list):
    """
        Should definitely pull the URLs that were not pulled
    :return:
    """

    print("URL lists are: ", url_list)
    query = session.query(URLEntity.id, URLEntity.url, RawMarkup.markup)\
        .filter(URLEntity.id == RawMarkup.url_id)\
        .filter(URLEntity.url.in_(url_list))\

    print("Query is: ", query)

    query = query.all()

    print("Fetched this many items: ", len(query))

    entity_candidates = []
    for tpl in query:
        url_id, url, raw_markup = tpl

        # print(url_ids[:10], url_entity[:10], raw_markup[:10])
        # print(url_ids[:10], url_entity[:10], raw_markup[:10])

        # for each URL, identify the (1) title, (2) description (3) url, very simply from HTML
        soup = BeautifulSoup(raw_markup, 'html.parser')

        print("\nTitle and description are: ")
        print(url)
        
        title = ""

        html_doc = html.fromstring(raw_markup)
        # html_doc = etree.parse(raw_markup, htmlparser)
        # html_doc.xpath(xpathselector)

        title = html_doc.xpath('//meta[@property="og:site_name"]/@content')
        if not title:
            title = html_doc.xpath('//meta[@property="og:title"]/@content')
        if not title:
            title = html_doc.xpath('//meta[@property="title"]/@content')
        if not title:
            title = html_doc.xpath('//meta[name="title"]/@content')
        if not title:
            title = html_doc.xpath('/html/head/title/text()')

        description = html_doc.xpath('//meta[@property="og:description"]/@content')
        if not description:
            description = html_doc.xpath('//meta[@property="description"]/@content')
        if not description:
            description = html_doc.xpath('//meta[name="description"]/@content')
        if not description:
            description = html_doc.xpath('/html/head/description/text()')
        if not description:
            description = html_doc.xpath('/*/site-description/text()')

        title = title[0] if title else ""
        description = description[0] if description else ""

        print("Title, description", title, description)
        entity_candidates.append({
            "url_id": url_id,
            "title": title,
            "description": description
        })

    # Temporarily add these in a database
    database.create_actor_entity_candidate(entity_candidates)
    database.commit()

    # Pick one of
    # meta property = og:site_name
    # meta property = og:title
    # meta property = og:description

    # meta name ="title" title content=""
    # meta name ="description" title content=""

    # Continue until one is found

    # title - tag -> in header
    # description - tag -> in header

    # return url_entity, raw_markup


# TODO: Use extractive or abstractive summarization tools?
# -> for this, collect all sentences (that are longer than a threshold), and apply summarization.
# OR filter keywords with most information.



if __name__ == "__main__":
    print("Homepage extractor starting")

    url_list = import_homepages()
    # fetch_nonexistent_url_markups(url_list)
    identify_entities(url_list)
