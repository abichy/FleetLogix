import os
import snowflake.connector

conn = snowflake.connector.connect(
    account=os.environ["SNOWFLAKE_ACCOUNT"],
    user=os.environ["SNOWFLAKE_USER"],
    authenticator="OAUTH_AUTHORIZATION_CODE",
    warehouse="FLEETLOGIX_WH",
    database="FLEETLOGIX_DW",
    schema="ANALYTICS"
)

try:
    with conn.cursor() as cur:

        cur.execute("""
            SELECT COUNT(*) FROM FACT_DELIVERIES
        """)
        existentes = cur.fetchone()[0]

        if existentes != 0:
            raise ValueError(
                f"FACT_DELIVERIES ya contiene "
                f"{existentes:,} registros. "
                "No se realizará otra carga inicial."
            )

        cur.execute("""
            INSERT INTO FACT_DELIVERIES (
                DATE_KEY,
                SCHEDULED_TIME_KEY,
                DELIVERED_TIME_KEY,
                VEHICLE_KEY,
                DRIVER_KEY,
                ROUTE_KEY,
                CUSTOMER_KEY,
                DELIVERY_ID,
                TRIP_ID,
                TRACKING_NUMBER,
                PACKAGE_WEIGHT_KG,
                DISTANCE_KM,
                FUEL_CONSUMED_LITERS,
                DELAY_MINUTES,
                FUEL_EFFICIENCY_KM_PER_LITER,
                IS_ON_TIME,
                HAS_SIGNATURE,
                DELIVERY_STATUS,
                ETL_TIMESTAMP
            )
            SELECT
                dt.DATE_KEY,
                tm.TIME_KEY,
                CASE
                    WHEN s.DELIVERED_DATETIME IS NOT NULL
                    THEN (
                        HOUR(s.DELIVERED_DATETIME) * 10000
                        + MINUTE(s.DELIVERED_DATETIME) * 100
                    )
                END,
                v.VEHICLE_KEY,
                dr.DRIVER_KEY,
                r.ROUTE_KEY,
                c.CUSTOMER_KEY,
                s.DELIVERY_ID,
                s.TRIP_ID,
                s.TRACKING_NUMBER,
                s.PACKAGE_WEIGHT_KG,
                s.DISTANCE_KM,
                s.FUEL_CONSUMED_LITERS,
                CASE
                    WHEN s.DELIVERED_DATETIME IS NULL
                    THEN NULL
                    ELSE GREATEST(
                        DATEDIFF(
                            minute,
                            s.SCHEDULED_DATETIME,
                            s.DELIVERED_DATETIME
                        ),
                        0
                    )
                END,
                s.DISTANCE_KM
                    / NULLIF(s.FUEL_CONSUMED_LITERS, 0),
                CASE
                    WHEN s.DELIVERED_DATETIME IS NULL
                    THEN NULL
                    ELSE s.DELIVERED_DATETIME
                         <= s.SCHEDULED_DATETIME
                END,
                s.RECIPIENT_SIGNATURE,
                s.DELIVERY_STATUS,
                CURRENT_TIMESTAMP()
            FROM STG_DELIVERIES s
            JOIN DIM_CUSTOMER c
                ON LOWER(TRIM(s.CUSTOMER_NAME))
                 = LOWER(TRIM(c.CUSTOMER_NAME))
            JOIN DIM_DRIVER dr
                ON s.DRIVER_ID = dr.DRIVER_ID
               AND dr.IS_CURRENT = TRUE
            JOIN DIM_VEHICLE v
                ON s.VEHICLE_ID = v.VEHICLE_ID
               AND v.IS_CURRENT = TRUE
            JOIN DIM_ROUTE r
                ON s.ROUTE_ID = r.ROUTE_ID
            JOIN DIM_DATE dt
                ON TO_NUMBER(
                    TO_CHAR(s.SCHEDULED_DATETIME, 'YYYYMMDD')
                ) = dt.DATE_KEY
            JOIN DIM_TIME tm
                ON (
                    HOUR(s.SCHEDULED_DATETIME) * 10000
                    + MINUTE(s.SCHEDULED_DATETIME) * 100
                ) = tm.TIME_KEY
        """)

        cur.execute("""
            SELECT
                COUNT(*),
                COUNT(DISTINCT DELIVERY_ID),
                COUNT_IF(DELIVERY_STATUS = 'delivered'),
                COUNT_IF(DELIVERY_STATUS = 'pending')
            FROM FACT_DELIVERIES
        """)

        total, unicas, completadas, pendientes = cur.fetchone()

        print("\nFACT_DELIVERIES")
        print("=" * 45)
        print(f"Total: {total:,}")
        print(f"Entregas únicas: {unicas:,}")
        print(f"Completadas: {completadas:,}")
        print(f"Pendientes: {pendientes:,}")

        if (
            total != 400000
            or unicas != 400000
            or completadas != 339820
            or pendientes != 60180
        ):
            raise ValueError(
                "La validación de FACT_DELIVERIES falló"
            )

        print("Validación: OK")

finally:
    conn.close()
