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
                route_id,
                route_code,
                origin_city,
                destination_city,
                distance_km,
                estimated_duration_hours,
                toll_cost
            FROM public.routes
            ORDER BY route_id
        """)
        routes = cur.fetchall()

    ids = [row[0] for row in routes]

    if any(x is None for x in ids):
        raise ValueError("Existen ROUTE_ID nulos")

    if len(ids) != len(set(ids)):
        raise ValueError("Existen ROUTE_ID duplicados")

    print(f"Rutas extraídas: {len(routes)}")

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
        cur.execute("SELECT ROUTE_ID FROM DIM_ROUTE")
        existing_ids = {int(row[0]) for row in cur.fetchall()}

        nuevos = []

        for row in routes:
            if row[0] in existing_ids:
                continue

            nuevos.append((
                row[0],  # ROUTE_KEY
                row[0],  # ROUTE_ID
                row[1],  # ROUTE_CODE
                row[2],  # ORIGIN_CITY
                row[3],  # DESTINATION_CITY
                row[4],  # DISTANCE_KM
                row[5],  # ESTIMATED_DURATION_HOURS
                row[6]   # TOLL_COST
            ))

        if nuevos:
            cur.executemany("""
                INSERT INTO DIM_ROUTE (
                    ROUTE_KEY,
                    ROUTE_ID,
                    ROUTE_CODE,
                    ORIGIN_CITY,
                    DESTINATION_CITY,
                    DISTANCE_KM,
                    ESTIMATED_DURATION_HOURS,
                    TOLL_COST
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, nuevos)

        cur.execute("""
            SELECT COUNT(*), COUNT(DISTINCT ROUTE_ID)
            FROM DIM_ROUTE
        """)

        total, distintos = cur.fetchone()

        if total != distintos:
            raise ValueError("Existen ROUTE_ID duplicados")

        if total != len(routes):
            raise ValueError(
                f"Esperados {len(routes)}, encontrados {total}"
            )

    sf.commit()

    print("\nETL DIM_ROUTE COMPLETADO")
    print("=" * 45)
    print(f"Rutas origen: {len(routes)}")
    print(f"Rutas nuevas: {len(nuevos)}")
    print(f"Rutas Snowflake: {total}")
    print("Validación: OK")

except Exception:
    if sf is not None:
        sf.rollback()
    raise

finally:
    pg.close()
    if sf is not None:
        sf.close()
