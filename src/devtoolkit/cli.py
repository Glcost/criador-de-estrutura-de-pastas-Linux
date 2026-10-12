
"""Interface de linha de comando do DevToolkit."""

import argparse
import sys
from pathlib import Path

from devtoolkit import __version__
from devtoolkit.diagnostics import run_diagnostics
from devtoolkit.installer import SUPPORTED_TOOLS, install_tool
from devtoolkit.project_creator import (
    SUPPORTED_TEMPLATES,
    ProjectCreationError,
    create_project,
)


def build_parser() -> argparse.ArgumentParser:
    """Monta os comandos e argumentos da CLI."""

    parser = argparse.ArgumentParser(
        prog="devtoolkit",
        description="Kit de automacao para desenvolvimento Linux.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    commands = parser.add_subparsers(
        dest="command",
        required=True,
    )

    commands.add_parser(
        "web",
        help="Abre a interface web local do DevToolkit.",
    )

    commands.add_parser(
        "doctor",
        help="Verifica o sistema e as ferramentas instaladas.",
    )

    create_parser = commands.add_parser(
        "create",
        help="Cria um projeto a partir de um template.",
    )
    create_parser.add_argument(
        "name",
        help="Nome do novo projeto.",
    )
    create_parser.add_argument(
        "--template",
        required=True,
        choices=SUPPORTED_TEMPLATES,
        help="Tipo de projeto.",
    )
    create_parser.add_argument(
        "--dest",
        type=Path,
        default=Path.cwd(),
        help="Pasta onde o projeto sera criado.",
    )

    install_parser = commands.add_parser(
        "install",
        help="Instala uma ferramenta apos confirmacao.",
    )
    install_parser.add_argument(
        "tool",
        choices=sorted(SUPPORTED_TOOLS),
        help="Ferramenta que deseja instalar.",
    )

    return parser


def run_doctor() -> int:
    """Exibe os resultados do diagnostico."""

    results = run_diagnostics()

    print("\nDevToolkit - Diagnostico do ambiente\n")

    for result in results:
        status = "OK" if result.available else "AVISO"
        print(f"[{status}] {result.name}: {result.details}")

    if not results or not results[0].available:
        print(
            "\nO sistema nao foi identificado como Linux Mint. "
            "Revise a compatibilidade antes de executar automacoes."
        )
        return 1

    print("\nDiagnostico concluido.")
    return 0


def run_create(args: argparse.Namespace) -> int:
    """Executa a criacao de um projeto."""

    try:
        project_path = create_project(
            name=args.name,
            template=args.template,
            destination=args.dest,
        )
    except ProjectCreationError as error:
        print(f"Erro: {error}", file=sys.stderr)
        return 1

    print(f"Projeto criado em: {project_path}")
    print("\nProximos passos:")

    if args.template == "python":
        print(f"  cd {project_path}")
        print("  python3 app.py")
    elif args.template == "node":
        print(f"  cd {project_path}")
        print("  npm start")
    elif args.template == "web":
        print(f"  cd {project_path}")
        print("  Abra index.html no navegador.")
    elif args.template == "api":
        print(f"  cd {project_path}")
        print("  python3 -m venv .venv")
        print("  source .venv/bin/activate")
        print("  python -m pip install -r requirements.txt")
        print("  uvicorn app:app --reload")
    elif args.template == "react":
        print(f"  cd {project_path}")
        print("  npm install")
        print("  npm run dev")

    return 0


def main() -> int:
    """Ponto de entrada da aplicacao."""

    parser = build_parser()
    args = parser.parse_args()

    if args.command == "web":
        try:
            import uvicorn
        except ImportError:
            print(
                "A interface web requer dependencias extras. Execute: "
                "python -m pip install -e '.[web]'",
                file=sys.stderr,
            )
            return 1

        uvicorn.run(
            "devtoolkit.web_app:app",
            host="127.0.0.1",
            port=8765,
            reload=False,
        )
        return 0

    if args.command == "doctor":
        return run_doctor()

    if args.command == "create":
        return run_create(args)

    if args.command == "install":
        return install_tool(args.tool)

    parser.error("Comando nao implementado.")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
