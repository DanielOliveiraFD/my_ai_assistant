"""Ferramenta de busca na web exposta ao cérebro principal: schema (formato
OpenAI/Groq) e a função que executa.

Isolada do resto do projeto — só jarvis/brain/chat.py importa daqui.
"""

from jarvis.websearch import client

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "buscar_na_web",
            "description": (
                "Busca informação atual na internet quando você não sabe a "
                "resposta ou ela pode ter mudado (ex: clima, notícias, "
                "preços, eventos recentes, fatos específicos). Não abre "
                "nenhum navegador no computador do usuário — a busca "
                "acontece só aqui, o resultado volta como texto pra você "
                "ler e responder. Se o usuário também quiser ver a página "
                "aberta no Safari (não só ouvir a resposta), chame "
                "TAMBÉM pesquisar_no_safari com o mesmo termo, na mesma "
                "resposta — as duas não são excludentes."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "pergunta": {
                        "type": "string",
                        "description": "A pergunta ou termo a pesquisar.",
                    }
                },
                "required": ["pergunta"],
            },
        },
    },
]


def buscar_na_web(pergunta: str) -> dict:
    resultado = client.search(pergunta)
    return {"resultado": resultado}


DISPATCH = {"buscar_na_web": buscar_na_web}
