import os
import snowflake.connector

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
            INSERT INTO DIM_TIME (
                TIME_KEY,
                HOUR,
                MINUTE,
                SECOND,
                TIME_OF_DAY,
                HOUR_24,
                HOUR_12,
                AM_PM,
                IS_BUSINESS_HOUR,
                SHIFT
            )
            SELECT
                h * 10000 + m * 100,
                h,
                m,
                0,
                CASE
                    WHEN h BETWEEN 6 AND 11 THEN 'Mañana'
                    WHEN h BETWEEN 12 AND 17 THEN 'Tarde'
                    WHEN h BETWEEN 18 AND 21 THEN 'Noche'
                    ELSE 'Madrugada'
                END,
                LPAD(h::VARCHAR, 2, '0'),
                LPAD(
                    (CASE
                        WHEN MOD(h, 12) = 0 THEN 12
                        ELSE MOD(h, 12)
                    END)::VARCHAR,
                    2, '0'
                ),
                CASE WHEN h < 12 THEN 'AM' ELSE 'PM' END,
                h BETWEEN 8 AND 17,
                CASE
                    WHEN h BETWEEN 6 AND 13 THEN 'Turno mañana'
                    WHEN h BETWEEN 14 AND 21 THEN 'Turno tarde'
                    ELSE 'Turno noche'
                END
            FROM (
                SELECT
                    FLOOR(SEQ4() / 60) AS h,
                    MOD(SEQ4(), 60) AS m
                FROM TABLE(GENERATOR(ROWCOUNT => 1440))
            ) horarios
            WHERE NOT EXISTS (
                SELECT 1
                FROM DIM_TIME existente
                WHERE existente.TIME_KEY = h * 10000 + m * 100
            )
        """)

        cur.execute("""
            SELECT
                COUNT(*),
                COUNT(DISTINCT TIME_KEY),
                MIN(TIME_KEY),
                MAX(TIME_KEY)
            FROM DIM_TIME
        """)

        total, unicas, minimo, maximo = cur.fetchone()

        print("\nETL DIM_TIME")
        print("=" * 45)
        print(f"Horarios registrados: {total:,}")
        print(f"Claves únicas: {unicas:,}")
        print(f"Primera clave: {minimo}")
        print(f"Última clave: {maximo}")

        if (
            total != 1440
            or unicas != 1440
            or minimo != 0
            or maximo != 235900
        ):
            raise ValueError("Validación de DIM_TIME fallida")

        print("Validación: OK")

finally:
    conn.close()
