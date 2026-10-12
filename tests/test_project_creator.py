
"""Testes do gerador de projetos."""

import json
from pathlib import Path

import pytest

from devtoolkit.project_creator import (
    SUPPORTED_TEMPLATES,
    ProjectCreationError,
    create_project,
    get_template_files,
    validate_project_name,
)


@pytest.mark.parametrize(
    "name",
    ["meu-projeto", "app1", "projeto_web", "a"],
)
def test_valid_project_names(name: str) -> None:
    validate_project_name(name)


@pytest.mark.parametrize(
    "name",
    [
        "",
        "MeuProjeto",
        "1projeto",
        "../invasao",
        "projeto/arquivo",
        "a" * 51,
    ],
)
def test_invalid_project_names(name: str) -> None:
    with pytest.raises(ProjectCreationError):
        validate_project_name(name)


@pytest.mark.parametrize("template", SUPPORTED_TEMPLATES)
def test_create_project_templates(
    tmp_path: Path,
    template: str,
) -> None:
    project_path = create_project(
        name="meu-projeto",
        template=template,
        destination=tmp_path,
    )

    assert project_path.is_dir()
    assert (project_path / "README.md").is_file()
    assert (project_path / ".gitignore").is_file()


def test_python_template_contains_entry_point(
    tmp_path: Path,
) -> None:
    project_path = create_project(
        name="app-python",
        template="python",
        destination=tmp_path,
    )

    app_file = project_path / "app.py"

    assert app_file.is_file()
    assert "def main()" in app_file.read_text(encoding="utf-8")


def test_node_template_has_valid_package_json(
    tmp_path: Path,
) -> None:
    project_path = create_project(
        name="app-node",
        template="node",
        destination=tmp_path,
    )

    package = json.loads(
        (project_path / "package.json").read_text(encoding="utf-8")
    )

    assert package["name"] == "app-node"
    assert package["type"] == "module"
    assert package["scripts"]["start"] == "node src/index.js"


def test_web_template_contains_html(
    tmp_path: Path,
) -> None:
    project_path = create_project(
        name="app-web",
        template="web",
        destination=tmp_path,
    )

    html = (project_path / "index.html").read_text(encoding="utf-8")

    assert "<!doctype html>" in html
    assert 'lang="pt-BR"' in html


def test_api_template_contains_fastapi_endpoints(
    tmp_path: Path,
) -> None:
    project_path = create_project(
        name="minha-api",
        template="api",
        destination=tmp_path,
    )

    app = (project_path / "app.py").read_text(encoding="utf-8")
    requirements = (
        project_path / "requirements.txt"
    ).read_text(encoding="utf-8")
    readme = (project_path / "README.md").read_text(encoding="utf-8")

    assert "from fastapi import FastAPI" in app
    assert 'app = FastAPI(title="minha-api"' in app
    assert '@app.get("/")' in app
    assert '@app.get("/health")' in app
    assert "fastapi" in requirements.lower()
    assert "uvicorn" in requirements.lower()
    assert "uvicorn app:app --reload" in readme


def test_react_template_has_valid_package_json(
    tmp_path: Path,
) -> None:
    project_path = create_project(
        name="meu-frontend",
        template="react",
        destination=tmp_path,
    )

    package = json.loads(
        (project_path / "package.json").read_text(encoding="utf-8")
    )

    assert package["name"] == "meu-frontend"
    assert package["private"] is True
    assert package["type"] == "module"
    assert package["scripts"]["dev"] == "vite"
    assert package["scripts"]["build"] == "vite build"
    assert "react" in package["dependencies"]
    assert "react-dom" in package["dependencies"]
    assert "vite" in package["devDependencies"]
    assert "@vitejs/plugin-react" in package["devDependencies"]


def test_react_template_contains_entry_files(
    tmp_path: Path,
) -> None:
    project_path = create_project(
        name="meu-frontend",
        template="react",
        destination=tmp_path,
    )

    expected_files = [
        "index.html",
        "vite.config.js",
        "src/main.jsx",
        "src/App.jsx",
        "src/style.css",
    ]

    for relative_path in expected_files:
        assert (project_path / relative_path).is_file(), relative_path

    html = (project_path / "index.html").read_text(encoding="utf-8")
    app = (project_path / "src/App.jsx").read_text(encoding="utf-8")

    assert 'id="root"' in html
    assert "/src/main.jsx" in html
    assert "useState" in app
    assert "setCount" in app


def test_existing_project_is_not_overwritten(
    tmp_path: Path,
) -> None:
    project_path = tmp_path / "meu-projeto"
    project_path.mkdir()

    original_file = project_path / "importante.txt"
    original_file.write_text("nao apagar", encoding="utf-8")

    with pytest.raises(ProjectCreationError):
        create_project(
            name="meu-projeto",
            template="python",
            destination=tmp_path,
        )

    assert original_file.read_text(encoding="utf-8") == "nao apagar"


def test_unknown_template_is_rejected() -> None:
    with pytest.raises(ProjectCreationError):
        get_template_files("meu-projeto", "desconhecido")


def test_create_project_rejects_unknown_template(
    tmp_path: Path,
) -> None:
    with pytest.raises(ProjectCreationError):
        create_project(
            name="meu-projeto",
            template="desconhecido",
            destination=tmp_path,
        )

    assert not (tmp_path / "meu-projeto").exists()
