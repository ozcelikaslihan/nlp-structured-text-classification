"""Output contract shared by prompting, constrained decoding, and validation."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

CATEGORIES = (
    "dunya",
    "ekonomi",
    "kultur",
    "saglik",
    "siyaset",
    "spor",
    "teknoloji",
)
ENTITY_TYPES = ("PERSON", "ORGANIZATION", "LOCATION")


class Entities(BaseModel):
    """Typed surface-form entity lists copied from the input text."""

    model_config = ConfigDict(extra="forbid")

    persons: list[str] = Field(max_length=20)
    organizations: list[str] = Field(max_length=20)
    locations: list[str] = Field(max_length=20)


class ModelOutput(BaseModel):
    """Strict model response used in both experimental settings."""

    model_config = ConfigDict(extra="forbid")

    category: Literal[
        "dunya", "ekonomi", "kultur", "saglik", "siyaset", "spor", "teknoloji"
    ]
    entities: Entities


OUTPUT_JSON_SCHEMA = ModelOutput.model_json_schema()

