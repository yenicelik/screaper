"""
    Implements the core module of screaper.

    The core module combines multiple logics:

    Create "global" objects, including database and the proxy-list.

    While True:
    - Batch-fetch requests from Postgres -> save inputs in a local buffer
    - Create a bunch of async http requests -> save output in a local buffer
    - Flush response of async requests to database
"""
