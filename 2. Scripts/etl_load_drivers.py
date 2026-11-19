import os
import getpass
import psycopg2
import snowflake.connector

password = getpass.getpass("Contraseña PostgreSQL: ")

pg = psycopg2.connect(
    host="localhost",
    port=5432,
    dbname=os.environ["PGDATABASE"],
    user=os.environ["PGUSER"],
    password=password
)

sf = None

try:
    with pg.cursor() as cur:
        cur.execute("""
            SELECT
                driver_id,
                employee_code,
                first_name,
                last_name,
                license_number,
                license_expiry,
                phone,
                hire_date,
                status
            FROM public.drivers
            ORDER BY driver_id
        """)
        drivers = cur.fetchall()

    ids = [row[0] for row in drivers]

    if any(x is None for x in ids):
        raise ValueError("Existen DRIVER_ID nulos")

    if len(ids) != len(set(ids)):
        raise ValueError("Existen DRIVER_ID duplicados")

    sf = snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        authenticator="OAUTH_AUTHORIZATION_CODE",
        warehouse="FLEETLOGIX_WH",
        database="FLEETLOGIX_DW",
        schema="ANALYTICS",
        enable_server_session_keep_alive_auto_detection=False
    )

    sf.autocommit(False)

    with sf.cursor() as cur:
        cur.execute("""
            SELECT DRIVER_ID
            FROM DIM_DRIVER
        """)

        existing_ids = {int(row[0]) for row in cur.fetchall()}

        nuevos = []

        for row in drivers:
            driver_id = row[0]

            if driver_id in existing_ids:
                continue

            nombre = " ".join(
                str(value).strip()
                for value in (row[2], row[3])
                if value
            )

            nuevos.append((
                driver_id,
                driver_id,
                row[1],
                nombre,
                row[4],
                row[5],
                row[6],
                row[7],
                row[8],
                True
            ))

        if nuevos:
            cur.executemany("""
                INSERT INTO DIM_DRIVER (
                    DRIVER_KEY,
                    DRIVER_ID,
                    EMPLOYEE_CODE,
                    FULL_NAME,
                    LICENSE_NUMBER,
                    LICENSE_EXPIRY,
                    PHONE,
                    HIRE_DATE,
                    STATUS,
                    IS_CURRENT
                )
                VALUES (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s
                )
            """, nuevos)

        cur.execute("""
            SELECT COUNT(*), COUNT(DISTINCT DRIVER_ID)
            FROM DIM_DRIVER
        """)

        total, distintos = cur.fetchone()

        if total != distintos:
            raise ValueError(
                "Validación fallida: existen DRIVER_ID duplicados"
            )

        if total != len(drivers):
            raise ValueError(
                f"Esperados {len(drivers)}, encontrados {total}"
            )

    sf.commit()

    print("\nETL DIM_DRIVER COMPLETADO")
    print("=" * 45)
    print(f"Conductores origen: {len(drivers)}")
    print(f"Conductores nuevos: {len(nuevos)}")
    print(f"Conductores Snowflake: {total}")
    print("Validación: OK")

except Exception:
    if sf is not None:
        sf.rollback()
    raise

finally:
    pg.close()
    if sf is not None:
        sf.close()
