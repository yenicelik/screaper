"""
    Add breadth column depending on depth of urls
"""

SQL = """
    ALTER TABLE url_queue ADD score INTEGER NOT NULL DEFAULT 0;    -- CREATE INDEX url_queue.score;
    CREATE INDEX ix_url_queue_score ON url_queue(score);
"""

if __name__ == "__main__":
    print("Adding depth parameter for pseudo-BFS based on initial sites")

    "https://www.thomasnet.com/catalogs/mechanical-components-and-assemblies/bearings/",
    "https://www.go4worldbusiness.com/suppliers/bearing.html?region=worldwide",
