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
    with CONFIG_PATH.open('w', encoding='utf-8') as f:
        json.dump(instances, f, indent=2)

def prompt_machine(existing: list[dict]) -> Machine:
    """Prompt user with robust error handling for non-integer inputs."""
    while True:
        try:
            name = input("VM name: ").strip()
            if any(vm.get("name") == name for vm in existing):
                print(f"❌ VM '{name}' already exists. Choose another.")
                continue
                
            os_input = input("OS (ubuntu/debian/centos/rocky/alpine): ").strip().lower()
            cpu_input = input("CPU cores (1-64): ").strip()
            ram_input = input("RAM GB (1-512): ").strip()

            if not cpu_input.isdigit() or not ram_input.isdigit():
                print("❌ CPU and RAM must be valid numbers.")
                continue

            return Machine(name=name, os=os_input, cpu=int(cpu_input), ram_gb=int(ram_input))

        except ValidationError as e:
            print(f"❌ Validation Error: {e.json()}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")

def run_nginx_install() -> None:
    if platform.system().lower() != "linux":
        log.info("Non-linux system detected. Skipping actual bash execution.")
        return

    script_path = Path("scripts") / "install_nginx.sh"
    if not script_path.exists():
        log.error(f"Script missing: {script_path}")
        return

    
    script_path.chmod(script_path.stat().st_mode | 0o111)

    log.info("Executing service installation...")
    try:
        
        result = subprocess.run(
            ["sudo", "bash", str(script_path)],
            capture_output=True, text=True, check=True
        )
        log.info("Success: %s", result.stdout)
    except subprocess.CalledProcessError as e:
        log.error("Script failed! Error: %s", e.stderr)
        raise RuntimeError(f"Bash script failed: {e.stderr}")

def main():
    log.info("Starting automation tool")
    instances = load_instances()

    while True:
        new_vm = prompt_machine(instances)
        instances.append(new_vm.to_dict())
        save_instances(instances)
        
        if input("Add another? (y/n): ").lower() != 'y':
            break

    try:
        run_nginx_install()
        print("✅ Process completed successfully. Check logs/provisioning.log")
    except Exception as e:
        print(f"🔥 Error during installation: {e}")

if __name__ == "__main__":
    main()

    