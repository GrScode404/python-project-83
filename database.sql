CREATE TABLE urls (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP NOT NULL
);

CREATE TABLE url_checks (
    id BIGSERIAL PRIMARY KEY,
    url_id INTEGER NOT NULL REFERENCES urls(id) ON DELETE CASCADE,
    status_code INTEGER,
    title VARCHAR(255),
    h1 VARCHAR(255),
    description VARCHAR(255),
    created_at TIMESTAMP NOT NULL
);