import os
import csv
import getpass
import psycopg2

password = os.getenv("PGPASSWORD") or getpass.getpass(
    "Contraseña PostgreSQL: "
)

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    dbname=os.environ["PGDATABASE"],
    user=os.environ["PGUSER"],
    password=password
)

archivo = "deliveries_export.csv"

consulta = """
SELECT
    d.delivery_id,
    d.trip_id,
    d.tracking_number,
    LOWER(TRIM(d.customer_name)) AS customer_name,
    d.package_weight_kg,
    d.scheduled_datetime,
    d.delivered_datetime,
    d.delivery_status,
    d.recipient_signature,
    t.vehicle_id,
    t.driver_id,
    t.route_id,
    t.fuel_consumed_liters,
    r.distance_km
FROM public.deliveries d
JOIN public.trips t
    ON d.trip_id = t.trip_id
JOIN public.routes r
    ON t.route_id = r.route_id
ORDER BY d.delivery_id
"""

columnas = [
    "DELIVERY_ID",
    "TRIP_ID",
    "TRACKING_NUMBER",
    "CUSTOMER_NAME",
    "PACKAGE_WEIGHT_KG",
    "SCHEDULED_DATETIME",
    "DELIVERED_DATETIME",
    "DELIVERY_STATUS",
    "RECIPIENT_SIGNATURE",
    "VEHICLE_ID",
    "DRIVER_ID",
    "ROUTE_ID",
    "FUEL_CONSUMED_LITERS",
    "DISTANCE_KM"
]

try:
    with conn.cursor(name="deliveries_stream") as cur:
        cur.itersize = 10000
        cur.execute(consulta)

        total = 0

        with open(
            archivo,
            "w",
            newline="",
            encoding="utf-8"
        ) as f:
            writer = csv.writer(f)
            writer.writerow(columnas)

            for fila in cur:
                writer.writerow(fila)
                total += 1

                if total % 50000 == 0:
                    print(f"Entregas exportadas: {total:,}")

    print("\nEXTRACCIÓN FACT_DELIVERIES")
    print("=" * 45)
    print(f"Total exportado: {total:,}")
    print(f"Archivo: {archivo}")

    if total == 0:
        raise ValueError(
            "La extracción no produjo registros"
        )

    print("Validación: OK")

finally:
    conn.close()
