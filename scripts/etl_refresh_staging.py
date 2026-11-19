import os
import sys
import uuid
from pathlib import Path

import snowflake.connector

COLUMNS = [
    "DELIVERY_ID", "TRIP_ID", "TRACKING_NUMBER",
    "CUSTOMER_NAME", "PACKAGE_WEIGHT_KG",
    "SCHEDULED_DATETIME", "DELIVERED_DATETIME",
    "DELIVERY_STATUS", "RECIPIENT_SIGNATURE",
    "VEHICLE_ID", "DRIVER_ID", "ROUTE_ID",
    "FUEL_CONSUMED_LITERS", "DISTANCE_KM"
]

def main():
    archivo = Path(__file__).resolve().parent / "deliveries_export.csv"
    if not archivo.is_file():
        raise FileNotFoundError(archivo)

    conn = snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        authenticator="OAUTH_AUTHORIZATION_CODE",
        warehouse="FLEETLOGIX_WH",
        database="FLEETLOGIX_DW",
        schema="ANALYTICS"
    )

    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TEMPORARY TABLE TMP_DELIVERIES
                LIKE STG_DELIVERIES
            """)

            stage = "TMP_DELIVERIES"
            nombre = archivo.name

            cur.execute(f"""
                PUT 'file://{archivo.as_posix()}'
                @%{stage}
                AUTO_COMPRESS=TRUE
                OVERWRITE=TRUE
            """)

            cur.execute(f"""
                COPY INTO {stage}
                FROM @%{stage}
                FILE_FORMAT = (
                    TYPE = CSV
                    SKIP_HEADER = 1
                    FIELD_OPTIONALLY_ENCLOSED_BY = '"'
                    NULL_IF = ('')
                    TIMESTAMP_FORMAT = 'YYYY-MM-DD HH24:MI:SS'
                    ENCODING = 'UTF8'
                )
                ON_ERROR = ABORT_STATEMENT
            """)

            cur.execute("""
                SELECT COUNT(*), COUNT(DISTINCT DELIVERY_ID)
                FROM TMP_DELIVERIES
            """)
            total, unicas = cur.fetchone()

            if total == 0 or total != unicas:
                raise ValueError(
                    f"CSV inválido: {total} filas, {unicas} únicas"
                )

            print(f"Filas temporales validadas: {total:,}")

            columnas = ", ".join(COLUMNS)
            valores = ", ".join(f"src.{c}" for c in COLUMNS)
            cambios = ", ".join(
                f"dst.{c} = src.{c}"
                for c in COLUMNS
                if c != "DELIVERY_ID"
            )

            comparaciones = " OR ".join(
                f"dst.{c} IS DISTINCT FROM src.{c}"
                for c in COLUMNS
                if c != "DELIVERY_ID"
            )

            sql = f"""
                MERGE INTO STG_DELIVERIES dst
                USING TMP_DELIVERIES src
                ON dst.DELIVERY_ID = src.DELIVERY_ID
                WHEN MATCHED AND (
                    {comparaciones}
                ) THEN UPDATE SET {cambios}
                WHEN NOT MATCHED THEN
                    INSERT ({columnas})
                    VALUES ({valores})
            """

            cur.execute(sql)
            print("STAGING ACTUALIZADO CORRECTAMENTE")

    finally:
        conn.close()

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
