"""Cliente isolado de busca na web, via Tavily.

Groq Compound (groq/compound) foi tentado primeiro, mas apresenta um bug
conhecido do lado deles — retorna 413 "Request Entity Too Large" mesmo em
buscas triviais, sem prompt de sistema nenhum (confirmado em relatos da
comunidade do Groq, não é algo que dá pra contornar ajustando nossa
requisição). Tavily é uma API de busca dedicada, com plano gratuito
generoso, sem essa instabilidade.

Não é o provedor de IA principal do assistente (isso continua em
jarvis/brain/) — é só um backend de busca chamado pela ferramenta
buscar_na_web.
"""

import json
import ssl
import urllib.request

import certifi

from jarvis import config

API_URL = "https://api.tavily.com/search"
TIMEOUT_SECONDS = 15

# Alguns Pythons instalados no macOS (via python.org) não vêm com os
# certificados raiz do sistema configurados, causando
# CERTIFICATE_VERIFY_FAILED em qualquer chamada HTTPS via urllib. O certifi
# fornece um bundle de certificados próprio, independente da configuração
# do sistema.
_SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())


def search(query: str) -> str:
    if not config.TAVILY_API_KEY:
        return "Busca na web não configurada (falta TAVILY_API_KEY no .env)."

    payload = {
        "api_key": config.TAVILY_API_KEY,
        "query": query,
        "include_answer": True,
        "max_results": 3,
    }
    request = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(
            request, timeout=TIMEOUT_SECONDS, context=_SSL_CONTEXT
        ) as response:
            data = json.loads(response.read().decode("utf-8"))
    except Exception as exc:
        return f"Não consegui buscar na web agora ({exc})."

    answer = data.get("answer")
    if answer:
        return answer

    results = data.get("results", [])
    if not results:
        return "Não encontrei nada relevante sobre isso."

    return "\n".join(
        f"- {r.get('title', '')}: {r.get('content', '')}" for r in results[:3]
    )
