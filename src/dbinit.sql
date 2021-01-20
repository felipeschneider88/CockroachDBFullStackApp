DROP DATABASE IF EXISTS movr CASCADE; 

CREATE DATABASE movr;

IMPORT TABLE movr.vehicles (
        id UUID PRIMARY KEY,
        last_longitude FLOAT8,
        last_latitude FLOAT8,
        battery INT8,
        last_checkin TIMESTAMP,
        in_use BOOL,
        vehicle_type STRING NOT NULL
    )
CSV DATA ('https://cockroach-university-public.s3.amazonaws.com/10000vehicles.csv')
    WITH delimiter = '|';
