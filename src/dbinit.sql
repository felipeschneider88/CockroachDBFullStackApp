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



CREATE TABLE movr.location_history(
    id UUID PRIMARY KEY,
    vehicle_id UUID REFERENCES movr.vehicles(id) ON DELETE CASCADE,
    ts TIMESTAMP NOT NULL,
    longitude FLOAT8 NOT NULL,
    latitude FLOAT8 NOT NULL
);

INSERT INTO movr.location_history (id,
                                   vehicle_id,
                                   ts,
                                   longitude,
                                   latitude)
     SELECT gen_random_uuid(),
            id,
            last_checkin,
            last_longitude,
            last_latitude
       FROM movr.vehicles;

SET sql_safe_updates = false;

ALTER TABLE movr.vehicles
       DROP COLUMN last_checkin,
       DROP COLUMN last_longitude,
       DROP COLUMN last_latitude;

SET sql_safe_updates=true;
