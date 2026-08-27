"""Conexão e schema do banco de memória de longo prazo (SQLite, arquivo único local).

Validação de `tipo` fica no código Python (ver repository.py), não numa
CHECK constraint do SQLite — alterar esse tipo de constraint num banco já
existente é custoso, e a lista de tipos válidos deve poder crescer (ex:
"rotina") sem exigir migração de schema.
"""

import sqlite3

from jarvis import config

_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS memorias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    texto TEXT NOT NULL,
    categoria TEXT NOT NULL,
    tipo TEXT NOT NULL,
    passos TEXT,
    data_criacao TEXT NOT NULL,
    data_expiracao TEXT
);
"""


def _ensure_passos_column(conn: sqlite3.Connection) -> None:
    """Adiciona a coluna `passos` a bancos criados antes dela existir."""
    columns = {row["name"] for row in conn.execute("PRAGMA table_info(memorias)").fetchall()}
    if "passos" not in columns:
        conn.execute("ALTER TABLE memorias ADD COLUMN passos TEXT")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(config.MEMORY_DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute(_CREATE_TABLE)
    _ensure_passos_column(conn)
    return conn
