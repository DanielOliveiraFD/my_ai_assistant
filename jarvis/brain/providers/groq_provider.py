"""Implementação de AIProvider usando a API do Groq.

Toda referência ao SDK/modelo do Groq, incluindo o formato específico de
tool calling da API, fica isolada neste arquivo.
"""

import json

from groq import Groq

from jarvis.brain.base import AIProvider, ChatResult, ToolCall

MODEL = "qwen/qwen3.6-27b"


class GroqProvider(AIProvider):
    def __init__(self, api_key: str):
        self._client = Groq(api_key=api_key)

    def chat(self, messages: list[dict], tools: list[dict] | None = None) -> ChatResult:
        # reasoning_effort="none" desliga o modo de raciocínio: este é um
        # assistente de diálogo geral, não precisa de "pensar em voz alta",
        # e deixar ligado arrisca vazar texto de raciocínio na resposta
        # final (bug conhecido com modelos de raciocínio no Groq).
        kwargs = {"model": MODEL, "messages": messages, "reasoning_effort": "none"}
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"

        response = self._client.chat.completions.create(**kwargs)
        message = response.choices[0].message

        if message.tool_calls:
            calls = [
                ToolCall(
                    id=call.id,
                    name=call.function.name,
                    arguments=json.loads(call.function.arguments),
                )
                for call in message.tool_calls
            ]
            return ChatResult(content=None, tool_calls=calls)

        return ChatResult(content=message.content.strip())
