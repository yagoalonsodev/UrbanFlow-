-- Métricas disponibles para Metabase sobre llegadas GTFS-RT.
-- Las consultas usan únicamente columnas existentes en realtime_bus_arrivals.

-- Llegadas por línea durante la última hora.
SELECT
    line,
    COUNT(*) AS total_llegadas
FROM realtime_bus_arrivals
WHERE event_timestamp >= CURRENT_TIMESTAMP - INTERVAL '1 hour'
GROUP BY line
ORDER BY total_llegadas DESC;

-- Llegadas procesadas por minuto durante la última hora.
SELECT
    date_trunc('minute', event_timestamp) AS minuto,
    COUNT(*) AS total_llegadas
FROM realtime_bus_arrivals
WHERE event_timestamp >= CURRENT_TIMESTAMP - INTERVAL '1 hour'
GROUP BY minuto
ORDER BY minuto;

-- Tiempo medio estimado de llegada por línea durante la última hora.
SELECT
    line,
    AVG(arrival_seconds) AS media_segundos,
    MIN(arrival_seconds) AS minimo_segundos,
    MAX(arrival_seconds) AS maximo_segundos
FROM realtime_bus_arrivals
WHERE event_timestamp >= CURRENT_TIMESTAMP - INTERVAL '1 hour'
GROUP BY line
ORDER BY media_segundos DESC;

-- Paradas con más llegadas durante la última hora.
SELECT
    stop_id,
    COUNT(*) AS total_llegadas
FROM realtime_bus_arrivals
WHERE event_timestamp >= CURRENT_TIMESTAMP - INTERVAL '1 hour'
GROUP BY stop_id
ORDER BY total_llegadas DESC
LIMIT 10;

-- Resumen del estado realtime.
SELECT
    COUNT(*) AS total_llegadas,
    COUNT(DISTINCT line) AS lineas_activas,
    COUNT(DISTINCT stop_id) AS paradas_activas,
    AVG(arrival_seconds) AS media_segundos
FROM realtime_bus_arrivals
WHERE event_timestamp >= CURRENT_TIMESTAMP - INTERVAL '1 hour';

-- Viajes batch del último snapshot disponible.
SELECT
    snapshot_date,
    COUNT(*) AS total_viajes,
    COUNT(DISTINCT route_key) AS total_rutas,
    COUNT(DISTINCT service_key) AS total_servicios
FROM fact_trip
WHERE snapshot_date = (SELECT MAX(snapshot_date) FROM fact_trip)
GROUP BY snapshot_date;