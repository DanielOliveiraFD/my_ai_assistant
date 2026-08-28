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
MAX_RESULTS = 2
CONTENT_CHAR_LIMIT = 300  # por resultado, evita inchar o histórico da conversa

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
        "max_results": MAX_RESULTS,
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

    # Não usa o campo "answer" da Tavily de propósito: ele não segue o
    # idioma da pergunta (visto no teste manual: pergunta em português,
    # resposta pronta em inglês). Devolvendo só os resultados brutos, quem
    # formula a resposta final é o cérebro principal — que já segue
    # corretamente o idioma do usuário.
    results = data.get("results", [])
    if not results:
        return "Não encontrei nada relevante sobre isso."

    # Corta o conteúdo de cada resultado: sem isso, respostas de sites tipo
    # previsão do tempo (tabela de vários dias + alertas) inflam demais o
    # histórico da conversa — cada busca nova soma ao que já foi guardado,
    # e o cérebro fica cada vez mais lento a cada pergunta na mesma sessão
    # (visto no teste manual: 3s -> 14s -> 53s em buscas seguidas).
    linhas = []
    for r in results[:MAX_RESULTS]:
        conteudo = r.get("content", "")[:CONTENT_CHAR_LIMIT]
        linhas.append(f"- {r.get('title', '')}: {conteudo}")
    return "\n".join(linhas)
