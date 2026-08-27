"""Acesso a dados da memória de longo prazo. Nenhuma referência a IA/provedor
aqui — só leitura e escrita no SQLite."""

from datetime import datetime, timedelta

from jarvis.memory.db import get_connection

# "rotina" está listado aqui porque o schema já suporta (coluna `passos`),
# mas ainda não há ferramentas que criem memórias desse tipo — fica para
# quando a Fase 2 trouxer ações reais para uma rotina executar.
TIPOS_VALIDOS = ("fato", "preferencia", "rotina")


def _not_expired_clause() -> str:
    return "(data_expiracao IS NULL OR data_expiracao > ?)"


def save_memory(
    texto: str, categoria: str, tipo: str, expira_em_dias: float | None = None
) -> int:
    if tipo not in TIPOS_VALIDOS:
        raise ValueError(f"tipo inválido: {tipo!r} (esperado um de {TIPOS_VALIDOS})")

    data_criacao = datetime.now().isoformat()
    data_expiracao = (
        (datetime.now() + timedelta(days=expira_em_dias)).isoformat()
        if expira_em_dias is not None
        else None
    )

    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO memorias (texto, categoria, tipo, data_criacao, data_expiracao) "
            "VALUES (?, ?, ?, ?, ?)",
            (texto, categoria, tipo, data_criacao, data_expiracao),
        )
        return cursor.lastrowid


def list_categories() -> list[str]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT DISTINCT categoria FROM memorias ORDER BY categoria"
        ).fetchall()
    return [row["categoria"] for row in rows]


def search_memories(categoria: str | None = None, texto_chave: str | None = None) -> list[dict]:
    query = f"SELECT * FROM memorias WHERE tipo = 'fato' AND {_not_expired_clause()}"
    params = [datetime.now().isoformat()]

    if categoria:
        query += " AND categoria = ?"
        params.append(categoria)
    if texto_chave:
        query += " AND texto LIKE ?"
        params.append(f"%{texto_chave}%")

    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()
    return [dict(row) for row in rows]


def list_preferences() -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM memorias WHERE tipo = 'preferencia'").fetchall()
    return [dict(row) for row in rows]


def list_for_transparency(categoria: str | None = None) -> list[dict]:
    query = f"SELECT * FROM memorias WHERE {_not_expired_clause()}"
    params = [datetime.now().isoformat()]
    if categoria:
        query += " AND categoria = ?"
        params.append(categoria)
    query += " ORDER BY categoria, data_criacao"

    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()
    return [dict(row) for row in rows]


def get_memory(memory_id: int) -> dict | None:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM memorias WHERE id = ?", (memory_id,)).fetchone()
    return dict(row) if row else None


def find_memories_by_text(texto_chave: str) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM memorias WHERE texto LIKE ? ORDER BY data_criacao DESC",
            (f"%{texto_chave}%",),
        ).fetchall()
    return [dict(row) for row in rows]


def delete_memory(memory_id: int) -> bool:
    with get_connection() as conn:
        cursor = conn.execute("DELETE FROM memorias WHERE id = ?", (memory_id,))
        return cursor.rowcount > 0
