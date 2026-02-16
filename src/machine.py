from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .logger import get_logger

log = get_logger()


@dataclass(frozen=True)
class Machine:
    name: str
    os: str
    cpu: int
    ram_gb: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "os": self.os,
            "cpu": self.cpu,
            "ram_gb": self.ram_gb,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Machine":

        return cls(
            name=str(data["name"]),
            os=str(data["os"]),
            cpu=int(data["cpu"]),
            ram_gb=int(data["ram_gb"]),
        )

    def log_creation(self) -> None:
        log.info(
            "Machine created: name=%s os=%s cpu=%s ram_gb=%s",
            self.name,
            self.os,
            self.cpu,
            self.ram_gb,
        )
