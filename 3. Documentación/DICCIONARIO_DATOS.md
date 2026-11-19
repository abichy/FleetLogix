# FleetLogix — Diccionario de datos

Columnas y tipos obtenidos de PostgreSQL mediante information_schema.columns.

| Tabla | Columna | Tipo de dato | Permite NULL |
|---|---|---|---|
| deliveries | delivery_id | integer | NO |
| deliveries | trip_id | integer | YES |
| deliveries | tracking_number | character varying | NO |
| deliveries | customer_name | character varying | NO |
| deliveries | delivery_address | text | NO |
| deliveries | package_weight_kg | numeric | YES |
| deliveries | scheduled_datetime | timestamp without time zone | YES |
| deliveries | delivered_datetime | timestamp without time zone | YES |
| deliveries | delivery_status | character varying | YES |
| deliveries | recipient_signature | boolean | YES |
| drivers | driver_id | integer | NO |
| drivers | employee_code | character varying | NO |
| drivers | first_name | character varying | NO |
| drivers | last_name | character varying | NO |
| drivers | license_number | character varying | NO |
| drivers | license_expiry | date | YES |
| drivers | phone | character varying | YES |
| drivers | hire_date | date | YES |
| drivers | status | character varying | YES |
| maintenance | maintenance_id | integer | NO |
| maintenance | vehicle_id | integer | YES |
| maintenance | maintenance_date | date | NO |
| maintenance | maintenance_type | character varying | NO |
| maintenance | description | text | YES |
| maintenance | cost | numeric | YES |
| maintenance | next_maintenance_date | date | YES |
| maintenance | performed_by | character varying | YES |
| routes | route_id | integer | NO |
| routes | route_code | character varying | NO |
| routes | origin_city | character varying | NO |
| routes | destination_city | character varying | NO |
| routes | distance_km | numeric | YES |
| routes | estimated_duration_hours | numeric | YES |
| routes | toll_cost | numeric | YES |
| trips | trip_id | integer | NO |
| trips | vehicle_id | integer | YES |
| trips | driver_id | integer | YES |
| trips | route_id | integer | YES |
| trips | departure_datetime | timestamp without time zone | NO |
| trips | arrival_datetime | timestamp without time zone | YES |
| trips | fuel_consumed_liters | numeric | YES |
| trips | total_weight_kg | numeric | YES |
| trips | status | character varying | YES |
| vehicles | vehicle_id | integer | NO |
| vehicles | license_plate | character varying | NO |
| vehicles | vehicle_type | character varying | NO |
| vehicles | capacity_kg | numeric | YES |
| vehicles | fuel_type | character varying | YES |
| vehicles | acquisition_date | date | YES |
| vehicles | status | character varying | YES |

Nota: las claves primarias, foráneas y las descripciones funcionales requieren documentación adicional.
