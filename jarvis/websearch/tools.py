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
                "Busca informação atual na internet e te deixa responder "
                "por voz. É a ferramenta PADRÃO sempre que o usuário "
                "pedir para 'pesquisar'/'procurar' algo SEM mencionar "
                "Safari ou navegador — nesse caso, use só esta, não abra "
                "nenhum navegador. Não abre nada visível no computador do "
                "usuário — a busca acontece só aqui, o resultado volta "
                "como texto pra você ler e responder falando. Só chame "
                "TAMBÉM pesquisar_no_safari se o usuário mencionar "
                "explicitamente o Safari/navegador."
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
