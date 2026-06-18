import sqlite3
from pathlib import Path
from typing import Optional

import sqlite_vec

from core.config import get_settings

_SCHEMA_PATH = Path(__file__).parent / "schema.sql"


def load_vec_extension(conn: sqlite3.Connection) -> None:
    conn.enable_load_extension(True)
    conn.load_extension(sqlite_vec.loadable_path())
    conn.enable_load_extension(False)


def init_db(db_path: Optional[str] = None) -> None:
    if db_path is None:
        db_path = get_settings().db_path
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    load_vec_extension(conn)
    conn.executescript(_SCHEMA_PATH.read_text(encoding="utf-8"))
    conn.commit()
    conn.close()


def get_db(db_path: Optional[str] = None) -> sqlite3.Connection:
    if db_path is None:
        db_path = get_settings().db_path
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    load_vec_extension(conn)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn
