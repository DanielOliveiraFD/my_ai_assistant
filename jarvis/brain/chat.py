"""Cérebro do assistente: conversa com o Groq mantendo histórico da sessão."""

from groq import Groq

from jarvis import config

_client = Groq(api_key=config.GROQ_API_KEY)


class Brain:
    def __init__(self):
        self.history = [{"role": "system", "content": config.SYSTEM_PROMPT}]

    def ask(self, user_text: str) -> str:
        self.history.append({"role": "user", "content": user_text})
        response = _client.chat.completions.create(
            model=config.BRAIN_MODEL,
            messages=self.history,
        )
        reply = response.choices[0].message.content.strip()
        self.history.append({"role": "assistant", "content": reply})
        return reply

    def reset(self):
        self.history = self.history[:1]
