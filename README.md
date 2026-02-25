# Infra Automation

Python-based tool for infrastructure provisioning and configuration simulation.

Features
Validation: Uses Pydantic to enforce VM specs (CPU, RAM, OS).

Persistence: Saves inventory to configs/instances.json.

Automation: Integrated Bash script with multi-distro support (apt, dnf, apk).

Logging: Centralized logs in logs/provisioning.log.

Structure
src/: Python logic (Machine class, Simulator).

scripts/: Bash automation (install_nginx.sh).

configs/: Infrastructure inventory.

logs/: Execution history.

Quick Start
Install: pip install -r requirements.txt

Run: python3 -m src.infra_simulator