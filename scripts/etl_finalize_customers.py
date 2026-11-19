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
        cur.execute("SELECT COUNT(*) FROM DIM_CUSTOMER")
        existentes = cur.fetchone()[0]

        if existentes != 0:
            raise ValueError(
                f"DIM_CUSTOMER ya contiene {existentes} registros. "
                "No se realizará la carga inicial."
            )

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
            SELECT
                COUNT(*),
                COUNT(DISTINCT CUSTOMER_KEY),
                COUNT(DISTINCT LOWER(TRIM(CUSTOMER_NAME)))
            FROM TMP_CUSTOMERS
        """)

        total, claves, nombres = cur.fetchone()

        if (total, claves, nombres) != (400000, 400000, 400000):
            raise ValueError(
                "Validación temporal fallida: "
                f"{total} filas, {claves} claves, {nombres} nombres"
            )

        cur.execute("""
            SELECT COUNT(*)
            FROM TMP_CUSTOMERS
            WHERE CUSTOMER_KEY IS NULL
               OR CUSTOMER_NAME IS NULL
               OR TRIM(CUSTOMER_NAME) = ''
               OR FIRST_DELIVERY_DATE IS NULL
               OR TOTAL_DELIVERIES <> 1
        """)

        if cur.fetchone()[0] != 0:
            raise ValueError("Hay datos incompletos o inválidos")

        conn.autocommit(False)

        try:
            cur.execute("""
                INSERT INTO DIM_CUSTOMER (
                    CUSTOMER_KEY,
                    CUSTOMER_NAME,
                    FIRST_DELIVERY_DATE,
                    TOTAL_DELIVERIES
                )
                SELECT
                    CUSTOMER_KEY,
                    CUSTOMER_NAME,
                    FIRST_DELIVERY_DATE,
                    TOTAL_DELIVERIES
                FROM TMP_CUSTOMERS
            """)

            cur.execute("""
                SELECT COUNT(*), COUNT(DISTINCT CUSTOMER_KEY)
                FROM DIM_CUSTOMER
            """)

            final, claves_finales = cur.fetchone()

            if final != 400000 or claves_finales != 400000:
                raise ValueError(
                    "La validación final de DIM_CUSTOMER falló"
                )

            conn.commit()

        except Exception:
            conn.rollback()
            raise

    print("\nETL DIM_CUSTOMER COMPLETADO")
    print("=" * 45)
    print(f"Clientes cargados: {final:,}")
    print(f"Claves únicas: {claves_finales:,}")
    print("Validación: OK")
    print("Transacción confirmada en Snowflake.")

finally:
    conn.close()
