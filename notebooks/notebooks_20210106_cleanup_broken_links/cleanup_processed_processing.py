"""

"""

query = """
    SELECT * FROM url_queue, raw_markup WHERE raw_markup.url_id = url_queue.url_id;
"""