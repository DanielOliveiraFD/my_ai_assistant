"""App de barra de menu do macOS: liga/desliga o Jarvis sem precisar do
Terminal. Roda o loop principal (jarvis/orchestrator.py) numa thread de
segundo plano, controlada pelos itens de menu Ligar/Desligar.

Rodar diretamente (para testar):
    python -m jarvis.app

Ou instalado como LaunchAgent (ver macos/README.md) para iniciar sozinho no
login, sem Terminal nenhum aberto.
"""

import threading

import rumps

from jarvis import orchestrator


class JarvisMenuBarApp(rumps.App):
    def __init__(self):
        super().__init__("Jarvis", title="⚪ Jarvis", quit_button=None)
        self.menu = [
            rumps.MenuItem("Ligar", callback=self.ligar),
            rumps.MenuItem("Desligar", callback=self.desligar),
            None,
            rumps.MenuItem("Sair", callback=self.sair),
        ]
        self._stop_event = None
        self._thread = None
        self._update_menu_state(running=False)

    def ligar(self, _sender):
        if self._thread is not None and self._thread.is_alive():
            return

        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._run_orchestrator, daemon=True)
        self._thread.start()
        self._update_menu_state(running=True)

    def desligar(self, _sender):
        if self._stop_event is not None:
            self._stop_event.set()
        self._update_menu_state(running=False)

    def sair(self, _sender):
        if self._stop_event is not None:
            self._stop_event.set()
        rumps.quit_application()

    def _run_orchestrator(self):
        try:
            orchestrator.run(stop_event=self._stop_event)
        except Exception as exc:  # nunca deixar a thread morrer em silêncio
            print(f"[app] erro no orchestrator: {exc}")
        finally:
            self._update_menu_state(running=False)

    def _update_menu_state(self, running: bool):
        self.menu["Ligar"].state = running
        self.menu["Desligar"].state = not running
        self.title = "🟢 Jarvis" if running else "⚪ Jarvis"


def main():
    JarvisMenuBarApp().run()


if __name__ == "__main__":
    main()
