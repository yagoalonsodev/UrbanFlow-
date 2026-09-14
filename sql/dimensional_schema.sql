CREATE TABLE IF NOT EXISTS dim_route (

    route_key SERIAL PRIMARY KEY,

    route_id VARCHAR(100) NOT NULL,

    route_short_name VARCHAR(100),

    route_long_name VARCHAR(255),

    route_type INTEGER,

    route_url VARCHAR(500),

    route_color VARCHAR(20),

    route_text_color VARCHAR(20),

    snapshot_date DATE NOT NULL,

    UNIQUE (route_id, snapshot_date)

);

CREATE TABLE IF NOT EXISTS dim_stop (

    stop_key SERIAL PRIMARY KEY,

    stop_id VARCHAR(100) NOT NULL,

    stop_code VARCHAR(100),

    stop_name VARCHAR(255),

    stop_lat DOUBLE PRECISION,

    stop_lon DOUBLE PRECISION,

    stop_url VARCHAR(500),

    location_type INTEGER,

    parent_station VARCHAR(100),

    wheelchair_boarding INTEGER,

    snapshot_date DATE NOT NULL,

    UNIQUE (stop_id, snapshot_date)

);

CREATE TABLE IF NOT EXISTS dim_service (

    service_key SERIAL PRIMARY KEY,

    service_id VARCHAR(100) NOT NULL,

    monday INTEGER,

    tuesday INTEGER,

    wednesday INTEGER,

    thursday INTEGER,

    friday INTEGER,

    saturday INTEGER,

    sunday INTEGER,

    start_date DATE,

    end_date DATE,

    snapshot_date DATE NOT NULL,

    UNIQUE (service_id, snapshot_date)

);

CREATE TABLE IF NOT EXISTS fact_trip (

    trip_key SERIAL PRIMARY KEY,

    trip_id VARCHAR(100) NOT NULL,

    route_key INTEGER NOT NULL,

    service_key INTEGER NOT NULL,

    trip_headsign VARCHAR(255),

    direction_id INTEGER,

    shape_id VARCHAR(100),

    wheelchair_accessible INTEGER,

    snapshot_date DATE NOT NULL,

    UNIQUE (trip_id, snapshot_date),

    CONSTRAINT fk_fact_trip_route

        FOREIGN KEY (route_key)

        REFERENCES dim_route(route_key),

    CONSTRAINT fk_fact_trip_service

        FOREIGN KEY (service_key)

        REFERENCES dim_service(service_key)

);

CREATE TABLE IF NOT EXISTS fact_stop_time (

    stop_time_key SERIAL PRIMARY KEY,

    trip_key INTEGER NOT NULL,

    stop_key INTEGER NOT NULL,

    arrival_time VARCHAR(20),

    departure_time VARCHAR(20),

    stop_sequence INTEGER NOT NULL,

    snapshot_date DATE NOT NULL,

    CONSTRAINT fk_fact_stop_time_trip

        FOREIGN KEY (trip_key)

        REFERENCES fact_trip(trip_key),

    CONSTRAINT fk_fact_stop_time_stop

        FOREIGN KEY (stop_key)

        REFERENCES dim_stop(stop_key)

);

CREATE INDEX IF NOT EXISTS idx_dim_route_route_id

    ON dim_route(route_id);


CREATE INDEX IF NOT EXISTS idx_dim_stop_stop_id

    ON dim_stop(stop_id);


CREATE INDEX IF NOT EXISTS idx_dim_service_service_id

    ON dim_service(service_id);


CREATE INDEX IF NOT EXISTS idx_fact_trip_route_key

    ON fact_trip(route_key);


CREATE INDEX IF NOT EXISTS idx_fact_trip_service_key

    ON fact_trip(service_key);


CREATE INDEX IF NOT EXISTS idx_fact_stop_time_trip_key

    ON fact_stop_time(trip_key);


CREATE INDEX IF NOT EXISTS idx_fact_stop_time_stop_key

    ON fact_stop_time(stop_key);