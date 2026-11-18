import os
import sys
import logging
import snowflake.connector

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

CHECKS = {
    "Entregas duplicadas": """
        SELECT COUNT(*) - COUNT(DISTINCT DELIVERY_ID)
        FROM FACT_DELIVERIES
    """,
    "Claves dimensionales nulas": """
        SELECT COUNT(*)
        FROM FACT_DELIVERIES
        WHERE DATE_KEY IS NULL
           OR SCHEDULED_TIME_KEY IS NULL
           OR VEHICLE_KEY IS NULL
           OR DRIVER_KEY IS NULL
           OR ROUTE_KEY IS NULL
           OR CUSTOMER_KEY IS NULL
    """,
    "Clientes sin correspondencia": """
        SELECT COUNT(*)
        FROM FACT_DELIVERIES f
        LEFT JOIN DIM_CUSTOMER d
          ON f.CUSTOMER_KEY = d.CUSTOMER_KEY
        WHERE d.CUSTOMER_KEY IS NULL
    """,
    "Conductores sin correspondencia": """
        SELECT COUNT(*)
        FROM FACT_DELIVERIES f
        LEFT JOIN DIM_DRIVER d
          ON f.DRIVER_KEY = d.DRIVER_KEY
        WHERE d.DRIVER_KEY IS NULL
    """,
    "Vehículos sin correspondencia": """
        SELECT COUNT(*)
        FROM FACT_DELIVERIES f
        LEFT JOIN DIM_VEHICLE d
          ON f.VEHICLE_KEY = d.VEHICLE_KEY
        WHERE d.VEHICLE_KEY IS NULL
    """,
    "Rutas sin correspondencia": """
        SELECT COUNT(*)
        FROM FACT_DELIVERIES f
        LEFT JOIN DIM_ROUTE d
          ON f.ROUTE_KEY = d.ROUTE_KEY
        WHERE d.ROUTE_KEY IS NULL
    """,
    "Fechas sin correspondencia": """
        SELECT COUNT(*)
        FROM FACT_DELIVERIES f
        LEFT JOIN DIM_DATE d
          ON f.DATE_KEY = d.DATE_KEY
        WHERE d.DATE_KEY IS NULL
    """,
    "Horas sin correspondencia": """
        SELECT COUNT(*)
        FROM FACT_DELIVERIES f
        LEFT JOIN DIM_TIME d
          ON f.SCHEDULED_TIME_KEY = d.TIME_KEY
        WHERE d.TIME_KEY IS NULL
    """,
    "Pendientes con hora de entrega": """
        SELECT COUNT(*)
        FROM FACT_DELIVERIES
        WHERE DELIVERY_STATUS = 'pending'
          AND DELIVERED_TIME_KEY IS NOT NULL
    """,
    "Completadas sin hora de entrega": """
        SELECT COUNT(*)
        FROM FACT_DELIVERIES
        WHERE DELIVERY_STATUS = 'delivered'
          AND DELIVERED_TIME_KEY IS NULL
    """
}

def main():
    conn = snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        authenticator="OAUTH_AUTHORIZATION_CODE",
        warehouse="FLEETLOGIX_WH",
        database="FLEETLOGIX_DW",
        schema="ANALYTICS"
    )

    failures = 0

    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM FACT_DELIVERIES")
            total = cur.fetchone()[0]
            logging.info("Total de entregas: %s", f"{total:,}")

            if total == 0:
                logging.error("FACT_DELIVERIES está vacía")
                failures += 1

            for name, sql in CHECKS.items():
                cur.execute(sql)
                errors = cur.fetchone()[0]

                if errors == 0:
                    logging.info("OK | %s", name)
                else:
                    logging.error(
                        "ERROR | %s: %s registros",
                        name, errors
                    )
                    failures += 1

        if failures:
            logging.error(
                "CALIDAD RECHAZADA: %s controles fallidos",
                failures
            )
            return 1

        logging.info("CALIDAD APROBADA: todos los controles OK")
        return 0

    finally:
        conn.close()

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        logging.exception("Error en controles de calidad")
        sys.exit(1)
