--Create location_history table:
CREATE TABLE location_history (
    id UUID PRIMARY KEY,
    vehicle_id UUID REFERENCES vehicles(id) ON DELETE CASCADE,
    ts TIMESTAMP NOT NULL,
    longitude FLOAT8 NOT NULL,
    latitude FLOAT8 NOT NULL
);


--Migrate the data:
INSERT INTO movr.location_history (id, vehicle_id, ts, longitude, latitude)
SELECT gen_random_uuid(), id, last_checkin, last_longitude, last_latitude 
FROM vehicles;


--remove the safeguard when droping columns
SET sql_safe_updates = false;
--Remove the columns from vehicles table:

ALTER TABLE vehicles DROP COLUMN last_checkin,
    DROP COLUMN last_longitude,
    DROP COLUMN last_latitude;

--Add again the safe drop 
SET sql_safe_updates = true;