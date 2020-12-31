"""
    Exports the tables to CSVs s.t. we can normalize the data
"""
import pandas as pd

from screaper_resources.resources.db import resource_database
from screaper_resources.resources import URLEntity, RawMarkup, URLReferralsEntity, URLQueueEntity

datadir = "/Users/david/screaper/migrations/20201211_migration_normalize_db/"


def import_url_task_queue():
    print("Importing url task queue csv")
    df = pd.read_csv("/Users/david/screaper/data/raw/url_task_queue.csv")
    print("Imported url task queue csv")
    return df


def import_markup():
    print("Importing markup csv")
    df = pd.read_csv("/Users/david/screaper/data/raw/markup.csv")
    print("Imported markup csv")
    return df


def normalize_url_entities(df_url_task_queue, df_markup):
    # extract all urls from markup and the referral and normal items
    urls1 = df_url_task_queue['url'].tolist()
    urls2 = df_url_task_queue['referrer_url'].tolist()
    urls3 = df_markup['url'].tolist()
    urls = list(set(urls1 + urls2 + urls3))

    print("URLs are: ", len(urls))

    # Insert into database for each of these items
    print("Adding raw URLs")
    engine_version = "0.0.1"
    for url in urls:
        if url is None:
            continue
        if url != url:
            continue
        # print("url is: ", url)
        obj = URLEntity(
            url=url,
            engine_version=engine_version
        )
        resource_database.session.add(obj)

    print("Committing...")
    resource_database.commit()
    print("Done adding the URL Entities")

def normalize_markup(df_markup):
    print("Normalizing markups")

    for idx, row in df_markup.iterrows():

        # get the id of the row
        url_entity = resource_database.session.query(URLEntity)\
            .filter(URLEntity.url == row['url'])\
            .one_or_none()

        # if this is none, just skip
        if url_entity != url_entity:
            continue

        # print("url id is: ", url_id)

        # print("markup is: ", row['markup'])
        # Markup, remove the style and script tags

        # TODO: Add this to the new scraper version
        # soup = BeautifulSoup(row['markup'], "lxml")
        # for tag in soup():
        #     for attribute in ["script", "style"]:
        #         del tag[attribute]
        # markup = str(soup)
        # print("Sentinel is: ", row['spider_processing_sentinel'], row['spider_processing_sentinel'] == "t", type(row['spider_processing_sentinel']))

        obj = RawMarkup(
            url_id=url_entity.id,
            markup=row['markup'],
            spider_processing_sentinel=False,
            spider_processed_sentinel=False,
            spider_skip=False,
            version_spider=row['engine_version'],
        )
        resource_database.session.add(obj)

    print("Committing...")
    resource_database.commit()
    print("Done adding entries")

def normalize_referrals(import_url_task_queue):

    print("Normalizing referrals")

    for idx, row in import_url_task_queue.iterrows():

        if idx % 1000 == 0:
            print("Idx is: ", idx, len(import_url_task_queue))

        # get the id of the row
        url_entity = resource_database.session.query(URLEntity)\
            .filter(URLEntity.url == row['url'])\
            .one_or_none()

        target_url_entity = resource_database.session.query(URLEntity) \
            .filter(URLEntity.url == row['url']) \
            .one_or_none()

        # if this is none, just skip
        if url_entity != url_entity or target_url_entity != target_url_entity:
            continue

        obj = URLReferralsEntity(
            target_url_id=url_entity.id,
            referrer_url_id=target_url_entity.id
        )
        resource_database.session.add(obj)
    print("Committing...")
    resource_database.commit()
    print("Done adding entries!")

def normalize_queue(import_url_task_queue):

    print("Normalizing queue")

    for idx, row in import_url_task_queue.iterrows():

        if idx % 1000 == 0:
            print("Idx is: ", idx, len(import_url_task_queue))

        # get the id of the row
        url_entity = resource_database.session.query(URLEntity)\
            .filter(URLEntity.url == row['url'])\
            .one_or_none()

        # if this is none, just skip
        if url_entity != url_entity:
            continue

        # Check if object exists, if yes, add the retries and occurrences on top of each other
        url_queue_entity = resource_database.session.query(URLQueueEntity)\
            .filter(URLQueueEntity.url_id == url_entity.id)\
            .one_or_none()

        if url_queue_entity is None:
            obj = URLQueueEntity(
                url_id=url_entity.id,
                crawler_processing_sentinel=row['crawler_processing_sentinel'] == "t",
                crawler_processed_sentinel=row['crawler_processed_sentinel'] == "t",
                crawler_skip=row['crawler_skip'] == "t",
                retries=row['retries'],
                occurrences=row['occurrences'],
                version_crawl_frontier=row['engine_version'],
            )
            resource_database.session.add(obj)
        else:
            url_queue_entity.retries += row['retries']
            url_queue_entity.occurrences += row['occurrences']

    print("Committing...")
    resource_database.commit()
    print("Done adding entries!")

if __name__ == "__main__":
    print("Starting to export and normalize dataframes")

    # df1 = import_url_task_queue()
    # df2 = import_markup()
    # normalize_url_entities(df1, df2)

    # df2 = import_markup()
    # normalize_markup(df_markup=df2)

    # df1 = import_url_task_queue()
    # normalize_referrals(df1)

    # df1 = import_url_task_queue()
    # normalize_queue(df1)
