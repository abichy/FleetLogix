import os
import snowflake.connector

archivo = os.path.abspath("customers_export.csv")

if not os.path.isfile(archivo):
    raise FileNotFoundError(archivo)

conn = snowflake.connector.connect(
    account=os.environ["SNOWFLAKE_ACCOUNT"],
    user=os.environ["SNOWFLAKE_USER"],
    authenticator="OAUTH_AUTHORIZATION_CODE",
    warehouse="FLEETLOGIX_WH",
    database="FLEETLOGIX_DW",
    schema="ANALYTICS",
    enable_server_session_keep_alive_auto_detection=False
)

try:
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TEMPORARY TABLE TMP_CUSTOMERS (
                CUSTOMER_KEY NUMBER,
                CUSTOMER_NAME TEXT,
                FIRST_DELIVERY_DATE DATE,
                TOTAL_DELIVERIES NUMBER
            )
        """)

        cur.execute(f"""
            PUT 'file://{archivo}'
            @%TMP_CUSTOMERS
            AUTO_COMPRESS=TRUE
            OVERWRITE=TRUE
        """)

        cur.execute("""
            COPY INTO TMP_CUSTOMERS
            FROM @%TMP_CUSTOMERS
            FILE_FORMAT = (
                TYPE = CSV
                SKIP_HEADER = 1
                FIELD_OPTIONALLY_ENCLOSED_BY = '"'
                DATE_FORMAT = 'YYYY-MM-DD'
                ENCODING = 'UTF8'
            )
            ON_ERROR = ABORT_STATEMENT
        """)

        cur.execute("""
            SELECT COUNT(*), COUNT(DISTINCT CUSTOMER_KEY)
            FROM TMP_CUSTOMERS
        """)

        total, claves = cur.fetchone()

        print(f"Registros cargados temporalmente: {total:,}")
        print(f"Claves únicas: {claves:,}")

        if total != 400000 or claves != 400000:
            raise ValueError(
                "La validación de la carga temporal falló"
            )

        print("Carga temporal validada correctamente.")

finally:
    conn.close()
