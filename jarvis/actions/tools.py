"""Ferramentas de ação no macOS expostas ao cérebro: schema (formato
OpenAI/Groq) e as funções que executam.

Isoladas do resto do projeto — só jarvis/brain/chat.py importa daqui.
"""

from jarvis.actions import apps, safari

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "abrir_aplicativo",
            "description": (
                "Abre um aplicativo do Mac pelo nome (ex: 'Safari', "
                "'Spotify', 'Calendário', 'Notas'), sem fazer nenhuma "
                "busca ou ação dentro dele. Use quando o usuário só quer "
                "abrir o programa (ex: 'abre o Safari'), sem pedir mais "
                "nada específico junto."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "nome": {
                        "type": "string",
                        "description": "Nome do aplicativo, ex: 'Safari'.",
                    }
                },
                "required": ["nome"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "pesquisar_no_safari",
            "description": (
                "Pesquisa um termo no Google, abrindo o Safari numa aba "
                "nova. Use SOMENTE quando o usuário mencionar "
                "explicitamente o Safari/navegador (ex: 'pesquisa no "
                "Safari', 'abre o navegador e pesquisa'). Sozinha, essa "
                "ferramenta só abre a página, não traz o conteúdo pra "
                "você falar — por isso, toda vez que usar "
                "pesquisar_no_safari para algo informativo, chame TAMBÉM "
                "buscar_na_web com o mesmo termo, na mesma resposta, "
                "automaticamente (sem esperar o usuário pedir), para "
                "poder falar o resultado em voz alta além de abrir a "
                "página."
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


def abrir_aplicativo(nome: str) -> dict:
    return {"resultado": apps.open_app(nome)}


def pesquisar_no_safari(termo: str) -> dict:
    return {"resultado": safari.search(termo)}


def abrir_site_no_safari(url: str) -> dict:
    return {"resultado": safari.open_site(url)}


DISPATCH = {
    "abrir_aplicativo": abrir_aplicativo,
    "pesquisar_no_safari": pesquisar_no_safari,
    "abrir_site_no_safari": abrir_site_no_safari,
}
