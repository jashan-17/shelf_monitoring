CREATE TABLE raw_predictions (
    id SERIAL PRIMARY KEY,
    image_name VARCHAR(255),
    actual_label VARCHAR(50),
    predicted_label VARCHAR(50),
    confidence FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);