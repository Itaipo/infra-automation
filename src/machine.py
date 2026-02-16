from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from .logger import get_logger

log = get_logger()

AllowedOS = Literal["ubuntu", "debian", "centos", "rocky", "alpine"]


class Machine(BaseModel):
    name: str = Field(min_length=1)
    os: AllowedOS
    cpu: int = Field(ge=1, le=64)
    ram_gb: int = Field(ge=1, le=512)

    def model_post_init(self, __context) -> None:
        # Runs after validation & object creation
        log.info(
            "Machine created: name=%s os=%s cpu=%s ram_gb=%s",
            self.name,
            self.os,
            self.cpu,
            self.ram_gb,
        )

    def to_dict(self) -> dict:
        return self.model_dump()
