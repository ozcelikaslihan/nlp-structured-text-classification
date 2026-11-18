"""Thin local-only Ollama client wrapper with recorded generation metadata."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Literal

from ollama import Client

from .prompts import build_messages
from .schema import OUTPUT_JSON_SCHEMA

Setting = Literal["prompt_only", "schema_constrained"]


@dataclass(frozen=True)
class Generation:
    raw_output: str
    elapsed_seconds: float
    prompt_eval_count: int | None
    eval_count: int | None
    prompt_eval_duration: int | None
    eval_duration: int | None
    done_reason: str | None


def generate(
    *,
    client: Client,
    text: str,
    setting: Setting,
    config: dict[str, Any],
) -> Generation:
    """Call the local Ollama server; only constrained mode receives format."""

    options = {
        "seed": config["seed"],
        "temperature": config["temperature"],
        "top_k": config["top_k"],
        "top_p": config["top_p"],
        "num_ctx": config["num_ctx"],
        "num_predict": config["num_predict"],
    }
    kwargs: dict[str, Any] = {
        "model": config["model"],
        "messages": build_messages(text),
        "options": options,
        "stream": False,
        "keep_alive": config.get("keep_alive", "10m"),
    }
    if setting == "schema_constrained":
        kwargs["format"] = OUTPUT_JSON_SCHEMA
    # Critical experimental control: prompt_only must not contain a format key.
    started = time.perf_counter()
    response = client.chat(**kwargs)
    elapsed = time.perf_counter() - started
    return Generation(
        raw_output=response.message.content or "",
        elapsed_seconds=elapsed,
        prompt_eval_count=response.prompt_eval_count,
        eval_count=response.eval_count,
        prompt_eval_duration=response.prompt_eval_duration,
        eval_duration=response.eval_duration,
        done_reason=response.done_reason,
    )

