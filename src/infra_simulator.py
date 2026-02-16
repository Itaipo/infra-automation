from __future__ import annotations

import json
from pathlib import Path

CONFIG_PATH = Path("configs") / "instances.json"
ALLOWED_OS = {"ubuntu", "debian", "centos", "rocky", "alpine"}


def load_instances() -> list[dict]:
    if not CONFIG_PATH.exists():
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


def validate_name(name: str, existing: list[dict]) -> str:
    name = name.strip()
    if not name:
        raise ValueError("VM name cannot be empty.")
    if any(vm.get("name") == name for vm in existing):
        raise ValueError("A VM with this name already exists.")
    return name


def validate_os(os_name: str) -> str:
    os_name = os_name.strip().lower()
    if os_name not in ALLOWED_OS:
        allowed = ", ".join(sorted(ALLOWED_OS))
        raise ValueError(f"Invalid OS. Allowed: {allowed}")
    return os_name


def validate_int(raw: str, field: str, min_value: int, max_value: int) -> int:
    raw = raw.strip()
    if not raw.isdigit():
        raise ValueError(f"{field} must be a whole number.")
    value = int(raw)
    if value < min_value or value > max_value:
        raise ValueError(f"{field} must be between {min_value} and {max_value}.")
    return value


def prompt_machine(existing: list[dict]) -> dict:
    while True:
        try:
            name = validate_name(input("VM name: "), existing)
            os_name = validate_os(input(f"OS ({', '.join(sorted(ALLOWED_OS))}): "))
            cpu = validate_int(input("CPU cores (1-64): "), "CPU cores", 1, 64)
            ram = validate_int(input("RAM GB (1-512): "), "RAM GB", 1, 512)
            return {"name": name, "os": os_name, "cpu": cpu, "ram_gb": ram}
        except ValueError as e:
            print(f"❌ {e}")
            print("Try again.\n")


def main() -> None:
    print("=== Infra Automation (Mock Provisioning) ===")

    try:
        instances = load_instances()
    except RuntimeError as e:
        print(f"❌ {e}")
        return

    while True:
        vm = prompt_machine(instances)
        instances.append(vm)
        save_instances(instances)

        again = input("Add another VM? (y/n): ").strip().lower()
        if again != "y":
            break

    print(f"✅ Saved {len(instances)} VM(s) to {CONFIG_PATH}")


if __name__ == "__main__":
    main()
