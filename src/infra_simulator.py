from __future__ import annotations

import json
from pathlib import Path

from pydantic import ValidationError

from .logger import get_logger
from .machine import Machine

CONFIG_PATH = Path("configs") / "instances.json"
log = get_logger()


def load_instances() -> list[dict]:
    if not CONFIG_PATH.exists():
        log.info("No instances.json found. Starting with empty inventory.")
        return []

    try:
        data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise RuntimeError("configs/instances.json is corrupted (invalid JSON).") from e

    if not isinstance(data, list):
        raise RuntimeError("configs/instances.json must contain a JSON list.")

    return data


def save_instances(instances: list[dict]) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(instances, indent=2), encoding="utf-8")
    log.info("Saved %d instance(s) to %s", len(instances), CONFIG_PATH)


def validate_name(name: str, existing: list[dict]) -> str:
    name = name.strip()
    if not name:
        raise ValueError("VM name cannot be empty.")
    if any(vm.get("name") == name for vm in existing):
        raise ValueError("A VM with this name already exists.")
    return name


def input_int(prompt: str, field: str) -> int:
    raw = input(prompt).strip()
    if not raw.isdigit():
        raise ValueError(f"{field} must be a whole number.")
    return int(raw)


def prompt_machine(existing: list[dict]) -> Machine:
    while True:
        try:
            name = validate_name(input("VM name: "), existing)
            os_name = input("OS (ubuntu/debian/centos/rocky/alpine): ").strip().lower()
            cpu = input_int("CPU cores (1-64): ", "CPU cores")
            ram = input_int("RAM GB (1-512): ", "RAM GB")

            return Machine(name=name, os=os_name, cpu=cpu, ram_gb=ram)

        except ValidationError as e:
            log.warning("Validation error while creating Machine (fields: %s)", list(e.errors()))
            print(f"❌ Validation error:\n{e}\nTry again.\n")


        except ValueError as e:
            log.warning("Invalid user input: %s", e)
            print(f"❌ {e}\nTry again.\n")


def main() -> None:
    log.info("Provisioning run started")
    print("=== Infra Automation (Mock Provisioning) ===")

    try:
        instances = load_instances()
    except RuntimeError as e:
        log.exception("Failed to load instances")
        print(f"❌ {e}")
        return

    while True:
        machine = prompt_machine(instances)
        instances.append(machine.to_dict())
        save_instances(instances)

        again = input("Add another VM? (y/n): ").strip().lower()
        if again != "y":
            break

    log.info("Provisioning run finished successfully")
    print(f"✅ Saved {len(instances)} VM(s) to {CONFIG_PATH}")


if __name__ == "__main__":
    main()
