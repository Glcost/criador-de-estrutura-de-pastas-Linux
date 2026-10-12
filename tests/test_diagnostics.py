"""Testes do modulo de diagnostico."""

from pathlib import Path

from devtoolkit import diagnostics
from devtoolkit.diagnostics import (
    check_command,
    check_disk_space,
    check_operating_system,
    read_os_release,
)


def test_read_os_release(tmp_path: Path) -> None:
    release_file = tmp_path / "os-release"
    release_file.write_text(
        'ID=linuxmint\n'
        'PRETTY_NAME="Linux Mint Teste"\n'
        '# comentario\n',
        encoding="utf-8",
    )

    result = read_os_release(release_file)

    assert result["ID"] == "linuxmint"
    assert result["PRETTY_NAME"] == "Linux Mint Teste"


def test_read_os_release_when_missing(tmp_path: Path) -> None:
    result = read_os_release(tmp_path / "nao-existe")

    assert result == {}


def test_check_command_found(monkeypatch) -> None:
    monkeypatch.setattr(
        diagnostics.shutil,
        "which",
        lambda command: f"/usr/bin/{command}",
    )

    result = check_command("git")

    assert result.available is True
    assert result.details == "/usr/bin/git"


def test_check_command_missing(monkeypatch) -> None:
    monkeypatch.setattr(
        diagnostics.shutil,
        "which",
        lambda command: None,
    )

    result = check_command("node")

    assert result.available is False
    assert "Nao encontrado" in result.details


def test_check_operating_system_mint(monkeypatch) -> None:
    monkeypatch.setattr(
        diagnostics.platform,
        "system",
        lambda: "Linux",
    )
    monkeypatch.setattr(
        diagnostics,
        "read_os_release",
        lambda: {
            "ID": "linuxmint",
            "PRETTY_NAME": "Linux Mint Teste",
        },
    )

    result = check_operating_system()

    assert result.available is True
    assert result.details == "Linux Mint Teste"


def test_check_operating_system_unsupported(monkeypatch) -> None:
    monkeypatch.setattr(
        diagnostics.platform,
        "system",
        lambda: "Linux",
    )
    monkeypatch.setattr(
        diagnostics,
        "read_os_release",
        lambda: {
            "ID": "ubuntu",
            "PRETTY_NAME": "Ubuntu",
        },
    )

    result = check_operating_system()

    assert result.available is False


def test_check_disk_space(tmp_path: Path, monkeypatch) -> None:
    class FakeUsage:
        total = 10 * 1024**3
        used = 5 * 1024**3
        free = 5 * 1024**3

    monkeypatch.setattr(
        diagnostics.shutil,
        "disk_usage",
        lambda path: FakeUsage(),
    )

    result = check_disk_space(tmp_path)

    assert result.available is True
    assert "5.00 GiB" in result.details