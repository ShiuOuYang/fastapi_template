from __future__ import annotations

import argparse
import sys
from pathlib import Path

import uvicorn

ROOT_DIR = Path(__file__).resolve().parent
SRC_DIR = ROOT_DIR / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from app.core.config import settings


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Start Flying Probe Analysis System API from project root."
    )
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=settings.APP_PORT)
    parser.add_argument(
        "--no-reload",
        action="store_true",
        help="Disable auto reload in development.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    uvicorn.run(
        "app.main:app",
        host=args.host,
        port=args.port,
        reload=not args.no_reload and settings.APP_ENV == "development",
        app_dir=str(SRC_DIR),
    )


if __name__ == "__main__":
    main()
