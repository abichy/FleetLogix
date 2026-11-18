# FleetLogix M2 — Modelo estrella

## Diagrama dimensional

```mermaid
flowchart TB
    CUSTOMER["DIM_CUSTOMER<br/>400.000 clientes"]
    DATE["DIM_DATE<br/>365 fechas"]
    DRIVER["DIM_DRIVER<br/>400 conductores"]
    ROUTE["DIM_ROUTE<br/>50 rutas"]
    TIME["DIM_TIME<br/>1.440 minutos"]
    VEHICLE["DIM_VEHICLE<br/>200 vehículos"]

    FACT["FACT_DELIVERIES<br/>400.000 entregas"]

    CUSTOMER -->|CUSTOMER_KEY| FACT
    DATE -->|DATE_KEY| FACT
    DRIVER -->|DRIVER_KEY| FACT
    ROUTE -->|ROUTE_KEY| FACT
    TIME -->|TIME_KEY| FACT
    VEHICLE -->|VEHICLE_KEY| FACT
```

## Granularidad

Una fila de FACT_DELIVERIES representa una entrega.

## Relaciones

La tabla de hechos se relaciona con seis dimensiones
mediante claves dimensionales.

## Consideraciones

La distancia y el combustible corresponden al viaje.
Si un viaje contiene varias entregas, estos valores
pueden repetirse en la tabla de hechos.

Por eso no deben sumarse directamente por entrega.

## Plataforma

- Data Warehouse: Snowflake
- Base de datos: FLEETLOGIX_DW
- Esquema: ANALYTICS
- Warehouse: FLEETLOGIX_WH
