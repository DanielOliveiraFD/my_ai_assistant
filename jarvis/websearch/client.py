"""Cliente isolado de busca na web, via Groq Compound (groq/compound).

Não é o provedor de IA principal do assistente (isso continua em
jarvis/brain/) — é só um backend de busca chamado como caixa-preta pela
ferramenta buscar_na_web. O Compound tem busca embutida mas não suporta
ferramentas customizadas (as de memória, por exemplo), por isso ele nunca
vira o modelo principal da conversa — só responde perguntas pontuais aqui,
isoladamente, e o resultado volta como texto para o cérebro principal.
"""

from groq import Groq, GroqError

from jarvis import config

MODEL = "groq/compound"

_client = Groq(api_key=config.GROQ_API_KEY)


def search(query: str) -> str:
    try:
        response = _client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Responda à pergunta usando busca na web quando necessário. "
                        "Seja direto e breve, sem enrolação — a resposta vai ser "
                        "repassada para outro assistente de voz."
                    ),
                },
                {"role": "user", "content": query},
            ],
            # Restringe às ferramentas embutidas do Compound só à busca —
            # sem isso, o conjunto completo (busca, execução de código,
            # Wolfram Alpha, visitar site) parece pesar no tamanho da
            # requisição o suficiente pra estourar limite mesmo em
            # perguntas curtas (visto no teste manual: erro 413).
            compound_custom={"tools": {"enabled_tools": ["web_search"]}},
        )
        return response.choices[0].message.content.strip()
    except GroqError as exc:
        return f"Não consegui buscar na web agora ({exc})."
