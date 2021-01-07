"""
    Cleanup broken links and add depth parameter to all links
    (since seed)
"""

import os

import sqlalchemy
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.sql import func
from sqlalchemy.orm import scoped_session, sessionmaker

from screaper_resources.resources.entities import URLEntity, URLQueueEntity, URLReferralsEntity

load_dotenv()

db_url = os.getenv("DatabaseUrl")
engine = create_engine(db_url, encoding='utf8', pool_size=5, max_overflow=10)  # pool_timeout=1

Session = scoped_session(sessionmaker(autocommit=False, autoflush=True, expire_on_commit=False, bind=engine))
session = Session()


def func1_apply_queries():
    yield "ALTER TABLE url_queue ADD depth INTEGER NOT NULL DEFAULT -1;"
    # Add this as an index for faster indexing
    yield "CREATE INDEX ix_url_queue_depth ON url_queue(depth);"


def _make_depth__1():
    query = session.query(URLQueueEntity)
    query.update({URLQueueEntity.depth: -1}, synchronize_session=False)
    return True


def _make_depth_0(seed_ids):
    seed_items = session.query(URLQueueEntity) \
        .filter(URLEntity.id.in_(seed_ids)) \
        .filter(URLQueueEntity.url_id == URLEntity.id)
    seed_items.update({URLQueueEntity.depth: 0}, synchronize_session=False)
    return True


def _calculate_mean_depth():
    query = session.query(func.avg(URLQueueEntity.depth))
    return query.all()[0]


def _total_number_of_items_in_queue():
    query = session.query(URLQueueEntity).count()
    return query


def _remove_all_self_redirects():
    query = session.query(URLReferralsEntity) \
        .filter(URLReferralsEntity.referrer_url_id == URLReferralsEntity.target_url_id)

    query.delete(synchronize_session=False)


def _lookup_next(referrer_url_id, visited):
    # print("Refferer url id is: ", referrer_url_id)

    current_depth = session.query(URLQueueEntity.depth) \
        .filter(URLQueueEntity.url_id == referrer_url_id) \
        .one_or_none()
    if current_depth:
        current_depth = current_depth[0]
    else:
        return None, None

    assert current_depth >= 0, (
        current_depth,
        session.query(URLQueueEntity.url_id).filter(URLQueueEntity.url_id == referrer_url_id).one_or_none())

    query = session.query(URLQueueEntity) \
        .filter(URLReferralsEntity.referrer_url_id == referrer_url_id) \
        .filter(URLReferralsEntity.target_url_id == URLQueueEntity.url_id) \
        .filter(sqlalchemy.not_(URLReferralsEntity.target_url_id.in_(visited)))

    # Set the depth for all next items
    query.update({URLQueueEntity.depth: current_depth + 1}, synchronize_session=False)
    # session.commit()

    # Return the new URL ids
    query.all()

    query = [x.url_id for x in query]
    # print("Next ids are: ", query)

    return query, current_depth


def func2_breadth_first_search(seeds):
    exit(0)
    _remove_all_self_redirects()

    # Need to make sure we start clean
    _make_depth__1()

    # Find the corresponding starting items
    start_ids = session.query(URLEntity.id).filter(URLEntity.url.in_(seeds)).all()
    start_ids = [x[0] for x in start_ids]
    print("Start ids are: ", start_ids)
    _make_depth_0(start_ids)

    session.commit()

    # Make the start items to 0

    # Start the search
    # repeatedly iterate until there is no change in the average of the depths
    print("Mean depth is: ", _calculate_mean_depth())
    mean = -1  # Finish condition
    queue_ids = start_ids
    max_visited = None
    visited = set()
    last_depth = 0

    while True:
        # Calculate mean of depth

        # Calculate the depth at each step
        # Pops and gets at the same time
        # Do this many updates at the same time
        if len(visited) % 100 == 0:
            print("Depth, visited size and queue size are: ", last_depth, len(visited), len(queue_ids))
            print("Progress: ", len(visited), _total_number_of_items_in_queue())
            session.commit()

        lookup_id = queue_ids.pop(0)
        visited.add(lookup_id)
        next_ids, last_depth = _lookup_next(lookup_id, visited)
        if next_ids is None:
            continue

        # Update the depths here
        next_ids = [x for x in next_ids if x not in visited]

        queue_ids.extend(next_ids)

        if max_visited and len(visited) > max_visited:
            break

    exit(0)


def func3_breadth_first_search_by_flooding(seeds):
    _remove_all_self_redirects()

    # Need to make sure we start clean
    _make_depth__1()

    # Find the corresponding starting items
    start_ids = session.query(URLEntity.id).filter(URLEntity.url.in_(seeds)).all()
    start_ids = [x[0] for x in start_ids]
    print("Start ids are: ", start_ids)
    _make_depth_0(start_ids)

    session.commit()

    current_depth = 0

    total_updated_items = 0

    print("Total items in queue: ", session.query(URLQueueEntity).count())

    while True:

        # Get all items with this depth
        current_depth_items = session.query(URLQueueEntity.url_id) \
            .filter(URLQueueEntity.depth == current_depth) \

        # Get all items that are refferals of the above
        referrals = session.query(URLQueueEntity) \
            .filter(URLQueueEntity.url_id == URLReferralsEntity.target_url_id) \
            .filter(URLReferralsEntity.referrer_url_id.in_(current_depth_items)) \
            .filter(URLQueueEntity.depth == -1)

        updated_items = referrals.count()

        # print("\n\nReferrals are: ", referrals)
        referrals.update({URLQueueEntity.depth: max(current_depth, 0) + 1}, synchronize_session=False)

        # Only pick the ones that were not assigned yet (i.e. are -1)
        print(
            "Total updated: {} -- Current depth: {} -- Number of items with current depth: {} -- Items to be updated: {}".format(
                total_updated_items,
                current_depth,
                current_depth_items.count(),
                updated_items
            ))

        current_depth += 1
        total_updated_items += updated_items

        session.commit()

        if updated_items == 0:
            break

    # # If there are no more items in the referrals list, break
    # current_depth = session.query(URLQueueEntity.depth) \
    #     .filter(URLQueueEntity.url_id == referrer_url_id) \
    #     .one_or_none()
    # if current_depth:
    #     current_depth = current_depth[0]
    # else:
    #     return None, None
    #
    # assert current_depth >= 0, (
    #     current_depth,
    #     session.query(URLQueueEntity.url_id).filter(URLQueueEntity.url_id == referrer_url_id).one_or_none())
    #
    # query = session.query(URLQueueEntity) \
    #     .filter(URLReferralsEntity.referrer_url_id == referrer_url_id) \
    #     .filter(URLReferralsEntity.target_url_id == URLQueueEntity.url_id) \
    #     .filter(sqlalchemy.not_(URLReferralsEntity.target_url_id.in_(visited)))
    #
    # # Set the depth for all next items
    # query.update({URLQueueEntity.depth: current_depth + 1}, synchronize_session=False)
    # # session.commit()
    #
    # # Return the new URL ids
    # query.all()
    #
    # query = [x.url_id for x in query]
    # # print("Next ids are: ", query)
    #
    # return query, current_depth


if __name__ == "__main__":
    print("Working on adding a depth parameter to the database")

    seeds = [
        "/",
        "https://www.thomasnet.com/browse/machinery-tools-supplies/bearings-1.html",
        "https://www.go4worldbusiness.com/suppliers/bearing.html?region=worldwide",
    ]

    # func2_breadth_first_search(seeds)
    func3_breadth_first_search_by_flooding(seeds)
