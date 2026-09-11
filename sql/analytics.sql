-- CONSULTAS ANNALITICAS
-- Base de datos: urbanflow
-- Fuente: GTFS TMB Barcelona

-- 1. TOP 10 RUTAS POR NÚMERO DE VIAJES

SELECT
    r.route_short_name,
    r.route_long_name,
    COUNT(t.trip_id) AS num_viajes
FROM routes r
JOIN trips t
    ON r.route_id = t.route_id
GROUP BY
    r.route_id,
    r.route_short_name,
    r.route_long_name
ORDER BY num_viajes DESC
LIMIT 10;

-- 2. VIAJES POR TIPO DE TRANSPORTE

SELECT
    CASE
        WHEN r.route_type = 0 THEN 'Tranvía'
        WHEN r.route_type = 1 THEN 'Metro'
        WHEN r.route_type = 3 THEN 'Autobús'
        WHEN r.route_type = 7 THEN 'Funicular'
        ELSE 'Otro'
    END AS tipo_transporte,
    COUNT(t.trip_id) AS num_viajes
FROM routes r
JOIN trips t
    ON r.route_id = t.route_id
GROUP BY r.route_type
ORDER BY num_viajes DESC;

-- 3. TOP 10 PARADAS POR NÚMERO DE VIAJES

SELECT
    s.stop_id,
    s.stop_name,
    COUNT(st.trip_id) AS num_viajes
FROM stops s
JOIN stop_times st
    ON s.stop_id = st.stop_id
GROUP BY
    s.stop_id,
    s.stop_name
ORDER BY num_viajes DESC
LIMIT 10;

-- 4. TOP 10 RUTAS POR NÚMERO DE PARADAS

SELECT
    r.route_short_name,
    r.route_long_name,
    COUNT(DISTINCT st.stop_id) AS num_paradas
FROM routes r
JOIN trips t
    ON r.route_id = t.route_id
JOIN stop_times st
    ON t.trip_id = st.trip_id
GROUP BY
    r.route_id,
    r.route_short_name,
    r.route_long_name
ORDER BY num_paradas DESC
LIMIT 10;

-- 5. DISTRIBUCIÓN DE VIAJES POR DIRECCIÓN

SELECT
    direction_id,
    COUNT(*) AS num_viajes
FROM trips
GROUP BY direction_id
ORDER BY direction_id;

-- 6. EXCEPCIONES DEL CALENDARIO

SELECT
    exception_type,
    COUNT(*) AS num_registros
FROM calendar_dates
GROUP BY exception_type
ORDER BY exception_type;


-- 7. TOP 10 SERVICE_ID POR NÚMERO DE VIAJES

SELECT
    service_id,
    COUNT(*) AS num_viajes
FROM trips
GROUP BY service_id
ORDER BY num_viajes DESC
LIMIT 10;