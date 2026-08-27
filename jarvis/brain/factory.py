"""Ponto único de escolha de qual provedor de IA usar como cérebro.

Para trocar de provedor no futuro: implementar uma nova classe em
jarvis/brain/providers/ e adicionar um ramo aqui. Nenhum outro módulo do
projeto precisa saber qual provedor está por trás.
"""

from jarvis import config
from jarvis.brain.base import AIProvider
from jarvis.brain.providers.groq_provider import GroqProvider


def get_provider() -> AIProvider:
    if config.AI_PROVIDER == "groq":
        return GroqProvider(api_key=config.GROQ_API_KEY)
    raise ValueError(f"Provedor de IA desconhecido: {config.AI_PROVIDER}")
