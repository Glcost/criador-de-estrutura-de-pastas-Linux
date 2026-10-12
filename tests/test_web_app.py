"""Testes da interface web local."""

from pathlib import Path

import pytest

fastapi = pytest.importorskip("fastapi")
httpx = pytest.importorskip("httpx")
from fastapi.testclient import TestClient

from devtoolkit.web_app import app

client = TestClient(app)


def test_home_page_is_served() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "DevToolkit" in response.text
    assert "styles.css" in response.text


def test_templates_endpoint_lists_supported_templates() -> None:
    response = client.get("/api/templates")
    assert response.status_code == 200
    assert [item["id"] for item in response.json()["templates"]] == [
        "python", "node", "web", "api", "react"
    ]


def test_preview_returns_files_without_creating_project(tmp_path: Path) -> None:
    response = client.post(
        "/api/preview",
        json={
            "name": "minha-api",
            "template": "api",
            "destination": str(tmp_path),
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert any(item["path"] == "app.py" for item in payload["files"])
    assert not (tmp_path / "minha-api").exists()


def test_preview_rejects_invalid_project_name(tmp_path: Path) -> None:
    response = client.post(
        "/api/preview",
        json={
            "name": "../fora",
            "template": "python",
            "destination": str(tmp_path),
        },
    )
    assert response.status_code == 400


def test_create_endpoint_creates_project(tmp_path: Path) -> None:
    response = client.post(
        "/api/create",
        json={
            "name": "projeto-web",
            "template": "web",
            "destination": str(tmp_path),
        },
    )
    assert response.status_code == 200
    assert (tmp_path / "projeto-web" / "index.html").is_file()


def test_create_endpoint_does_not_overwrite_existing_project(tmp_path: Path) -> None:
    project = tmp_path / "projeto-web"
    project.mkdir()
    important = project / "important.txt"
    important.write_text("preservar", encoding="utf-8")

    response = client.post(
        "/api/create",
        json={
            "name": "projeto-web",
            "template": "web",
            "destination": str(tmp_path),
        },
    )
    assert response.status_code == 400
    assert important.read_text(encoding="utf-8") == "preservar"
