
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL
);

CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    title VARCHAR(255) NOT NULL,
    event_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    predicted_minutes INTEGER,
    google_event_id VARCHAR(255)
);

INSERT INTO users (username, password_hash)
VALUES ('test_user', 'temporary')
ON CONFLICT (username) DO NOTHING;
