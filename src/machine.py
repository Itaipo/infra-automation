from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, Field, model_validator
from .logger import get_logger

log = get_logger()

AllowedOS = Literal["ubuntu", "debian", "centos", "rocky", "alpine"]

class Machine(BaseModel):
    name: str = Field(min_length=1, description="Machine name")
    os: AllowedOS
    cpu: int = Field(ge=1, le=64)
    ram_gb: int = Field(ge=1, le=512)

    @model_validator(mode='after')
    def log_creation(self) -> Machine:
        """Runs automatically after Pydantic finishes validation."""
        log.info(
            "Machine validated: name=%s os=%s cpu=%d ram_gb=%d",
            self.name, self.os, self.cpu, self.ram_gb
        )
        return self

    def to_dict(self) -> dict:
        return self.model_dump()