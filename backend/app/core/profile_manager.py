"""Recording profile manager (per-session recorder configuration)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional
import logging

import yaml

from app.core.config import config

logger = logging.getLogger(__name__)


def _deep_merge(base: Any, override: Any) -> Any:
    """Deep-merge two YAML-ish structures (dicts/lists/scalars)."""
    if isinstance(base, dict) and isinstance(override, dict):
        merged = dict(base)
        for key, override_value in override.items():
            if key in merged:
                merged[key] = _deep_merge(merged[key], override_value)
            else:
                merged[key] = override_value
        return merged
    return override if override is not None else base


def _read_yaml(path: Path) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        content = yaml.safe_load(f)
    return content if isinstance(content, dict) else {}


@dataclass(frozen=True)
class ProfileInfo:
    name: str
    description: str
    source: str


class RecordingProfileManager:
    """
    Manage selectable recording profiles.

    Profiles live under `backend/config/profiles/*.yaml` and are merged onto the
    default recorder config (`backend/config/recorder.yaml` loaded by ConfigManager).

    A profile file may include:
      - `profile.name` / `profile.description` (metadata)
      - `recorder: ...` (partial or full overrides)
    """

    def __init__(self) -> None:
        backend_dir = Path(__file__).resolve().parent.parent.parent
        self._profiles_dir = backend_dir / "config" / "profiles"
        self._profiles_dir.mkdir(parents=True, exist_ok=True)

    def list_profiles(self) -> List[ProfileInfo]:
        profiles: List[ProfileInfo] = []

        profile_files = sorted(
            list(self._profiles_dir.glob("*.yaml")) + list(self._profiles_dir.glob("*.yml"))
        )
        for path in profile_files:
            try:
                data = _read_yaml(path)
                meta = data.get("profile", {}) if isinstance(data.get("profile"), dict) else {}
                # Profile name is the filename stem (so it can be reliably loaded later).
                name = path.stem
                description = str(meta.get("description") or "自定义配置文件")
                profiles.append(
                    ProfileInfo(
                        name=name,
                        description=description,
                        source=f"backend/config/profiles/{path.name}",
                    )
                )
            except Exception as e:
                logger.warning(f"Failed to read profile {path}: {e}")

        # Deduplicate by name (prefer first occurrence)
        seen = set()
        unique: List[ProfileInfo] = []
        for p in profiles:
            if p.name in seen:
                continue
            seen.add(p.name)
            unique.append(p)
        return unique

    def load_recorder_config(self, profile_name: Optional[str]) -> Dict[str, Any]:
        """
        Load the effective recorder config (full `recorder` config file dict).

        Returns a dict shaped like the `recorder.yaml` file (top-level `recorder:` key).
        """
        base = config.get("recorder") or {}
        if not profile_name:
            return base

        path = self._profiles_dir / f"{profile_name}.yaml"
        if not path.exists():
            yml_path = self._profiles_dir / f"{profile_name}.yml"
            if yml_path.exists():
                path = yml_path

        if not path.exists():
            logger.warning(f"Profile not found: {profile_name}, falling back to default")
            return base

        override = _read_yaml(path)
        # Only merge known config keys; ignore metadata
        if "profile" in override:
            override = dict(override)
            override.pop("profile", None)

        return _deep_merge(base, override) if isinstance(base, dict) else override


profile_manager = RecordingProfileManager()
