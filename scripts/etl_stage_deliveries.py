import os
import snowflake.connector

archivo = os.path.abspath("deliveries_export.csv")

if not os.path.isfile(archivo):
    raise FileNotFoundError(archivo)

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
            CREATE TABLE IF NOT EXISTS STG_DELIVERIES (
                DELIVERY_ID NUMBER,
                TRIP_ID NUMBER,
                TRACKING_NUMBER TEXT,
                CUSTOMER_NAME TEXT,
                PACKAGE_WEIGHT_KG NUMBER(18,3),
                SCHEDULED_DATETIME TIMESTAMP_NTZ,
                DELIVERED_DATETIME TIMESTAMP_NTZ,
                DELIVERY_STATUS TEXT,
                RECIPIENT_SIGNATURE BOOLEAN,
                VEHICLE_ID NUMBER,
                DRIVER_ID NUMBER,
                ROUTE_ID NUMBER,
                FUEL_CONSUMED_LITERS NUMBER(18,3),
                DISTANCE_KM NUMBER(18,3)
            )
        """)

        cur.execute("SELECT COUNT(*) FROM STG_DELIVERIES")
        existentes = cur.fetchone()[0]

        if existentes != 0:
            raise ValueError(
                f"STG_DELIVERIES contiene {existentes:,} filas. "
                "No se cargará nuevamente para evitar duplicados."
            )

        cur.execute(f"""
            PUT 'file://{archivo}'
            @%STG_DELIVERIES
            AUTO_COMPRESS=TRUE
            OVERWRITE=TRUE
        """)

        cur.execute("""
            COPY INTO STG_DELIVERIES
            FROM @%STG_DELIVERIES
            FILE_FORMAT = (
                TYPE = CSV
                SKIP_HEADER = 1
                FIELD_OPTIONALLY_ENCLOSED_BY = '"'
                NULL_IF = ('')
                TIMESTAMP_FORMAT = 'YYYY-MM-DD HH24:MI:SS'
                ENCODING = 'UTF8'
            )
            ON_ERROR = ABORT_STATEMENT
        """)

        cur.execute("""
            SELECT
                COUNT(*),
                COUNT(DISTINCT DELIVERY_ID),
                COUNT_IF(DELIVERY_STATUS = 'delivered'),
                COUNT_IF(DELIVERY_STATUS = 'pending')
            FROM STG_DELIVERIES
        """)

        total, unicas, entregadas, pendientes = cur.fetchone()

        print("\nSTAGING DE ENTREGAS")
        print("=" * 45)
        print(f"Total: {total:,}")
        print(f"Entregas únicas: {unicas:,}")
        print(f"Completadas: {entregadas:,}")
        print(f"Pendientes: {pendientes:,}")

        if (
            total != 400000
            or unicas != 400000
            or entregadas != 339820
            or pendientes != 60180
        ):
            raise ValueError(
                "La validación de STG_DELIVERIES falló"
            )

        print("Validación: OK")

finally:
    conn.close()
