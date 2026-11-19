import os
import getpass
import psycopg2

password = getpass.getpass("Contraseña PostgreSQL: ")

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    dbname=os.environ["PGDATABASE"],
    user=os.environ["PGUSER"],
    password=password
)

try:
    with conn.cursor() as cur:
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

        conductores = cur.fetchall()

    print("\nPRUEBA ETL - DIM_DRIVER")
    print("=" * 45)
    print(f"Conductores extraídos: {len(conductores)}")

    ids = [fila[0] for fila in conductores]

    if len(ids) != len(set(ids)):
        raise ValueError("Existen DRIVER_ID duplicados")

    if any(driver_id is None for driver_id in ids):
        raise ValueError("Existen DRIVER_ID nulos")

    print("Identificadores: OK")

    for fila in conductores[:5]:
        driver_id = fila[0]
        nombre = " ".join(
            str(valor).strip()
            for valor in (fila[2], fila[3])
            if valor
        )

        print(f"DRIVER_KEY={driver_id} | Nombre={nombre}")

    print("\nPrueba completada. No se modificaron datos.")

finally:
    conn.close()
