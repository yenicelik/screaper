-- Add indices, because we will work with indices
-- ALTER TABLE markup ADD COLUMN idx SERIAL;
-- ALTER TABLE url_task_queue ADD COLUMN idx SERIAL;

COPY url(url, engine_version)
FROM '/Users/david/screaper/data/raw/_url_entities.csv'
DELIMITER ','
CSV HEADER;