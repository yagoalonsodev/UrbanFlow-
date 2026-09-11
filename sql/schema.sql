
-- ============================================================

-- URBANFLOW - ESQUEMA POSTGRESQL

-- GTFS estático + snapshots históricos + tiempo real

-- ============================================================

-- ============================================================

-- AGENCY

-- ============================================================

CREATE TABLE IF NOT EXISTS agency (

    agency_name VARCHAR(255) NOT NULL,

    agency_url VARCHAR(500),

    agency_timezone VARCHAR(100),

    agency_lang VARCHAR(10),

    agency_phone VARCHAR(50),

    snapshot_date DATE NOT NULL,

    PRIMARY KEY (agency_name, snapshot_date)

);

-- ============================================================

-- ROUTES

-- ============================================================

CREATE TABLE IF NOT EXISTS routes (

    route_id VARCHAR(100) NOT NULL,

    route_short_name VARCHAR(100),

    route_long_name VARCHAR(255),

    route_type INTEGER,

    route_url VARCHAR(500

    route_color VARCHAR(20),

    route_text_color VARCHAR(20),

    snapshot_date DATE NOT NULL,

    PRIMARY KEY (route_id, snapshot_date)

);

-- ============================================================

-- STOPS

-- ============================================================

CREATE TABLE IF NOT EXISTS stops (

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

    PRIMARY KEY (stop_id, snapshot_date)

);

-- ============================================================

-- CALENDAR

-- ============================================================

CREATE TABLE IF NOT EXISTS calendar (

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

    PRIMARY KEY (service_id, snapshot_date)

);

-- ============================================================

-- CALENDAR DATES

-- ============================================================

CREATE TABLE IF NOT EXISTS calendar_dates (

    service_id VARCHAR(100) NOT NULL,

    date DATE NOT NULL,

    exception_type INTEGER NOT NULL,

    snapshot_date DATE NOT NULL,

    PRIMARY KEY (service_id, date, snapshot_date)

);

-- ============================================================

-- TRIPS

-- ============================================================

CREATE TABLE IF NOT EXISTS trips (

    trip_id VARCHAR(100) NOT NULL,

    route_id VARCHAR(100) NOT NULL,

    service_id VARCHAR(100) NOT NULL,

    trip_headsign VARCHAR(255),

    direction_id INTEGER,

    shape_id VARCHAR(100),

    wheelchair_accessible INTEGER,

    snapshot_date DATE NOT NULL,

    PRIMARY KEY (trip_id, snapshot_date),

    CONSTRAINT fk_trips_route

        FOREIGN KEY (route_id, snapshot_date)

        REFERENCES routes(route_id, snapshot_date)

);

-- ============================================================

-- STOP TIMES

-- ============================================================

CREATE TABLE IF NOT EXISTS stop_times (

    trip_id VARCHAR(100) NOT NULL,

    stop_id VARCHAR(100) NOT NULL,

    arrival_time VARCHAR(20),

    departure_time VARCHAR(20),

    stop_sequence INTEGER NOT NULL,

    snapshot_date DATE NOT NULL,

    PRIMARY KEY (

        trip_id,

        stop_id,

        stop_sequence,

        snapshot_date

    ),

    CONSTRAINT fk_stop_times_trip

        FOREIGN KEY (trip_id, snapshot_date)

        REFERENCES trips(trip_id, snapshot_date),

    CONSTRAINT fk_stop_times_stop

        FOREIGN KEY (stop_id, snapshot_date)

        REFERENCES stops(stop_id, snapshot_date)

);

-- ============================================================

-- ÍNDICES GTFS

-- ===========================================================

CREATE INDEX IF NOT EXISTS idx_trips_route_id

    ON trips(route_id);

CREATE INDEX IF NOT EXISTS idx_trips_service_id

    ON trips(service_id);

CREATE INDEX IF NOT EXISTS idx_stop_times_trip_id

    ON stop_times(trip_id);

CREATE INDEX IF NOT EXISTS idx_stop_times_stop_id

    ON stop_times(stop_id);

CREATE INDEX IF NOT EXISTS idx_stops_name

    ON stops(stop_name);

CREATE INDEX IF NOT EXISTS idx_calendar_dates_service_id

    ON calendar_dates(service_id);

CREATE INDEX IF NOT EXISTS idx_calendar_dates_date

    ON calendar_dates(date);

-- ============================================================

-- ÍNDICES SNAPSHOT

-- ============================================================

CREATE INDEX IF NOT EXISTS idx_agency_snapshot_date

    ON agency(snapshot_date);

CREATE INDEX IF NOT EXISTS idx_routes_snapshot_date

    ON routes(snapshot_date);

CREATE INDEX IF NOT EXISTS idx_stops_snapshot_date

    ON stops(snapshot_date);

CREATE INDEX IF NOT EISTS idx_calendar_snapshot_date

    ON calendar(snapshot_date);

CREATE INDEX IF NOT EXISTS idx_calendar_dates_snapshot_date

    ON calendar_dates(snapshot_date);

CREATE INDEX IF NOT EXISTS idx_trips_snapshot_date

    ON trips(snapshot_date);

CREATE INDEX IF NOT EXISTS idx_stop_times_snapshot_date

    ON stop_times(snapshot_date);

-- ============================================================

-- REAL-TIME BUS ARRIVALS

-- ============================================================

CREATE TABLE IF NOT EXISTS realtime_bus_arrivals (

    id BIGSERIAL PRIMARY KEY,

    event_timestamp TIMESTAMP NOT NULL,

    destination VARCHAR(255),

    line VARCHAR(20),

    route_id VARCHAR(20),

    stop_id VARCHAR(20),

    arrival_minutes INTEGER,

    arrival_seconds INTEGER,

    arrival_text VARCHAR(100),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);

