
"""Diagnóstico do sistema e das ferramentas de desenvolvimento."""

import platform
import shutil
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CheckResult:
    """Representa o resultado de uma verificação."""

    name: str
    available: bool
    details: str


def read_os_release(
    file_path: Path = Path("/etc/os-release"),
) -> dict[str, str]:
    """Lê as informações do sistema operacional."""

    if not file_path.is_file():
        return {}

    data: dict[str, str] = {}

    try:
        for line in file_path.read_text(encoding="utf-8").splitlines():
            if "=" not in line or line.startswith("#"):
                continue

            key, value = line.split("=", maxsplit=1)
            data[key] = value.strip().strip('"').strip("'")

    except OSError:
        return {}

    return data


def check_operating_system() -> CheckResult:
    """Verifica se o sistema operacional é Linux Mint."""

    system = platform.system()

    if system != "Linux":
        return CheckResult(
            name="Sistema operacional",
            available=False,
            details=f"Sistema não suportado nesta versão: {system}",
        )

    release = read_os_release()
    distro_id = release.get("ID", "").lower()
    pretty_name = release.get(
        "PRETTY_NAME",
        "Linux desconhecido",
    )

    if distro_id == "linuxmint":
        return CheckResult(
            name="Sistema operacional",
            available=True,
            details=pretty_name,
        )

    return CheckResult(
        name="Sistema operacional",
        available=False,
        details=(
            f"{pretty_name} detectado; "
            "o alvo principal é Linux Mint."
        ),
    )


def check_command(command: str) -> CheckResult:
    """Verifica se um executável está disponível no PATH."""

    executable = shutil.which(command)

    if executable is None:
        return CheckResult(
            name=command,
            available=False,
            details="Nao encontrado no PATH",
        )

    return CheckResult(
        name=command,
        available=True,
        details=executable,
    )


def check_disk_space(path: Path = Path.home()) -> CheckResult:
    """Verifica o espaço livre na partição de um caminho."""

    try:
        usage = shutil.disk_usage(path)
    except OSError as error:
        return CheckResult(
            name="Espaço em disco",
            available=False,
            details=f"Não foi possível verificar: {error}",
        )

    free_gib = usage.free / (1024**3)

    return CheckResult(
        name="Espaço em disco",
        available=free_gib >= 2,
        details=f"{free_gib:.2f} GiB livres",
    )


def run_diagnostics() -> list[CheckResult]:
    """Executa todas as verificações iniciais."""

    return [
        check_operating_system(),
        check_command("git"),
        check_command("python3"),
        check_command("node"),
        check_command("npm"),
        check_disk_space(),
    ]
