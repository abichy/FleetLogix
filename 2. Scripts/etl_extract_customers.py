import os
import csv
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

archivo = "customers_export.csv"

try:
    with conn.cursor(name="customers_stream") as cur:
        cur.itersize = 10000

        cur.execute("""
            SELECT
                ROW_NUMBER() OVER (
                    ORDER BY LOWER(TRIM(customer_name))
                ) AS customer_key,
                TRIM(customer_name) AS customer_name,
                MIN(scheduled_datetime::date)
                    AS first_delivery_date,
                COUNT(*) AS total_deliveries
            FROM public.deliveries
            GROUP BY TRIM(customer_name)
            ORDER BY LOWER(TRIM(customer_name))
        """)

        total = 0

        with open(
            archivo,
            "w",
            newline="",
            encoding="utf-8"
        ) as f:
            writer = csv.writer(f)

            writer.writerow([
                "CUSTOMER_KEY",
                "CUSTOMER_NAME",
                "FIRST_DELIVERY_DATE",
                "TOTAL_DELIVERIES"
            ])

            for row in cur:
                writer.writerow(row)
                total += 1

                if total % 50000 == 0:
                    print(f"Exportados: {total:,}")

    print("\nEXTRACCIÓN COMPLETADA")
    print("=" * 40)
    print(f"Clientes exportados: {total:,}")
    print(f"Archivo generado: {archivo}")

    if total != 400000:
        raise ValueError(
            f"Se esperaban 400000 clientes, encontrados {total}"
        )

    print("Validación: OK")

finally:
    conn.close()
