import os
import sys
import logging
import snowflake.connector

logging.basicConfig(
    level=logging.WARNING,
    format="%(levelname)s | %(message)s"
)

SQL = """
MERGE INTO FACT_DELIVERIES f
USING (
    SELECT
        s.DELIVERY_ID,
        s.TRIP_ID,
        s.TRACKING_NUMBER,
        dt.DATE_KEY,
        tm.TIME_KEY AS SCHEDULED_TIME_KEY,
        CASE
            WHEN s.DELIVERED_DATETIME IS NOT NULL
            THEN HOUR(s.DELIVERED_DATETIME) * 10000
               + MINUTE(s.DELIVERED_DATETIME) * 100
        END AS DELIVERED_TIME_KEY,
        v.VEHICLE_KEY,
        dr.DRIVER_KEY,
        r.ROUTE_KEY,
        c.CUSTOMER_KEY,
        s.PACKAGE_WEIGHT_KG,
        s.DISTANCE_KM,
        s.FUEL_CONSUMED_LITERS,
        CASE
            WHEN s.DELIVERED_DATETIME IS NULL THEN NULL
            ELSE GREATEST(
                DATEDIFF(minute, s.SCHEDULED_DATETIME,
                         s.DELIVERED_DATETIME), 0
            )
        END AS DELAY_MINUTES,
        s.DISTANCE_KM /
            NULLIF(s.FUEL_CONSUMED_LITERS, 0)
            AS FUEL_EFFICIENCY_KM_PER_LITER,
        CASE
            WHEN s.DELIVERED_DATETIME IS NULL THEN NULL
            ELSE s.DELIVERED_DATETIME <= s.SCHEDULED_DATETIME
        END AS IS_ON_TIME,
        s.RECIPIENT_SIGNATURE AS HAS_SIGNATURE,
        s.DELIVERY_STATUS
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
      ON HOUR(s.SCHEDULED_DATETIME) * 10000
       + MINUTE(s.SCHEDULED_DATETIME) * 100
       = tm.TIME_KEY
) src
ON f.DELIVERY_ID = src.DELIVERY_ID
WHEN MATCHED AND (
    f.TRIP_ID IS DISTINCT FROM src.TRIP_ID
    OR f.TRACKING_NUMBER IS DISTINCT FROM src.TRACKING_NUMBER
    OR f.DATE_KEY IS DISTINCT FROM src.DATE_KEY
    OR f.SCHEDULED_TIME_KEY IS DISTINCT FROM src.SCHEDULED_TIME_KEY
    OR f.DELIVERED_TIME_KEY IS DISTINCT FROM src.DELIVERED_TIME_KEY
    OR f.VEHICLE_KEY IS DISTINCT FROM src.VEHICLE_KEY
    OR f.DRIVER_KEY IS DISTINCT FROM src.DRIVER_KEY
    OR f.ROUTE_KEY IS DISTINCT FROM src.ROUTE_KEY
    OR f.CUSTOMER_KEY IS DISTINCT FROM src.CUSTOMER_KEY
    OR f.PACKAGE_WEIGHT_KG IS DISTINCT FROM src.PACKAGE_WEIGHT_KG
    OR f.DISTANCE_KM IS DISTINCT FROM src.DISTANCE_KM
    OR f.FUEL_CONSUMED_LITERS IS DISTINCT FROM src.FUEL_CONSUMED_LITERS
    OR f.DELAY_MINUTES IS DISTINCT FROM src.DELAY_MINUTES
    OR f.FUEL_EFFICIENCY_KM_PER_LITER IS DISTINCT FROM src.FUEL_EFFICIENCY_KM_PER_LITER
    OR f.IS_ON_TIME IS DISTINCT FROM src.IS_ON_TIME
    OR f.HAS_SIGNATURE IS DISTINCT FROM src.HAS_SIGNATURE
    OR f.DELIVERY_STATUS IS DISTINCT FROM src.DELIVERY_STATUS
) THEN UPDATE SET
    f.TRIP_ID = src.TRIP_ID,
    f.TRACKING_NUMBER = src.TRACKING_NUMBER,
    f.DATE_KEY = src.DATE_KEY,
    f.SCHEDULED_TIME_KEY = src.SCHEDULED_TIME_KEY,
    f.DELIVERED_TIME_KEY = src.DELIVERED_TIME_KEY,
    f.VEHICLE_KEY = src.VEHICLE_KEY,
    f.DRIVER_KEY = src.DRIVER_KEY,
    f.ROUTE_KEY = src.ROUTE_KEY,
    f.CUSTOMER_KEY = src.CUSTOMER_KEY,
    f.PACKAGE_WEIGHT_KG = src.PACKAGE_WEIGHT_KG,
    f.DISTANCE_KM = src.DISTANCE_KM,
    f.FUEL_CONSUMED_LITERS = src.FUEL_CONSUMED_LITERS,
    f.DELAY_MINUTES = src.DELAY_MINUTES,
    f.FUEL_EFFICIENCY_KM_PER_LITER =
        src.FUEL_EFFICIENCY_KM_PER_LITER,
    f.IS_ON_TIME = src.IS_ON_TIME,
    f.HAS_SIGNATURE = src.HAS_SIGNATURE,
    f.DELIVERY_STATUS = src.DELIVERY_STATUS,
    f.ETL_TIMESTAMP = CURRENT_TIMESTAMP()
WHEN NOT MATCHED THEN INSERT (
    DELIVERY_ID, TRIP_ID, TRACKING_NUMBER,
    DATE_KEY, SCHEDULED_TIME_KEY, DELIVERED_TIME_KEY,
    VEHICLE_KEY, DRIVER_KEY, ROUTE_KEY, CUSTOMER_KEY,
    PACKAGE_WEIGHT_KG, DISTANCE_KM, FUEL_CONSUMED_LITERS,
    DELAY_MINUTES, FUEL_EFFICIENCY_KM_PER_LITER,
    IS_ON_TIME, HAS_SIGNATURE, DELIVERY_STATUS,
    ETL_TIMESTAMP
) VALUES (
    src.DELIVERY_ID, src.TRIP_ID, src.TRACKING_NUMBER,
    src.DATE_KEY, src.SCHEDULED_TIME_KEY,
    src.DELIVERED_TIME_KEY, src.VEHICLE_KEY,
    src.DRIVER_KEY, src.ROUTE_KEY, src.CUSTOMER_KEY,
    src.PACKAGE_WEIGHT_KG, src.DISTANCE_KM,
    src.FUEL_CONSUMED_LITERS, src.DELAY_MINUTES,
    src.FUEL_EFFICIENCY_KM_PER_LITER,
    src.IS_ON_TIME, src.HAS_SIGNATURE,
    src.DELIVERY_STATUS, CURRENT_TIMESTAMP()
)
"""

def main():
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
            for table in ("STG_DELIVERIES", "FACT_DELIVERIES"):
                cur.execute(f"""
                    SELECT COUNT(*) - COUNT(DISTINCT DELIVERY_ID)
                    FROM {table}
                """)
                if cur.fetchone()[0] != 0:
                    raise ValueError(
                        f"Hay entregas duplicadas en {table}"
                    )

            cur.execute("SELECT COUNT(*) FROM STG_DELIVERIES")
            staged = cur.fetchone()[0]

            if staged == 0:
                raise ValueError("STG_DELIVERIES está vacía")

            print(f"Registros en staging: {staged:,}")

            cur.execute(SQL)
            print("MERGE ejecutado correctamente")

    finally:
        conn.close()

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
