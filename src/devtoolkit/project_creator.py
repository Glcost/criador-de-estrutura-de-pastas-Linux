
"""Criacao segura de estruturas iniciais de projetos."""

import json
import re
import shutil
from pathlib import Path


PROJECT_NAME_PATTERN = re.compile(r"^[a-z][a-z0-9_-]{0,49}$")

SUPPORTED_TEMPLATES = ("python", "node", "web", "api", "react")


class ProjectCreationError(Exception):
    """Erro esperado durante a criacao de um projeto."""


def validate_project_name(name: str) -> None:
    """Valida o nome do projeto antes de criar arquivos."""

    if not PROJECT_NAME_PATTERN.fullmatch(name):
        raise ProjectCreationError(
            "Nome invalido. Use letras minusculas no inicio e, "
            "depois, apenas letras minusculas, numeros, '_' ou '-'. "
            "Limite: 50 caracteres."
        )


def get_template_files(name: str, template: str) -> dict[str, str]:
    """Retorna os arquivos do template escolhido."""

    if template == "python":
        return {
            "app.py": (
                "def main() -> None:\n"
                f'    print("Projeto {name} iniciado.")\n'
                "\n"
                "\n"
                'if __name__ == "__main__":\n'
                "    main()\n"
            ),
            "README.md": (
                f"# {name}\n\n"
                "Projeto Python criado pelo DevToolkit.\n\n"
                "## Executar\n\n"
                "```bash\n"
                "python3 app.py\n"
                "```\n"
            ),
            ".gitignore": (
                "__pycache__/\n"
                "*.py[cod]\n"
                ".venv/\n"
                ".env\n"
                ".pytest_cache/\n"
            ),
        }

    if template == "node":
        package = {
            "name": name,
            "version": "1.0.0",
            "private": True,
            "type": "module",
            "scripts": {
                "start": "node src/index.js",
            },
        }

        return {
            "package.json": (
                json.dumps(package, indent=2, ensure_ascii=False) + "\n"
            ),
            "src/index.js": (
                f'console.log("Projeto {name} iniciado.");\n'
            ),
            "README.md": (
                f"# {name}\n\n"
                "Projeto Node.js criado pelo DevToolkit.\n\n"
                "## Executar\n\n"
                "```bash\n"
                "npm start\n"
                "```\n"
            ),
            ".gitignore": (
                "node_modules/\n"
                "dist/\n"
                ".env\n"
                ".env.*\n"
                "!.env.example\n"
            ),
        }

    if template == "web":
        return {
            "index.html": (
                "<!doctype html>\n"
                '<html lang="pt-BR">\n'
                "<head>\n"
                '  <meta charset="UTF-8">\n'
                '  <meta name="viewport" '
                'content="width=device-width, initial-scale=1.0">\n'
                f"  <title>{name}</title>\n"
                '  <link rel="stylesheet" href="style.css">\n'
                "</head>\n"
                "<body>\n"
                f"  <main><h1>{name}</h1>"
                "<p>Projeto criado pelo DevToolkit.</p></main>\n"
                '  <script src="script.js"></script>\n'
                "</body>\n"
                "</html>\n"
            ),
            "style.css": (
                "body {\n"
                "    margin: 0;\n"
                "    padding: 2rem;\n"
                "    font-family: system-ui, sans-serif;\n"
                "    line-height: 1.5;\n"
                "}\n"
            ),
            "script.js": (
                'console.log("DevToolkit: projeto carregado.");\n'
            ),
            "README.md": (
                f"# {name}\n\n"
                "Projeto web estatico criado pelo DevToolkit.\n\n"
                "Abra `index.html` no navegador para visualizar.\n"
            ),
            ".gitignore": (
                ".env\n"
                ".env.*\n"
                "!.env.example\n"
                ".DS_Store\n"
            ),
        }

    if template == "api":
        return {
            "app.py": (
                "from fastapi import FastAPI\n"
                "\n"
                f'app = FastAPI(title="{name}", version="0.1.0")\n'
                "\n"
                "\n"
                '@app.get("/")\n'
                "def read_root() -> dict[str, str]:\n"
                "    return {\n"
                f'        "message": "API {name} funcionando",\n'
                '        "status": "ok",\n'
                "    }\n"
                "\n"
                "\n"
                '@app.get("/health")\n'
                "def health_check() -> dict[str, str]:\n"
                '    return {"status": "healthy"}\n'
            ),
            "requirements.txt": (
                "fastapi>=0.115.0,<1.0.0\n"
                "uvicorn[standard]>=0.30.0,<1.0.0\n"
            ),
            "README.md": (
                f"# {name}\n\n"
                "API Python criada pelo DevToolkit com FastAPI.\n\n"
                "## Requisitos\n\n"
                "- Python 3.10 ou superior.\n\n"
                "## Instalar dependencias\n\n"
                "```bash\n"
                "python3 -m venv .venv\n"
                "source .venv/bin/activate\n"
                "python -m pip install -r requirements.txt\n"
                "```\n\n"
                "## Executar\n\n"
                "```bash\n"
                "uvicorn app:app --reload\n"
                "```\n\n"
                "A API ficara disponivel em `http://127.0.0.1:8000`.\n\n"
                "Documentacao interativa: `http://127.0.0.1:8000/docs`.\n\n"
                "Verificacao de saude: `http://127.0.0.1:8000/health`.\n"
            ),
            ".gitignore": (
                "__pycache__/\n"
                "*.py[cod]\n"
                ".venv/\n"
                ".env\n"
                ".pytest_cache/\n"
            ),
        }

    if template == "react":
        package = {
            "name": name,
            "version": "1.0.0",
            "private": True,
            "type": "module",
            "scripts": {
                "dev": "vite",
                "build": "vite build",
                "preview": "vite preview",
            },
            "dependencies": {
                "react": "^19.0.0",
                "react-dom": "^19.0.0",
            },
            "devDependencies": {
                "@vitejs/plugin-react": "^4.4.1",
                "vite": "^6.3.5",
            },
        }

        return {
            "package.json": (
                json.dumps(package, indent=2, ensure_ascii=False) + "\n"
            ),
            "index.html": (
                "<!doctype html>\n"
                '<html lang="pt-BR">\n'
                "<head>\n"
                '  <meta charset="UTF-8">\n'
                '  <meta name="viewport" '
                'content="width=device-width, initial-scale=1.0">\n'
                f"  <title>{name}</title>\n"
                "</head>\n"
                "<body>\n"
                '  <div id="root"></div>\n'
                '  <script type="module" src="/src/main.jsx"></script>\n'
                "</body>\n"
                "</html>\n"
            ),
            "vite.config.js": (
                'import { defineConfig } from "vite";\n'
                'import react from "@vitejs/plugin-react";\n'
                "\n"
                "export default defineConfig({\n"
                "  plugins: [react()],\n"
                "});\n"
            ),
            "src/main.jsx": (
                'import { StrictMode } from "react";\n'
                'import { createRoot } from "react-dom/client";\n'
                'import App from "./App.jsx";\n'
                'import "./style.css";\n'
                "\n"
                'createRoot(document.getElementById("root")).render(\n'
                "  <StrictMode>\n"
                "    <App />\n"
                "  </StrictMode>,\n"
                ");\n"
            ),
            "src/App.jsx": (
                'import { useState } from "react";\n'
                "\n"
                "export default function App() {\n"
                "  const [count, setCount] = useState(0);\n"
                "\n"
                "  return (\n"
                "    <main className=\"container\">\n"
                f"      <h1>{name}</h1>\n"
                "      <p>Projeto React criado pelo DevToolkit.</p>\n"
                "      <button onClick={() => setCount((value) => value + 1)}>\n"
                "        Cliques: {count}\n"
                "      </button>\n"
                "    </main>\n"
                "  );\n"
                "}\n"
            ),
            "src/style.css": (
                ":root {\n"
                '  font-family: Inter, system-ui, sans-serif;\n'
                "  color: #1e293b;\n"
                "  background: #f8fafc;\n"
                "  font-synthesis: none;\n"
                "  text-rendering: optimizeLegibility;\n"
                "}\n"
                "\n"
                "* {\n"
                "  box-sizing: border-box;\n"
                "}\n"
                "\n"
                "body {\n"
                "  margin: 0;\n"
                "  min-width: 320px;\n"
                "  min-height: 100vh;\n"
                "}\n"
                "\n"
                ".container {\n"
                "  max-width: 720px;\n"
                "  margin: 0 auto;\n"
                "  padding: 4rem 1.5rem;\n"
                "}\n"
                "\n"
                "button {\n"
                "  padding: 0.75rem 1rem;\n"
                "  border: 0;\n"
                "  border-radius: 0.5rem;\n"
                "  background: #2563eb;\n"
                "  color: white;\n"
                "  font: inherit;\n"
                "  cursor: pointer;\n"
                "}\n"
                "\n"
                "button:hover {\n"
                "  background: #1d4ed8;\n"
                "}\n"
            ),
            "README.md": (
                f"# {name}\n\n"
                "Projeto React criado pelo DevToolkit com Vite.\n\n"
                "## Requisitos\n\n"
                "- Node.js compativel com a versao do Vite.\n"
                "- npm.\n\n"
                "## Instalar dependencias\n\n"
                "```bash\n"
                "npm install\n"
                "```\n\n"
                "## Executar em desenvolvimento\n\n"
                "```bash\n"
                "npm run dev\n"
                "```\n\n"
                "## Gerar versao de producao\n\n"
                "```bash\n"
                "npm run build\n"
                "```\n\n"
                "Os arquivos de producao serao gerados na pasta `dist/`.\n"
            ),
            ".gitignore": (
                "node_modules/\n"
                "dist/\n"
                ".env\n"
                ".env.*\n"
                "!.env.example\n"
                ".DS_Store\n"
            ),
        }

    raise ProjectCreationError(f"Template desconhecido: {template}")


def create_project(
    name: str,
    template: str,
    destination: Path,
) -> Path:
    """Cria o projeto sem sobrescrever arquivos existentes."""

    validate_project_name(name)

    if template not in SUPPORTED_TEMPLATES:
        raise ProjectCreationError(
            f"Template desconhecido: {template}"
        )

    destination = destination.expanduser().resolve()
    project_path = destination / name

    if project_path.exists():
        raise ProjectCreationError(
            f"O destino ja existe: {project_path}"
        )

    files = get_template_files(name, template)

    try:
        destination.mkdir(parents=True, exist_ok=True)
        project_path.mkdir()

        for relative_path, content in files.items():
            file_path = project_path / relative_path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content, encoding="utf-8")

    except OSError as error:
        if project_path.exists():
            shutil.rmtree(project_path, ignore_errors=True)

        raise ProjectCreationError(
            f"Nao foi possivel criar o projeto: {error}"
        ) from error

    return project_path
