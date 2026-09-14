-- ============================================================
-- URBANFLOW - CONSULTAS ANALÍTICAS DIMENSIONALES
-- Base de datos: urbanflow
-- Modelo dimensional: Star Schema
-- ============================================================


-- ============================================================
-- 1. TOP 10 RUTAS POR NÚMERO DE VIAJES
-- ============================================================

SELECT
    r.route_short_name,
    r.route_long_name,
    COUNT(f.trip_key) AS num_viajes
FROM fact_trip f
JOIN dim_route r
    ON f.route_key = r.route_key
GROUP BY
    r.route_key,
    r.route_short_name,
    r.route_long_name
ORDER BY num_viajes DESC
LIMIT 10;


-- ============================================================
-- 2. VIAJES POR TIPO DE TRANSPORTE
-- ============================================================

SELECT
    CASE
        WHEN r.route_type = 0 THEN 'Tranvía'
        WHEN r.route_type = 1 THEN 'Metro'
        WHEN r.route_type = 3 THEN 'Autobús'
        WHEN r.route_type = 7 THEN 'Funicular'
        ELSE 'Otro'
    END AS tipo_transporte,
    COUNT(f.trip_key) AS num_viajes
FROM fact_trip f
JOIN dim_route r
    ON f.route_key = r.route_key
GROUP BY r.route_type
ORDER BY num_viajes DESC;


-- ============================================================
-- 3. TOP 10 PARADAS POR NÚMERO DE PASOS DE VIAJES
-- ============================================================

SELECT
    s.stop_id,
    s.stop_name,
    COUNT(*) AS num_pasos
FROM fact_stop_time f
JOIN dim_stop s
    ON f.stop_key = s.stop_key
GROUP BY
    s.stop_key,
    s.stop_id,
    s.stop_name
ORDER BY num_pasos DESC
LIMIT 10;


-- ============================================================
-- 4. TOP 10 RUTAS POR NÚMERO DE PARADAS
-- ============================================================

SELECT
    r.route_short_name,
    r.route_long_name,
    COUNT(DISTINCT f.stop_key) AS num_paradas
FROM fact_stop_time f
JOIN fact_trip t
    ON f.trip_key = t.trip_key
JOIN dim_route r
    ON t.route_key = r.route_key
GROUP BY
    r.route_key,
    r.route_short_name,
    r.route_long_name
ORDER BY num_paradas DESC
LIMIT 10;


-- ============================================================
-- 5. VIAJES POR DIRECCIÓN
-- ============================================================

SELECT
    f.direction_id,
    COUNT(f.trip_key) AS num_viajes
FROM fact_trip f
GROUP BY f.direction_id
ORDER BY f.direction_id;


-- ============================================================
-- 6. VIAJES POR SERVICIO
-- ============================================================

SELECT
    s.service_id,
    COUNT(f.trip_key) AS num_viajes
FROM fact_trip f
JOIN dim_service s
    ON f.service_key = s.service_key
GROUP BY
    s.service_key,
    s.service_id
ORDER BY num_viajes DESC;


-- ============================================================
-- 7. RUTAS POR TIPO DE TRANSPORTE
-- ============================================================

SELECT
    CASE
        WHEN route_type = 0 THEN 'Tranvía'
        WHEN route_type = 1 THEN 'Metro'
        WHEN route_type = 3 THEN 'Autobús'
        WHEN route_type = 7 THEN 'Funicular'
        ELSE 'Otro'
    END AS tipo_transporte,
    COUNT(*) AS num_rutas
FROM dim_route
GROUP BY route_type
ORDER BY num_rutas DESC;


-- ============================================================
-- 8. TOP 10 RUTAS CON MÁS VIAJES POR SERVICIO
-- ============================================================

SELECT
    r.route_short_name,
    r.route_long_name,
    s.service_id,
    COUNT(f.trip_key) AS num_viajes
FROM fact_trip f
JOIN dim_route r
    ON f.route_key = r.route_key
JOIN dim_service s
    ON f.service_key = s.service_key
GROUP BY
    r.route_key,
    r.route_short_name,
    r.route_long_name,
    s.service_key,
    s.service_id
ORDER BY num_viajes DESC
LIMIT 10;


-- ============================================================
-- 9. VIAJES POR RUTA Y DIRECCIÓN
-- ============================================================

SELECT
    r.route_short_name,
    r.route_long_name,
    f.direction_id,
    COUNT(f.trip_key) AS num_viajes
FROM fact_trip f
JOIN dim_route r
    ON f.route_key = r.route_key
GROUP BY
    r.route_key,
    r.route_short_name,
    r.route_long_name,
    f.direction_id
ORDER BY
    r.route_short_name,
    f.direction_id;


-- ============================================================
-- 10. RUTAS Y VIAJES POR SERVICIO
-- ============================================================

SELECT
    s.service_id,
    COUNT(DISTINCT f.route_key) AS num_rutas,
    COUNT(f.trip_key) AS num_viajes
FROM fact_trip f
JOIN dim_service s
    ON f.service_key = s.service_key
GROUP BY
    s.service_key,
    s.service_id
ORDER BY num_viajes DESC;


-- ============================================================
-- 11. VIAJES POR DÍA DE LA SEMANA
-- ============================================================

SELECT
    CASE
        WHEN s.monday = 1 THEN 'Lunes'
        WHEN s.tuesday = 1 THEN 'Martes'
        WHEN s.wednesday = 1 THEN 'Miércoles'
        WHEN s.thursday = 1 THEN 'Jueves'
        WHEN s.friday = 1 THEN 'Viernes'
        WHEN s.saturday = 1 THEN 'Sábado'
        WHEN s.sunday = 1 THEN 'Domingo'
        ELSE 'Sin día'
    END AS dia_semana,
    COUNT(f.trip_key) AS num_viajes
FROM fact_trip f
JOIN dim_service s
    ON f.service_key = s.service_key
GROUP BY
    CASE
        WHEN s.monday = 1 THEN 'Lunes'
        WHEN s.tuesday = 1 THEN 'Martes'
        WHEN s.wednesday = 1 THEN 'Miércoles'
        WHEN s.thursday = 1 THEN 'Jueves'
        WHEN s.friday = 1 THEN 'Viernes'
        WHEN s.saturday = 1 THEN 'Sábado'
        WHEN s.sunday = 1 THEN 'Domingo'
        ELSE 'Sin día'
    END
ORDER BY num_viajes DESC;


-- ============================================================
-- 12. TOP 10 PARADAS POR NÚMERO DE VIAJES DISTINTOS
-- ============================================================

SELECT
    s.stop_id,
    s.stop_name,
    COUNT(DISTINCT f.trip_key) AS num_viajes
FROM fact_stop_time f
JOIN dim_stop s
    ON f.stop_key = s.stop_key
GROUP BY
    s.stop_key,
    s.stop_id,
    s.stop_name
ORDER BY num_viajes DESC
LIMIT 10;


-- ============================================================
-- 13. TOP 10 RUTAS CON MÁS PARADAS DISTINTAS
-- ============================================================

SELECT
    r.route_short_name,
    r.route_long_name,
    COUNT(DISTINCT f.stop_key) AS num_paradas
FROM fact_stop_time f
JOIN fact_trip t
    ON f.trip_key = t.trip_key
JOIN dim_route r
    ON t.route_key = r.route_key
GROUP BY
    r.route_key,
    r.route_short_name,
    r.route_long_name
ORDER BY num_paradas DESC
LIMIT 10;


-- ============================================================
-- 14. VIAJES POR RUTA Y SERVICIO
-- ============================================================

SELECT
    r.route_short_name,
    s.service_id,
    COUNT(f.trip_key) AS num_viajes
FROM fact_trip f
JOIN dim_route r
    ON f.route_key = r.route_key
JOIN dim_service s
    ON f.service_key = s.service_key
GROUP BY
    r.route_key,
    r.route_short_name,
    s.service_key,
    s.service_id
ORDER BY
    r.route_short_name,
    num_viajes DESC;


-- ============================================================
-- 15. PARADAS POR TIPO DE LOCALIZACIÓN
-- ============================================================

SELECT
    CASE
        WHEN location_type = 0 THEN 'Parada'
        WHEN location_type = 1 THEN 'Estación'
        WHEN location_type = 2 THEN 'Entrada/Salida'
        WHEN location_type = 3 THEN 'Nodo genérico'
        WHEN location_type = 4 THEN 'Zona de embarque'
        ELSE 'Otro'
    END AS tipo_localizacion,
    COUNT(*) AS num_paradas
FROM dim_stop
GROUP BY location_type
ORDER BY num_paradas DESC;


-- ============================================================
-- 16. DISTRIBUCIÓN DE ACCESIBILIDAD DE LAS PARADAS
-- ============================================================

SELECT
    wheelchair_boarding,
    COUNT(*) AS num_paradas
FROM dim_stop
GROUP BY wheelchair_boarding
ORDER BY wheelchair_boarding;


-- ============================================================
-- 17. DURACIÓN DE LOS VIAJES POR RUTA
-- ============================================================

SELECT
    r.route_short_name,
    r.route_long_name,
    COUNT(DISTINCT f.trip_key) AS num_viajes,
    COUNT(f.stop_key) AS num_paradas_recorridas
FROM fact_stop_time f
JOIN fact_trip t
    ON f.trip_key = t.trip_key
JOIN dim_route r
    ON t.route_key = r.route_key
GROUP BY
    r.route_key,
    r.route_short_name,
    r.route_long_name
ORDER BY num_paradas_recorridas DESC
LIMIT 10;


-- ============================================================
-- 18. SERVICIOS Y SUS DÍAS ACTIVOS
-- ============================================================

SELECT
    service_id,
    monday,
    tuesday,
    wednesday,
    thursday,
    friday,
    saturday,
    sunday,
    start_date,
    end_date
FROM dim_service
ORDER BY service_id;


-- ============================================================
-- 19. RESUMEN DEL MODELO DIMENSIONAL
-- ============================================================

SELECT
    COUNT(*) AS total_viajes,
    COUNT(DISTINCT route_key) AS total_rutas,
    COUNT(DISTINCT service_key) AS total_servicios,
    COUNT(DISTINCT direction_id) AS total_direcciones
FROM fact_trip;


-- ============================================================
-- 20. RESUMEN COMPLETO DEL MODELO
-- ============================================================

SELECT
    (SELECT COUNT(*) FROM dim_route) AS total_rutas,
    (SELECT COUNT(*) FROM dim_stop) AS total_paradas,
    (SELECT COUNT(*) FROM dim_service) AS total_servicios,
    (SELECT COUNT(*) FROM fact_trip) AS total_viajes,
    (SELECT COUNT(*) FROM fact_stop_time) AS total_stop_times;