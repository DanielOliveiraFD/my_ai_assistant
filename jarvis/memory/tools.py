"""Ferramentas de memória expostas à IA: schema (formato OpenAI/Groq) e as
funções que cada uma executa.

`excluir_memoria` e `confirmar_exclusao` são tratadas à parte em
jarvis/brain/chat.py, porque exigem estado de confirmação entre turnos —
não são uma chamada direta ao banco como as demais.
"""

from jarvis.memory import repository

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "salvar_memoria",
            "description": (
                "Salva um fato ou preferência sobre o usuário para lembrar em "
                "conversas futuras. Antes de criar uma categoria nova, chame "
                "listar_categorias e reaproveite uma existente se fizer sentido "
                "(evite categorias redundantes)."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "texto": {"type": "string", "description": "A informação a guardar."},
                    "categoria": {
                        "type": "string",
                        "description": "Categoria da memória, ex: 'Habilidades', 'Preferências'.",
                    },
                    "tipo": {"type": "string", "enum": ["fato", "preferencia"]},
                    "expira_em_dias": {
                        "type": "number",
                        "description": (
                            "Opcional. Preencher só se a informação tiver prazo de "
                            "validade natural (ex: uma viagem na semana que vem)."
                        ),
                    },
                },
                "required": ["texto", "categoria", "tipo"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "listar_categorias",
            "description": (
                "Lista as categorias de memória já existentes, para reaproveitar "
                "antes de criar uma categoria nova."
            ),
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "buscar_memorias",
            "description": (
                "Busca fatos relevantes já salvos sobre o usuário, por categoria "
                "e/ou palavra-chave. Nunca retorna memórias expiradas."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "categoria": {"type": "string"},
                    "texto_chave": {"type": "string"},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "listar_memorias_transparencia",
            "description": (
                "Use APENAS quando o usuário pedir explicitamente para saber o "
                "que você sabe sobre ele (ex: 'o que você sabe sobre mim?'). "
                "Lista as memórias de forma legível para ser falada em voz alta."
            ),
            "parameters": {
                "type": "object",
                "properties": {"categoria": {"type": "string"}},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "excluir_memoria",
            "description": (
                "Propõe a exclusão de uma memória, por id ou descrição. NÃO apaga "
                "nada ainda — apenas identifica a memória candidata. É obrigatório "
                "confirmar explicitamente com o usuário em voz antes de chamar "
                "confirmar_exclusao."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "descricao": {"type": "string"},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "confirmar_exclusao",
            "description": (
                "Confirma e executa a exclusão de uma memória previamente "
                "proposta por excluir_memoria. Só chamar depois que o usuário "
                "confirmar explicitamente em voz que quer apagar."
            ),
            "parameters": {"type": "object", "properties": {}},
        },
    },
]


def salvar_memoria(
    texto: str, categoria: str, tipo: str, expira_em_dias: float | None = None
) -> dict:
    memory_id = repository.save_memory(texto, categoria, tipo, expira_em_dias)
    return {"status": "ok", "id": memory_id}


def listar_categorias() -> dict:
    return {"categorias": repository.list_categories()}


def buscar_memorias(categoria: str | None = None, texto_chave: str | None = None) -> dict:
    return {"memorias": repository.search_memories(categoria, texto_chave)}


def listar_memorias_transparencia(categoria: str | None = None) -> dict:
    return {"memorias": repository.list_for_transparency(categoria)}


DISPATCH = {
    "salvar_memoria": salvar_memoria,
    "listar_categorias": listar_categorias,
    "buscar_memorias": buscar_memorias,
    "listar_memorias_transparencia": listar_memorias_transparencia,
}
