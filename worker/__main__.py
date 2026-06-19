import argparse
import logging

from core.logging_redactor import install_redactor
from worker.pipeline import run_daemon, run_once

install_redactor()
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


def main():
    parser = argparse.ArgumentParser(description="EleitorAI worker")
    parser.add_argument("--daemon", action="store_true", help="roda em modo daemon continuo")
    parser.add_argument("--once", action="store_true", help="processa fila uma vez")
    args = parser.parse_args()

    if args.daemon:
        run_daemon()
    elif args.once:
        processed = run_once()
        print(f"processados: {processed}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
