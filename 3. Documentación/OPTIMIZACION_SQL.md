# FleetLogix — Evidencia de optimización SQL

## Objetivo
Comparar el rendimiento de una consulta sobre 400.000 entregas en PostgreSQL.

## Índice utilizado
idx_deliveries_status_scheduled
Columnas: delivery_status y scheduled_datetime.

## Consulta SQL
SELECT delivery_id, delivery_status, scheduled_datetime
FROM deliveries
WHERE delivery_status = 'pending'
AND scheduled_datetime >= '2026-06-01'
AND scheduled_datetime < '2026-06-02';

## Resultados

| Métrica | Sin índice | Con índice |
|---|---|---|
| Tiempo de ejecución | 55,274 ms | 2,456 ms |
| Registros encontrados | 195 | 195 |
| Bloques compartidos accedidos | 6154 | 198 |
| Plan de ejecución | Parallel Seq Scan | Index Scan |

## Mejora observada
Reducción del tiempo de ejecución: 95,56 %.

## Metodología
Se utilizó EXPLAIN (ANALYZE, BUFFERS). Para comparar sin índice se desactivaron temporalmente los métodos de acceso por índice mediante SET LOCAL, sin eliminar índices ni modificar datos.

## Limitación
Se realizó una medición por escenario. Los resultados pueden variar según la caché y la carga del servidor.
