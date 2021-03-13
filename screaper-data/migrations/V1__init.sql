-- Update updated_at
CREATE OR REPLACE FUNCTION set_updated_at ()
    RETURNS TRIGGER
    AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$
LANGUAGE plpgsql;

-- Create url table
CREATE TABLE url (
    -- Columns
    id serial NOT NULL,
    created_at timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    data text NOT NULL,
    status smallint NOT NULL,
    retries int NOT NULL DEFAULT 0,
    score int NOT NULL DEFAULT 0,
    depth int NOT NULL DEFAULT -1,
    -- Constraints
    PRIMARY KEY (id),
    UNIQUE (data)
);

-- Add url table indices
CREATE INDEX ON url (data);

-- Add url updated_at
CREATE TRIGGER set_url_updated_at
    AFTER UPDATE ON url
    FOR EACH ROW
    EXECUTE FUNCTION set_updated_at ();

-- Create url referral table
CREATE TABLE url_referral (
    -- Columns
    referrer_id int NOT NULL,
    referee_id int NOT NULL,
    created_at timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    count int NOT NULL,
    -- Constraints
    PRIMARY KEY (referrer_id, referee_id),
    FOREIGN KEY (referrer_id) REFERENCES url (id),
    FOREIGN KEY (referee_id) REFERENCES url (id)
);

-- Add url_referral updated_at
CREATE TRIGGER set_url_referral_updated_at
    AFTER UPDATE ON url_referral
    FOR EACH ROW
    EXECUTE FUNCTION set_updated_at ();

-- Create markup table
CREATE TABLE markup (
    -- Columns
    url_id int NOT NULL,
    created_at timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    raw text NOT NULL,
    processed text,
    status smallint NOT NULL,
    -- Constraints
    PRIMARY KEY (url_id),
    FOREIGN KEY (url_id) REFERENCES url (id)
);

-- Add markup updated_at
CREATE TRIGGER set_markup_updated_at
    AFTER UPDATE ON markup
    FOR EACH ROW
    EXECUTE FUNCTION set_updated_at ();

