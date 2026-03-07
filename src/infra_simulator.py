import json
import platform
import subprocess
from pathlib import Path
from enum import Enum
from pydantic import ValidationError
from .logger import get_logger
from .machine import Machine

CONFIG_PATH = Path("configs") / "instances.json"
log = get_logger()


class OSName(str, Enum):
    UBUNTU = "ubuntu"
    DEBIAN = "debian"
    CENTOS = "centos"
    ROCKY = "rocky"
    ALPINE = "alpine"
    WINDOWS = "windows"


def load_instances() -> list[dict]:
    if not CONFIG_PATH.exists():
        return []
    try:
        return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, Exception) as e:
        log.error("Failed to load instances: %s", e)
        return []


def save_instances(instances: list[dict]) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CONFIG_PATH.open("w", encoding="utf-8") as f:
        json.dump(instances, f, indent=2)


def prompt_machine(existing: list[dict]) -> Machine:
    allowed_os = {os.value for os in OSName}

    while True:
        name = input("VM name: ").strip()

        if not name:
            print("❌ VM name cannot be empty.")
            continue

        if any(vm.get("name") == name for vm in existing):
            print(f"❌ VM '{name}' already exists. Choose another.")
            continue

        break

    while True:
        os_input = input("OS (ubuntu/debian/centos/rocky/alpine/windows): ").strip().lower()

        if os_input not in allowed_os:
            print("❌ Invalid OS. Choose one of: ubuntu, debian, centos, rocky, alpine, windows")
            continue

        break

    while True:
        cpu_input = input("CPU cores (1-64): ").strip()
        if not cpu_input.isdigit():
            print("❌ CPU must be a valid number.")
            continue

        cpu_value = int(cpu_input)
        if not (1 <= cpu_value <= 64):
            print("❌ CPU must be between 1 and 64.")
            continue

        break

    while True:
        ram_input = input("RAM GB (1-512): ").strip()
        if not ram_input.isdigit():
            print("❌ RAM must be a valid number.")
            continue

        ram_value = int(ram_input)
        if not (1 <= ram_value <= 512):
            print("❌ RAM must be between 1 and 512.")
            continue

        break

    try:
        return Machine(
            name=name,
            os=os_input,
            cpu=cpu_value,
            ram_gb=ram_value,
        )
    except ValidationError as e:
        print(f"❌ Validation Error: {e}")
        raise