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
            INSERT INTO DIM_DATE (
                DATE_KEY,
                FULL_DATE,
                DAY_OF_WEEK,
                DAY_NAME,
                DAY_OF_MONTH,
                DAY_OF_YEAR,
                WEEK_OF_YEAR,
                MONTH_NUM,
                MONTH_NAME,
                QUARTER,
                YEAR,
                IS_WEEKEND,
                FISCAL_QUARTER,
                FISCAL_YEAR
            )
            SELECT
                TO_NUMBER(TO_CHAR(d, 'YYYYMMDD')),
                d,
                DAYOFWEEKISO(d),
                DECODE(
                    DAYOFWEEKISO(d),
                    1, 'Lunes',
                    2, 'Martes',
                    3, 'Miércoles',
                    4, 'Jueves',
                    5, 'Viernes',
                    6, 'Sábado',
                    7, 'Domingo'
                ),
                DAY(d),
                DAYOFYEAR(d),
                WEEKISO(d),
                MONTH(d),
                DECODE(
                    MONTH(d),
                    1, 'Enero',
                    2, 'Febrero',
                    3, 'Marzo',
                    4, 'Abril',
                    5, 'Mayo',
                    6, 'Junio',
                    7, 'Julio',
                    8, 'Agosto',
                    9, 'Septiembre',
                    10, 'Octubre',
                    11, 'Noviembre',
                    12, 'Diciembre'
                ),
                QUARTER(d),
                YEAR(d),
                DAYOFWEEKISO(d) IN (6, 7),
                QUARTER(d),
                YEAR(d)
            FROM (
                SELECT DATEADD(
                    day,
                    SEQ4(),
                    '2026-01-01'::DATE
                ) AS d
                FROM TABLE(GENERATOR(ROWCOUNT => 365))
            )
            WHERE NOT EXISTS (
                SELECT 1
                FROM DIM_DATE existing
                WHERE existing.FULL_DATE = d
            )
        """)

        cur.execute("""
            SELECT COUNT(*), COUNT(DISTINCT DATE_KEY)
            FROM DIM_DATE
            WHERE YEAR = 2026
        """)

        total, unicas = cur.fetchone()

        if total != 365 or unicas != 365:
            raise ValueError(
                f"Validación fallida: {total} fechas, "
                f"{unicas} claves únicas"
            )

        print("\nETL DIM_DATE COMPLETADO")
        print("=" * 45)
        print(f"Fechas registradas: {total}")
        print(f"Claves únicas: {unicas}")
        print("Validación: OK")

finally:
    conn.close()
