"""Configuration loader for environment-driven settings.

This module centralizes runtime configuration so tests and deployment can
override behavior with environment variables. Keep settings small and
typed for easier reasoning in other modules.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os


@dataclass(frozen=True)
class Settings:
    """Typed runtime settings used across the application.

    - `data_dir`: path to the local `data/` folder
    - `openai_api_key`: optional, when present enables LLM synthesis
    - `openai_model`: model id used for LLM calls
    - `top_k`, `max_sources`, `similarity_threshold`, `temperature`: tuning knobs
    """
    data_dir: Path
    openai_api_key: str | None
    openai_model: str
    top_k: int
    max_sources: int
    similarity_threshold: float
    temperature: float
    app_title: str = "Altius Fund VIII Copilot"


def load_settings() -> Settings:
    """Read environment variables and return a `Settings` instance.

    Tests should call this function after temporarily setting env vars to
    validate alternative configurations.
    """
    root = Path(__file__).resolve().parents[1]
    data_dir = Path(os.getenv("DATA_DIR", str(root / "data"))).expanduser().resolve()
    return Settings(
        data_dir=data_dir,
        openai_api_key=os.getenv("OPENAI_API_KEY") or None,
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
        top_k=int(os.getenv("RETRIEVAL_TOP_K", "8")),
        max_sources=int(os.getenv("MAX_CITATIONS", "4")),
        similarity_threshold=float(os.getenv("SIMILARITY_THRESHOLD", "0.08")),
        temperature=float(os.getenv("LLM_TEMPERATURE", "0.2")),
    )