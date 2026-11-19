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
                v.vehicle_id,
                v.license_plate,
                v.vehicle_type,
                v.capacity_kg,
                v.fuel_type,
                v.acquisition_date,
                v.status,
                MAX(m.maintenance_date)
            FROM public.vehicles v
            LEFT JOIN public.maintenance m
                ON v.vehicle_id = m.vehicle_id
            GROUP BY
                v.vehicle_id,
                v.license_plate,
                v.vehicle_type,
                v.capacity_kg,
                v.fuel_type,
                v.acquisition_date,
                v.status
            ORDER BY v.vehicle_id
        """)

        vehicles = cur.fetchall()

    ids = [row[0] for row in vehicles]

    if any(x is None for x in ids):
        raise ValueError("Existen VEHICLE_ID nulos")

    if len(ids) != len(set(ids)):
        raise ValueError("Existen VEHICLE_ID duplicados")

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
            SELECT VEHICLE_ID
            FROM DIM_VEHICLE
        """)

        existing_ids = {
            int(row[0]) for row in cur.fetchall()
        }

        nuevos = []

        for row in vehicles:
            vehicle_id = row[0]

            if vehicle_id in existing_ids:
                continue

            nuevos.append((
                vehicle_id,
                vehicle_id,
                row[1],
                row[2],
                row[3],
                row[4],
                row[5],
                row[6],
                row[7],
                True
            ))

        if nuevos:
            cur.executemany("""
                INSERT INTO DIM_VEHICLE (
                    VEHICLE_KEY,
                    VEHICLE_ID,
                    LICENSE_PLATE,
                    VEHICLE_TYPE,
                    CAPACITY_KG,
                    FUEL_TYPE,
                    ACQUISITION_DATE,
                    STATUS,
                    LAST_MAINTENANCE_DATE,
                    IS_CURRENT
                )
                VALUES (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s
                )
            """, nuevos)

        cur.execute("""
            SELECT
                COUNT(*),
                COUNT(DISTINCT VEHICLE_ID)
            FROM DIM_VEHICLE
        """)

        total, distintos = cur.fetchone()

        if total != distintos:
            raise ValueError(
                "Validación fallida: VEHICLE_ID duplicados"
            )

        if total != len(vehicles):
            raise ValueError(
                f"Esperados {len(vehicles)}, encontrados {total}"
            )

    sf.commit()

    print("\nETL DIM_VEHICLE COMPLETADO")
    print("=" * 45)
    print(f"Vehículos origen: {len(vehicles)}")
    print(f"Vehículos nuevos: {len(nuevos)}")
    print(f"Vehículos Snowflake: {total}")
    print("Validación: OK")

except Exception:
    if sf is not None:
        sf.rollback()
    raise

finally:
    pg.close()
    if sf is not None:
        sf.close()
