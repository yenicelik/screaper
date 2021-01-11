"""
    DELETE FROM url_queue WHERE url_queue.id NOT IN (SELECT id FROM (SELECT DISTINCT id, url_id FROM url_queue));

    DELETE FROM url_queue USING (
      SELECT MIN(ctid) as ctid, url_id
        FROM url_queue
        GROUP BY url_id HAVING COUNT(*) > 1
      ) b
      WHERE url_queue.url_id = b.url_id
      AND url_queue.ctid <> b.ctid
"""
