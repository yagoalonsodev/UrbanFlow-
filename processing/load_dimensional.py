import logging

from sqlalchemy import create_engine, text

from utils.config import POSTGRES_DATABASE_URL


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger("urbanflow")


def load_dimensional_model() -> None:
    """Carga las dimensiones y facts del snapshot más reciente de PostgreSQL."""

    engine = create_engine(POSTGRES_DATABASE_URL)

    with engine.begin() as connection:
        snapshot_date = connection.execute(
            text("SELECT MAX(snapshot_date) FROM trips")
        ).scalar_one()

        if snapshot_date is None:
            raise RuntimeError("No existen trips para cargar el modelo dimensional.")

        connection.execute(
            text(
                """
                INSERT INTO dim_route (
                    route_id, route_short_name, route_long_name, route_type,
                    route_url, route_color, route_text_color, snapshot_date
                )
                SELECT
                    route_id, route_short_name, route_long_name, route_type,
                    route_url, route_color, route_text_color, snapshot_date
                FROM routes
                WHERE snapshot_date = :snapshot_date
                ON CONFLICT (route_id, snapshot_date) DO UPDATE SET
                    route_short_name = EXCLUDED.route_short_name,
                    route_long_name = EXCLUDED.route_long_name,
                    route_type = EXCLUDED.route_type,
                    route_url = EXCLUDED.route_url,
                    route_color = EXCLUDED.route_color,
                    route_text_color = EXCLUDED.route_text_color
                """
            ),
            {"snapshot_date": snapshot_date},
        )

        connection.execute(
            text(
                """
                INSERT INTO dim_stop (
                    stop_id, stop_code, stop_name, stop_lat, stop_lon, stop_url,
                    location_type, parent_station, wheelchair_boarding,
                    snapshot_date
                )
                SELECT
                    stop_id, stop_code, stop_name, stop_lat, stop_lon, stop_url,
                    location_type, parent_station, wheelchair_boarding,
                    snapshot_date
                FROM stops
                WHERE snapshot_date = :snapshot_date
                ON CONFLICT (stop_id, snapshot_date) DO UPDATE SET
                    stop_code = EXCLUDED.stop_code,
                    stop_name = EXCLUDED.stop_name,
                    stop_lat = EXCLUDED.stop_lat,
                    stop_lon = EXCLUDED.stop_lon,
                    stop_url = EXCLUDED.stop_url,
                    location_type = EXCLUDED.location_type,
                    parent_station = EXCLUDED.parent_station,
                    wheelchair_boarding = EXCLUDED.wheelchair_boarding
                """
            ),
            {"snapshot_date": snapshot_date},
        )

        connection.execute(
            text(
                """
                INSERT INTO dim_service (
                    service_id, monday, tuesday, wednesday, thursday, friday,
                    saturday, sunday, start_date, end_date, snapshot_date
                )
                SELECT
                    service_id, monday, tuesday, wednesday, thursday, friday,
                    saturday, sunday, start_date, end_date, snapshot_date
                FROM calendar
                WHERE snapshot_date = :snapshot_date
                UNION ALL
                SELECT
                    cd.service_id,
                    NULL, NULL, NULL, NULL, NULL, NULL, NULL,
                    NULL, NULL,
                    cd.snapshot_date
                FROM calendar_dates cd
                JOIN trips t
                    ON t.service_id = cd.service_id
                   AND t.snapshot_date = cd.snapshot_date
                LEFT JOIN calendar c
                    ON c.service_id = cd.service_id
                   AND c.snapshot_date = cd.snapshot_date
                WHERE cd.snapshot_date = :snapshot_date
                  AND c.service_id IS NULL
                GROUP BY cd.service_id, cd.snapshot_date
                ON CONFLICT (service_id, snapshot_date) DO UPDATE SET
                    monday = EXCLUDED.monday,
                    tuesday = EXCLUDED.tuesday,
                    wednesday = EXCLUDED.wednesday,
                    thursday = EXCLUDED.thursday,
                    friday = EXCLUDED.friday,
                    saturday = EXCLUDED.saturday,
                    sunday = EXCLUDED.sunday,
                    start_date = EXCLUDED.start_date,
                    end_date = EXCLUDED.end_date
                """
            ),
            {"snapshot_date": snapshot_date},
        )

        connection.execute(
            text(
                """
                DELETE FROM fact_stop_time
                WHERE snapshot_date = :snapshot_date
                """
            ),
            {"snapshot_date": snapshot_date},
        )
        connection.execute(
            text(
                """
                DELETE FROM fact_trip
                WHERE snapshot_date = :snapshot_date
                """
            ),
            {"snapshot_date": snapshot_date},
        )

        trip_result = connection.execute(
            text(
                """
                INSERT INTO fact_trip (
                    trip_id, route_key, service_key, trip_headsign, direction_id,
                    shape_id, wheelchair_accessible, snapshot_date
                )
                SELECT
                    t.trip_id,
                    r.route_key,
                    s.service_key,
                    t.trip_headsign,
                    t.direction_id,
                    t.shape_id,
                    t.wheelchair_accessible,
                    t.snapshot_date
                FROM trips t
                JOIN dim_route r
                    ON r.route_id = t.route_id
                   AND r.snapshot_date = t.snapshot_date
                JOIN dim_service s
                    ON s.service_id = t.service_id
                   AND s.snapshot_date = t.snapshot_date
                WHERE t.snapshot_date = :snapshot_date
                """
            ),
            {"snapshot_date": snapshot_date},
        )

        stop_time_result = connection.execute(
            text(
                """
                INSERT INTO fact_stop_time (
                    trip_key, stop_key, arrival_time, departure_time,
                    stop_sequence, snapshot_date
                )
                SELECT
                    f.trip_key,
                    s.stop_key,
                    st.arrival_time,
                    st.departure_time,
                    st.stop_sequence,
                    st.snapshot_date
                FROM stop_times st
                JOIN fact_trip f
                    ON f.trip_id = st.trip_id
                   AND f.snapshot_date = st.snapshot_date
                JOIN dim_stop s
                    ON s.stop_id = st.stop_id
                   AND s.snapshot_date = st.snapshot_date
                WHERE st.snapshot_date = :snapshot_date
                """
            ),
            {"snapshot_date": snapshot_date},
        )

        logger.info(
            "Modelo dimensional cargado para %s: %d fact_trip, %d fact_stop_time",
            snapshot_date,
            trip_result.rowcount,
            stop_time_result.rowcount,
        )

    engine.dispose()


if __name__ == "__main__":
    load_dimensional_model()