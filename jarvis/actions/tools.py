"""Ferramentas de ação no macOS expostas ao cérebro: schema (formato
OpenAI/Groq) e as funções que executam.

Isoladas do resto do projeto — só jarvis/brain/chat.py importa daqui.
"""

from jarvis.actions import apps, safari, system

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
    {
        "type": "function",
        "function": {
            "name": "ajustar_volume",
            "description": (
                "Define o volume do sistema para um valor exato (0-100). "
                "Use quando o usuário pedir um número específico (ex: "
                "'coloca o volume em 50%')."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "nivel": {"type": "integer", "description": "0 a 100."}
                },
                "required": ["nivel"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "aumentar_ou_diminuir_volume",
            "description": (
                "Aumenta ou diminui o volume em relação ao atual (ex: "
                "'aumenta o volume', 'abaixa um pouco'). Positivo para "
                "aumentar, negativo para diminuir."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "delta": {
                        "type": "integer",
                        "description": "Quanto ajustar, ex: 10 para aumentar, -10 para diminuir.",
                    }
                },
                "required": ["delta"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "silenciar_volume",
            "description": "Silencia ou reativa o som do sistema.",
            "parameters": {
                "type": "object",
                "properties": {
                    "mudo": {
                        "type": "boolean",
                        "description": "true para silenciar, false para reativar.",
                    }
                },
                "required": ["mudo"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "ajustar_brilho",
            "description": (
                "Aumenta ou diminui o brilho da tela em passos. Não é "
                "possível definir uma porcentagem exata — o macOS não tem "
                "esse comando nativo, só relativo. Positivo para "
                "aumentar, negativo para diminuir."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "passos": {
                        "type": "integer",
                        "description": "Quantos passos ajustar, ex: 2 para aumentar, -2 para diminuir.",
                    }
                },
                "required": ["passos"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "ajustar_modo_escuro",
            "description": (
                "Liga, desliga ou alterna o modo escuro do sistema. "
                "Omitir 'ativar' (ou mandar null) para apenas alternar "
                "entre claro e escuro."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "ativar": {
                        "type": ["boolean", "null"],
                        "description": "true para ligar, false para desligar, null para alternar.",
                    }
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "tirar_print_de_tela",
            "description": "Tira um print (screenshot) da tela inteira e salva na Área de Trabalho.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "ativar_modo_foco",
            "description": (
                "Ativa um Modo de Foco específico (ex: Trabalho, Não "
                "Perturbe) rodando um atalho do app Atalhos com esse "
                "nome. SÓ funciona se o usuário já tiver criado um "
                "atalho com esse nome exato no app Atalhos — não existe "
                "comando nativo para ativar um Modo de Foco direto por "
                "script. Se der erro de atalho não encontrado, avise o "
                "usuário que ele precisa criar esse atalho primeiro no "
                "app Atalhos."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "nome": {
                        "type": "string",
                        "description": "Nome exato do atalho/Modo de Foco.",
                    }
                },
                "required": ["nome"],
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


def ajustar_volume(nivel: int) -> dict:
    return {"resultado": system.set_volume(nivel)}


def aumentar_ou_diminuir_volume(delta: int) -> dict:
    return {"resultado": system.adjust_volume(delta)}


def silenciar_volume(mudo: bool) -> dict:
    return {"resultado": system.mute(mudo)}


def ajustar_brilho(passos: int) -> dict:
    return {"resultado": system.adjust_brightness(passos)}


def ajustar_modo_escuro(ativar: bool | None = None) -> dict:
    return {"resultado": system.set_dark_mode(ativar)}


def tirar_print_de_tela() -> dict:
    return {"resultado": system.take_screenshot()}


def ativar_modo_foco(nome: str) -> dict:
    return {"resultado": system.run_shortcut(nome)}


DISPATCH = {
    "abrir_aplicativo": abrir_aplicativo,
    "pesquisar_no_safari": pesquisar_no_safari,
    "abrir_site_no_safari": abrir_site_no_safari,
    "ajustar_volume": ajustar_volume,
    "aumentar_ou_diminuir_volume": aumentar_ou_diminuir_volume,
    "silenciar_volume": silenciar_volume,
    "ajustar_brilho": ajustar_brilho,
    "ajustar_modo_escuro": ajustar_modo_escuro,
    "tirar_print_de_tela": tirar_print_de_tela,
    "ativar_modo_foco": ativar_modo_foco,
}
