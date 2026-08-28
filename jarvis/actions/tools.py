"""Ferramentas de ação no Safari expostas ao cérebro: schema (formato
OpenAI/Groq) e as funções que executam.

Isoladas do resto do projeto — só jarvis/brain/chat.py importa daqui.
"""

from jarvis.actions import safari

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "pesquisar_no_safari",
            "description": (
                "Pesquisa um termo no Google, abrindo o Safari numa aba "
                "nova. Use quando o usuário pedir para pesquisar/procurar "
                "algo na internet (diferente de buscar_na_web, que só "
                "traz informação pra responder, sem abrir nada visível)."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "termo": {"type": "string", "description": "O que pesquisar."}
                },
                "required": ["termo"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "abrir_site_no_safari",
            "description": (
                "Abre um site específico no Safari numa aba nova (ex: "
                "'abre o Gmail', 'abre o YouTube'). Use a URL/domínio do "
                "site diretamente, não uma busca."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "URL ou domínio do site a abrir (ex: 'gmail.com').",
                    }
                },
                "required": ["url"],
            },
        },
    },
]


def pesquisar_no_safari(termo: str) -> dict:
    return {"resultado": safari.search(termo)}


def abrir_site_no_safari(url: str) -> dict:
    return {"resultado": safari.open_site(url)}


DISPATCH = {
    "pesquisar_no_safari": pesquisar_no_safari,
    "abrir_site_no_safari": abrir_site_no_safari,
}
