"""Cérebro do assistente: mantém o histórico da conversa e delega ao provedor de IA configurado."""

from jarvis import config
from jarvis.brain.factory import get_provider


class Brain:
    def __init__(self):
        self._provider = get_provider()
        self.history = [{"role": "system", "content": config.SYSTEM_PROMPT}]

    def ask(self, user_text: str) -> str:
        self.history.append({"role": "user", "content": user_text})
        reply = self._provider.chat(self.history)
        self.history.append({"role": "assistant", "content": reply})
        return reply

    def reset(self):
        self.history = self.history[:1]
