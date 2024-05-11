-- Create the merged_data table
CREATE TABLE merged_data (
    id INTEGER PRIMARY KEY,
    date DATETIME,
    cities VARCHAR,
    city_name VARCHAR,
    geography VARCHAR,
    views INTEGER,
    watch_time_hours FLOAT,
    average_view_duration VARCHAR
);
