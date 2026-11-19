-- Query 1: Contar vehículos por tipo
-- Objetivo: Conocer la composición de la flota

SELECT
    vehicle_type,
    COUNT(*) AS cantidad
FROM vehicles
GROUP BY vehicle_type
ORDER BY cantidad DESC; 

-- Query 2: Listar conductores con licencia próxima a vencer
-- Problema de negocio: Prevenir problemas legales por licencias vencidas

SELECT
    first_name,
    last_name,
    license_number,
    license_expiry
FROM drivers
WHERE license_expiry < CURRENT_DATE + INTERVAL '30 days'
ORDER BY license_expiry;

-- Query 3: Total de viajes por estado
-- Problema de negocio: Monitorear operaciones en curso

SELECT
    status,
    COUNT(*) AS total_viajes
FROM trips
GROUP BY status;

-- Query 4: Total de entregas por ciudad destino en los últimos 2 meses
-- Problema de negocio: Identificar demanda por ciudad para planificación de recursos

SELECT
    r.destination_city,
    COUNT(DISTINCT t.trip_id) AS total_viajes,
    COUNT(d.delivery_id) AS total_entregas,
    SUM(d.package_weight_kg) AS peso_total_kg
FROM routes r
INNER JOIN trips t ON r.route_id = t.route_id
INNER JOIN deliveries d ON t.trip_id = d.trip_id
WHERE t.departure_datetime >= CURRENT_DATE - INTERVAL '60 days'
GROUP BY r.destination_city
ORDER BY total_entregas DESC;

-- Query 5: Conductores activos con cantidad de viajes completados
-- Problema de negocio: Evaluar carga de trabajo por conductor

SELECT
    d.driver_id,
    d.first_name || ' ' || d.last_name as nombre_completo,
    d.license_expiry,
    COUNT(t.trip_id) as viajes_totales,
    SUM(CASE WHEN t.status = 'completed' THEN 1 ELSE 0 END) as viajes_completados
FROM drivers d
LEFT JOIN trips t ON d.driver_id = t.driver_id
WHERE d.status = 'active'
GROUP BY d.driver_id, d.first_name, d.last_name, d.license_expiry
HAVING COUNT(t.trip_id) > 0
ORDER BY viajes_completados DESC;

-- Query 6: Promedio de entregas por conductor en los últimos 6 meses
-- Problema de negocio: Medir productividad individual de conductores

SELECT 
    dr.driver_id,
    dr.first_name || ' ' || dr.last_name as conductor,
    COUNT(DISTINCT t.trip_id) as total_viajes,
    COUNT(d.delivery_id) as total_entregas,
    ROUND(COUNT(d.delivery_id)::NUMERIC / NULLIF(COUNT(DISTINCT t.trip_id), 0), 2) as promedio_entregas_por_viaje,
    ROUND(COUNT(d.delivery_id)::NUMERIC / 180, 2) as promedio_entregas_diarias
FROM drivers dr
INNER JOIN trips t ON dr.driver_id = t.driver_id
INNER JOIN deliveries d ON t.trip_id = d.trip_id
WHERE t.departure_datetime >= CURRENT_DATE - INTERVAL '6 months'
    AND t.status = 'completed'
GROUP BY dr.driver_id, dr.first_name, dr.last_name
HAVING COUNT(DISTINCT t.trip_id) >= 10
ORDER BY promedio_entregas_por_viaje DESC;

-- Query 7: Rutas con mayor consumo de combustible por kilómetro
-- Problema de negocio: Identificar rutas ineficientes para optimización

SELECT
    r.route_code,
    r.origin_city || ' -> ' || r.destination_city as ruta,
    r.distance_km,
    COUNT(t.trip_id) as viajes_realizados,
    AVG(t.fuel_consumed_liters) as promedio_combustible_litros,
    ROUND(AVG(t.fuel_consumed_liters / NULLIF(r.distance_km, 0)) * 100, 2) as litros_por_100km,
    SUM(t.fuel_consumed_liters) as combustible_total
FROM routes r
INNER JOIN trips t ON r.route_id = t.route_id
WHERE t.fuel_consumed_liters IS NOT NULL
    AND r.distance_km > 0
    AND t.status = 'completed'
GROUP BY r.route_id, r.route_code, r.origin_city, r.destination_city, r.distance_km
HAVING COUNT(t.trip_id) >= 50
ORDER BY litros_por_100km DESC
LIMIT 10;

-- Query 8: Análisis de entregas retrasadas por día de la semana
-- Problema de negocio: Identificar patrones de retraso para mejorar planificación

SELECT
    TO_CHAR(d.scheduled_datetime, 'Day') as dia_semana,
    EXTRACT(DOW FROM d.scheduled_datetime) as num_dia,
    COUNT(*) as total_entregas,
    COUNT(CASE
        WHEN d.delivered_datetime > d.scheduled_datetime + INTERVAL '30 minutes'
        THEN 1
    END) as entregas_retrasadas,
    ROUND(100.0 * COUNT(CASE
        WHEN d.delivered_datetime > d.scheduled_datetime + INTERVAL '30 minutes'
        THEN 1
    END) / COUNT(*), 2) as porcentaje_retrasos,
    AVG(EXTRACT(EPOCH FROM (d.delivered_datetime - d.scheduled_datetime)) / 60) as minutos_promedio_diferencia
FROM deliveries d
WHERE d.delivery_status = 'delivered'
    AND d.scheduled_datetime >= CURRENT_DATE - INTERVAL '90 days'
GROUP BY dia_semana, num_dia
ORDER BY num_dia;

-- Avance 2: Rendimiento ANTES de crear índices
-- Consulta 8: Entregas de los últimos 90 días

EXPLAIN (ANALYZE, BUFFERS)
SELECT COUNT(*)
FROM deliveries
WHERE delivery_status = 'delivered'
  AND scheduled_datetime >= CURRENT_DATE - INTERVAL '90 days';

-- Índice para optimizar la búsqueda de entregas
CREATE INDEX IF NOT EXISTS idx_deliveries_status_scheduled
ON deliveries (delivery_status, scheduled_datetime);

-- Rendimiento DESPUÉS de crear el índice

EXPLAIN (ANALYZE, BUFFERS)
SELECT COUNT(*)
FROM deliveries
WHERE delivery_status = 'delivered'
  AND scheduled_datetime >= CURRENT_DATE - INTERVAL '90 days';
