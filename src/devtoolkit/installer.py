
"""Instala ferramentas de desenvolvimento no Linux Mint."""

import platform
import shutil
import subprocess
import sys


SUPPORTED_TOOLS: dict[str, dict[str, str]] = {
    "git": {
        "package": "git",
        "description": "Git — controle de versão",
    },
    "python3": {
        "package": "python3",
        "description": "Python 3 — linguagem de programação",
    },
    "node": {
        "package": "nodejs",
        "description": "Node.js — ambiente JavaScript",
    },
    "npm": {
        "package": "npm",
        "description": "npm — gerenciador de pacotes Node.js",
    },
}


def install_tool(tool: str) -> int:
    """Instala uma ferramenta permitida após confirmação explícita."""

    if platform.system() != "Linux":
        print(
            "Erro: este instalador foi preparado para Linux Mint.",
            file=sys.stderr,
        )
        return 1

    if tool not in SUPPORTED_TOOLS:
        print(f"Erro: ferramenta não permitida: {tool}", file=sys.stderr)
        return 1

    tool_info = SUPPORTED_TOOLS[tool]
    package = tool_info["package"]
    description = tool_info["description"]

    if shutil.which(tool) is not None:
        print(f"{description} já está instalado.")
        return 0

    if shutil.which("apt") is None:
        print(
            "Erro: o gerenciador de pacotes apt não foi encontrado.",
            file=sys.stderr,
        )
        return 1

    print(f"\nFerramenta: {description}")
    print(f"Pacote a instalar: {package}")
    print("Comando previsto: sudo apt install " + package)

    try:
        answer = input("\nDeseja continuar? [s/N]: ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print("\nInstalação cancelada.")
        return 1

    if answer not in {"s", "sim"}:
        print("Instalação cancelada. Nenhuma alteração foi solicitada.")
        return 0

    print(f"\nIniciando a instalação de {package}...")

    try:
        result = subprocess.run(
            ["sudo", "apt", "install", package],
            check=False,
        )
    except FileNotFoundError:
        print(
            "Erro: não foi possível iniciar o comando de instalação.",
            file=sys.stderr,
        )
        return 1
    except KeyboardInterrupt:
        print("\nInstalação interrompida.")
        return 130

    if result.returncode != 0:
        print(
            "A instalação falhou ou foi interrompida. "
            "Confira as mensagens exibidas pelo apt.",
            file=sys.stderr,
        )
        return result.returncode or 1

    if shutil.which(tool) is None:
        print(
            "O instalador terminou, mas a ferramenta não foi encontrada "
            "no PATH. Verifique a instalação.",
            file=sys.stderr,
        )
        return 1

    print(f"\n{description} instalado e detectado com sucesso.")
    return 0
