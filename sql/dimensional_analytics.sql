-- 1. TOP 10 RUTAS CON MÁS VIAJES

SELECT
    r.route_id,
    r.route_short_name,
    r.route_long_name,
    COUNT(DISTINCT f.trip_key) AS num_viajes
FROM fact_trip f
JOIN dim_route r
    ON f.route_key = r.route_key
GROUP BY
    r.route_id,
    r.route_short_name,
    r.route_long_name
ORDER BY num_viajes DESC
LIMIT 10;


-- 2. VIAJES POR TIPO DE TRANSPORTE

SELECT
    r.route_type,
    COUNT(DISTINCT f.trip_key) AS num_viajes
FROM fact_trip f
JOIN dim_route r
    ON f.route_key = r.route_key
GROUP BY r.route_type
ORDER BY num_viajes DESC;


-- 3. TOP 10 PARADAS CON MÁS PASOS DE VIAJES

SELECT
    s.stop_id,
    s.stop_name,
    COUNT(*) AS num_pasos
FROM fact_stop_time f
JOIN dim_stop s
    ON f.stop_key = s.stop_key
GROUP BY
    s.stop_id,
    s.stop_name
ORDER BY num_pasos DESC
LIMIT 10;


-- 4. RUTAS CON MÁS PARADAS

SELECT
    r.route_short_name,
    r.route_long_name,
    COUNT(DISTINCT f.stop_key) AS num_paradas
FROM fact_trip t
JOIN dim_route r
    ON t.route_key = r.route_key
JOIN fact_stop_time f
    ON t.trip_key = f.trip_key
GROUP BY
    r.route_short_name,
    r.route_long_name
ORDER BY num_paradas DESC
LIMIT 10;


-- 5. VIAJES POR DIRECCIÓN

SELECT
    direction_id,
    COUNT(*) AS num_viajes
FROM fact_trip
GROUP BY direction_id
ORDER BY num_viajes DESC;


-- 6. VIAJES POR SERVICIO

SELECT
    s.service_id,
    COUNT(DISTINCT f.trip_key) AS num_viajes
FROM fact_trip f
JOIN dim_service s
    ON f.service_key = s.service_key
GROUP BY s.service_id
ORDER BY num_viajes DESC
LIMIT 20;


-- 7. RUTAS POR TIPO DE TRANSPORTE

SELECT
    r.route_type,
    COUNT(DISTINCT r.route_key) AS num_rutas
FROM dim_route r
GROUP BY r.route_type
ORDER BY num_rutas DESC;


-- 8. TOP 10 COMBINACIONES RUTA + SERVICIO

SELECT
    r.route_short_name,
    s.service_id,
    COUNT(DISTINCT f.trip_key) AS num_viajes
FROM fact_trip f
JOIN dim_route r
    ON f.route_key = r.route_key
JOIN dim_service s
    ON f.service_key = s.service_key
GROUP BY
    r.route_short_name,
    s.service_id
ORDER BY num_viajes DESC
LIMIT 10;


-- 9. VIAJES POR RUTA Y DIRECCIÓN

SELECT
    r.route_short_name,
    f.direction_id,
    COUNT(DISTINCT f.trip_key) AS num_viajes
FROM fact_trip f
JOIN dim_route r
    ON f.route_key = r.route_key
GROUP BY
    r.route_short_name,
    f.direction_id
ORDER BY
    r.route_short_name,
    num_viajes DESC;


-- 10. RUTAS Y VIAJES POR SERVICIO

SELECT
    s.service_id,
    COUNT(DISTINCT f.route_key) AS num_rutas,
    COUNT(DISTINCT f.trip_key) AS num_viajes
FROM fact_trip f
JOIN dim_service s
    ON f.service_key = s.service_key
GROUP BY s.service_id
ORDER BY num_viajes DESC;


-- 11. VIAJES POR DÍA DE LA SEMANA

SELECT
    'Lunes' AS dia_semana,
    COUNT(DISTINCT f.trip_key) AS num_viajes
FROM fact_trip f
JOIN dim_service s
    ON f.service_key = s.service_key
WHERE s.monday = 1

UNION ALL

SELECT
    'Martes' AS dia_semana,
    COUNT(DISTINCT f.trip_key) AS num_viajes
FROM fact_trip f
JOIN dim_service s
    ON f.service_key = s.service_key
WHERE s.tuesday = 1

UNION ALL

SELECT
    'Miércoles' AS dia_semana,
    COUNT(DISTINCT f.trip_key) AS num_viajes
FROM fact_trip f
JOIN dim_service s
    ON f.service_key = s.service_key
WHERE s.wednesday = 1

UNION ALL

SELECT
    'Jueves' AS dia_semana,
    COUNT(DISTINCT f.trip_key) AS num_viajes
FROM fact_trip f
JOIN dim_service s
    ON f.service_key = s.service_key
WHERE s.thursday = 1

UNION ALL

SELECT
    'Viernes' AS dia_semana,
    COUNT(DISTINCT f.trip_key) AS num_viajes
FROM fact_trip f
JOIN dim_service s
    ON f.service_key = s.service_key
WHERE s.friday = 1

UNION ALL

SELECT
    'Sábado' AS dia_semana,
    COUNT(DISTINCT f.trip_key) AS num_viajes
FROM fact_trip f
JOIN dim_service s
    ON f.service_key = s.service_key
WHERE s.saturday = 1

UNION ALL

SELECT
    'Domingo' AS dia_semana,
    COUNT(DISTINCT f.trip_key) AS num_viajes
FROM fact_trip f
JOIN dim_service s
    ON f.service_key = s.service_key
WHERE s.sunday = 1;


-- 12. TOP 10 PARADAS CON MÁS VIAJES DISTINTOS

SELECT
    s.stop_id,
    s.stop_name,
    COUNT(DISTINCT f.trip_key) AS num_viajes
FROM fact_stop_time f
JOIN dim_stop s
    ON f.stop_key = s.stop_key
GROUP BY
    s.stop_id,
    s.stop_name
ORDER BY num_viajes DESC
LIMIT 10;


-- 13. TOP 10 RUTAS CON MÁS PARADAS DISTINTAS

SELECT
    r.route_short_name,
    r.route_long_name,
    COUNT(DISTINCT st.stop_key) AS num_paradas
FROM fact_trip t
JOIN dim_route r
    ON t.route_key = r.route_key
JOIN fact_stop_time st
    ON t.trip_key = st.trip_key
GROUP BY
    r.route_short_name,
    r.route_long_name
ORDER BY num_paradas DESC
LIMIT 10;


-- 14. VIAJES POR RUTA Y SERVICIO

SELECT
    r.route_short_name,
    s.service_id,
    COUNT(DISTINCT f.trip_key) AS num_viajes
FROM fact_trip f
JOIN dim_route r
    ON f.route_key = r.route_key
JOIN dim_service s
    ON f.service_key = s.service_key
GROUP BY
    r.route_short_name,
    s.service_id
ORDER BY
    r.route_short_name,
    num_viajes DESC;


-- 15. PARADAS POR TIPO DE LOCALIZACIÓN

SELECT
    location_type,
    COUNT(*) AS num_paradas
FROM dim_stop
GROUP BY location_type
ORDER BY num_paradas DESC;


-- 16. ACCESIBILIDAD PARA SILLA DE RUEDAS

SELECT
    wheelchair_boarding,
    COUNT(*) AS num_paradas
FROM dim_stop
GROUP BY wheelchair_boarding
ORDER BY num_paradas DESC;


-- 17. VIAJES Y PARADAS RECORRIDAS POR RUTA

SELECT
    r.route_short_name,
    r.route_long_name,
    COUNT(DISTINCT t.trip_key) AS num_viajes,
    COUNT(st.stop_time_key) AS num_paradas_recorridas
FROM fact_trip t
JOIN dim_route r
    ON t.route_key = r.route_key
JOIN fact_stop_time st
    ON t.trip_key = st.trip_key
GROUP BY
    r.route_short_name,
    r.route_long_name
ORDER BY num_viajes DESC
LIMIT 20;


-- 18. DÍAS DE ACTIVIDAD DE CADA SERVICIO

SELECT
    service_id,
    start_date,
    end_date,
    (
        COALESCE(monday, 0)
        + COALESCE(tuesday, 0)
        + COALESCE(wednesday, 0)
        + COALESCE(thursday, 0)
        + COALESCE(friday, 0)
        + COALESCE(saturday, 0)
        + COALESCE(sunday, 0)
    ) AS dias_activos
FROM dim_service
ORDER BY dias_activos DESC;


-- 19. RESUMEN DEL MODELO DIMENSIONAL

SELECT
    (SELECT COUNT(*) FROM dim_route) AS total_rutas,
    (SELECT COUNT(*) FROM dim_stop) AS total_paradas,
    (SELECT COUNT(*) FROM dim_service) AS total_servicios,
    (SELECT COUNT(*) FROM fact_trip) AS total_viajes,
    (SELECT COUNT(*) FROM fact_stop_time) AS total_stop_times;


-- 20. RESUMEN COMPLETO DEL MODELO

SELECT
    COUNT(DISTINCT t.trip_key) AS total_viajes,
    COUNT(DISTINCT r.route_key) AS total_rutas,
    COUNT(DISTINCT s.stop_key) AS total_paradas,
    COUNT(DISTINCT sv.service_key) AS total_servicios,
    COUNT(st.stop_time_key) AS total_stop_times
FROM fact_trip t
JOIN dim_route r
    ON t.route_key = r.route_key
JOIN dim_service sv
    ON t.service_key = sv.service_key
JOIN fact_stop_time st
    ON t.trip_key = st.trip_key
JOIN dim_stop s
    ON st.stop_key = s.stop_key;