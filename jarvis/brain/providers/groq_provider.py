"""Implementação de AIProvider usando a API do Groq.

Toda referência ao SDK/modelo do Groq fica isolada neste arquivo.
"""

from groq import Groq

from jarvis.brain.base import AIProvider

MODEL = "llama-3.3-70b-versatile"


class GroqProvider(AIProvider):
    def __init__(self, api_key: str):
        self._client = Groq(api_key=api_key)

    def chat(self, messages: list[dict]) -> str:
        response = self._client.chat.completions.create(
            model=MODEL,
            messages=messages,
        )
        return response.choices[0].message.content.strip()
