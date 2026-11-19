import argparse
import logging
import subprocess
import sys
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent
LOG_DIR = BASE / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(
            LOG_DIR / "etl_pipeline.log",
            encoding="utf-8"
        )
    ]
)

def ejecutar(script):
    logging.info("INICIO | %s", script)

    resultado = subprocess.run(
        [sys.executable, str(BASE / script)],
        cwd=BASE,
        check=False
    )

    if resultado.returncode != 0:
        raise RuntimeError(
            f"{script} falló con código {resultado.returncode}"
        )

    logging.info("OK | %s", script)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Ejecutar MERGE y controles de calidad"
    )
    args = parser.parse_args()

    inicio = datetime.now()
    logging.info("PIPELINE FLEETLOGIX | INICIO")

    if not args.execute:
        logging.info(
            "MODO SEGURO: no se modificaron datos. "
            "Usar --execute para ejecutar el pipeline."
        )
        return

    try:
        ejecutar("etl_extract_deliveries.py")
        ejecutar("etl_refresh_staging.py")
        ejecutar("etl_merge_deliveries.py")
        ejecutar("etl_quality_checks.py")
    except Exception:
        logging.exception("PIPELINE FALLIDO")
        sys.exit(1)

    duracion = (datetime.now() - inicio).total_seconds()
    logging.info(
        "PIPELINE COMPLETADO | Duración: %.2f segundos",
        duracion
    )

if __name__ == "__main__":
    main()
