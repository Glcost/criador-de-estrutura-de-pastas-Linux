"""Interface web local do DevToolkit."""

from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from devtoolkit.diagnostics import run_diagnostics
from devtoolkit.project_creator import (
    SUPPORTED_TEMPLATES,
    ProjectCreationError,
    create_project,
    get_template_files,
    validate_project_name,
)

WEB_DIR = Path(__file__).parent / "web"

app = FastAPI(
    title="DevToolkit",
    description="Interface local para criar projetos de desenvolvimento.",
    version="0.1.0",
)


class ProjectRequest(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    template: Literal["python", "node", "web", "api", "react"]
    destination: str = Field(min_length=1, max_length=500)


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    """Entrega a página inicial."""
    return FileResponse(WEB_DIR / "index.html")


@app.get("/assets/{asset_name}", include_in_schema=False)
def asset(asset_name: str) -> FileResponse:
    """Entrega somente arquivos estáticos conhecidos."""
    if asset_name not in {"styles.css", "app.js"}:
        raise HTTPException(status_code=404, detail="Arquivo não encontrado.")
    return FileResponse(WEB_DIR / asset_name)


@app.get("/api/diagnostics")
def diagnostics() -> dict[str, object]:
    """Retorna o diagnóstico do ambiente local."""
    results = run_diagnostics()
    return {
        "checks": [
            {
                "name": item.name,
                "available": item.available,
                "details": item.details,
            }
            for item in results
        ],
        "supported": bool(results and results[0].available),
    }


@app.get("/api/templates")
def templates() -> dict[str, list[dict[str, str]]]:
    """Lista os templates aceitos pelo gerador existente."""
    descriptions = {
        "python": "Script Python com ponto de entrada simples.",
        "node": "Aplicação Node.js com npm start.",
        "web": "HTML, CSS e JavaScript sem framework.",
        "api": "API Python usando FastAPI.",
        "react": "Frontend React com Vite.",
    }
    return {
        "templates": [
            {"id": template, "description": descriptions[template]}
            for template in SUPPORTED_TEMPLATES
        ]
    }


@app.post("/api/preview")
def preview_project(request: ProjectRequest) -> dict[str, object]:
    """Pré-visualiza os arquivos que o gerador criaria."""
    try:
        validate_project_name(request.name)
        files = get_template_files(request.name, request.template)
    except ProjectCreationError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    return {
        "name": request.name,
        "template": request.template,
        "destination": str(Path(request.destination).expanduser()),
        "files": [
            {
                "path": path,
                "content": content,
            }
            for path, content in files.items()
        ],
    }


@app.post("/api/create")
def create_project_from_web(request: ProjectRequest) -> dict[str, str]:
    """Cria o projeto usando a implementação existente."""
    try:
        project_path = create_project(
            name=request.name,
            template=request.template,
            destination=Path(request.destination),
        )
    except ProjectCreationError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    return {
        "message": "Projeto criado com sucesso.",
        "path": str(project_path),
        "name": request.name,
        "template": request.template,
    }
