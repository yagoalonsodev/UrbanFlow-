-- Configuracion reproducible del dashboard UrbanFlow en Metabase.
-- Ejecutar contra la base interna de Metabase, no contra urbanflow.

BEGIN;

UPDATE report_card
SET dataset_query = jsonb_build_object(
    'lib/type', 'mbql/query',
    'database', (SELECT id FROM metabase_database WHERE name = 'UrbanFlow PostgreSQL'),
    'stages', jsonb_build_array(jsonb_build_object(
        'native', $$
SELECT
    CASE
        WHEN r.route_type = 0 THEN 'Tranvía'
        WHEN r.route_type = 1 THEN 'Metro'
        WHEN r.route_type = 3 THEN 'Autobús'
        WHEN r.route_type = 7 THEN 'Funicular'
        ELSE 'Otro'
    END AS tipo_transporte,
    COUNT(f.trip_key) AS total_viajes
FROM fact_trip f
JOIN dim_route r ON r.route_key = f.route_key
    AND r.snapshot_date = f.snapshot_date
WHERE f.snapshot_date = (SELECT MAX(snapshot_date) FROM fact_trip)
GROUP BY r.route_type
ORDER BY total_viajes DESC;
$$,
        'lib/type', 'mbql.stage/native'
    ))
)::text,
updated_at = CURRENT_TIMESTAMP
WHERE name = 'Viajes por tipo de transporte'
  AND database_id = (SELECT id FROM metabase_database WHERE name = 'UrbanFlow PostgreSQL');

UPDATE report_card
SET dataset_query = jsonb_build_object(
    'lib/type', 'mbql/query',
    'database', (SELECT id FROM metabase_database WHERE name = 'UrbanFlow PostgreSQL'),
    'stages', jsonb_build_array(jsonb_build_object(
        'native', $$
SELECT
    r.route_short_name AS linea,
    r.route_long_name AS nombre_ruta,
    COUNT(f.trip_key) AS total_viajes
FROM fact_trip f
JOIN dim_route r ON r.route_key = f.route_key
    AND r.snapshot_date = f.snapshot_date
WHERE f.snapshot_date = (SELECT MAX(snapshot_date) FROM fact_trip)
GROUP BY r.route_key, r.route_short_name, r.route_long_name
ORDER BY total_viajes DESC
LIMIT 10;
$$,
        'lib/type', 'mbql.stage/native'
    ))
)::text,
updated_at = CURRENT_TIMESTAMP
WHERE name = 'Top 10 líneas por número de viajes.'
  AND database_id = (SELECT id FROM metabase_database WHERE name = 'UrbanFlow PostgreSQL');

UPDATE report_card
SET dataset_query = jsonb_build_object(
    'lib/type', 'mbql/query',
    'database', (SELECT id FROM metabase_database WHERE name = 'UrbanFlow PostgreSQL'),
    'stages', jsonb_build_array(jsonb_build_object(
        'native', $$
SELECT COUNT(*) AS total_viajes
FROM fact_trip
WHERE snapshot_date = (SELECT MAX(snapshot_date) FROM fact_trip);
$$,
        'lib/type', 'mbql.stage/native'
    ))
)::text,
updated_at = CURRENT_TIMESTAMP
WHERE name = 'Total de Viajes'
  AND database_id = (SELECT id FROM metabase_database WHERE name = 'UrbanFlow PostgreSQL');

UPDATE report_card
SET dataset_query = jsonb_build_object(
    'lib/type', 'mbql/query',
    'database', (SELECT id FROM metabase_database WHERE name = 'UrbanFlow PostgreSQL'),
    'stages', jsonb_build_array(jsonb_build_object(
        'native', $$
SELECT COUNT(*) AS total_paradas
FROM dim_stop
WHERE snapshot_date = (SELECT MAX(snapshot_date) FROM dim_stop);
$$,
        'lib/type', 'mbql.stage/native'
    ))
)::text,
updated_at = CURRENT_TIMESTAMP
WHERE name = 'Total de paradas'
  AND database_id = (SELECT id FROM metabase_database WHERE name = 'UrbanFlow PostgreSQL');

UPDATE report_card
SET dataset_query = jsonb_build_object(
    'lib/type', 'mbql/query',
    'database', (SELECT id FROM metabase_database WHERE name = 'UrbanFlow PostgreSQL'),
    'stages', jsonb_build_array(jsonb_build_object(
        'native', $$
SELECT COUNT(*) AS total_lineas
FROM dim_route
WHERE snapshot_date = (SELECT MAX(snapshot_date) FROM dim_route);
$$,
        'lib/type', 'mbql.stage/native'
    ))
)::text,
updated_at = CURRENT_TIMESTAMP
WHERE name = 'Total de líneas'
  AND database_id = (SELECT id FROM metabase_database WHERE name = 'UrbanFlow PostgreSQL');

UPDATE report_card
SET dataset_query = jsonb_build_object(
    'lib/type', 'mbql/query',
    'database', (SELECT id FROM metabase_database WHERE name = 'UrbanFlow PostgreSQL'),
    'stages', jsonb_build_array(jsonb_build_object(
        'native', $$
SELECT
    s.stop_name AS parada,
    COUNT(*) AS total_pasos
FROM fact_stop_time f
JOIN dim_stop s ON s.stop_key = f.stop_key
    AND s.snapshot_date = f.snapshot_date
WHERE f.snapshot_date = (SELECT MAX(snapshot_date) FROM fact_stop_time)
GROUP BY s.stop_key, s.stop_id, s.stop_name
ORDER BY total_pasos DESC
LIMIT 10;
$$,
        'lib/type', 'mbql.stage/native'
    ))
)::text,
updated_at = CURRENT_TIMESTAMP
WHERE name = 'Top 10 Paradas'
  AND database_id = (SELECT id FROM metabase_database WHERE name = 'UrbanFlow PostgreSQL');

COMMIT;