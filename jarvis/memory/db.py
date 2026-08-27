"""Conexão e schema do banco de memória de longo prazo (SQLite, arquivo único local)."""

import sqlite3

from jarvis import config

_SCHEMA = """
CREATE TABLE IF NOT EXISTS memorias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    texto TEXT NOT NULL,
    categoria TEXT NOT NULL,
    tipo TEXT NOT NULL CHECK (tipo IN ('fato', 'preferencia')),
    data_criacao TEXT NOT NULL,
    data_expiracao TEXT
);
"""


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(config.MEMORY_DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute(_SCHEMA)
    return conn
