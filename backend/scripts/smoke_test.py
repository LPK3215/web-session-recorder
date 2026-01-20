"""Lightweight smoke test for backend configuration and APIs.

This is intentionally small and self-contained (no pytest required).
"""

from __future__ import annotations

import sys
from pathlib import Path


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(repo_root / "backend"))

    try:
        from fastapi.testclient import TestClient  # type: ignore
        from app.main import app  # type: ignore
    except Exception as exc:
        print(f"[FAIL] import error: {exc}")
        return 2

    client = TestClient(app)

    def check_get(path: str, params: dict | None = None) -> None:
        r = client.get(path, params=params)
        if r.status_code != 200:
            raise RuntimeError(f"GET {path} -> {r.status_code}: {r.text[:200]}")

    try:
        check_get("/health")
        check_get("/api/config")
        check_get("/api/profiles")
        check_get("/api/config/presets")
        check_get("/api/config/presets", params={"profile": "default"})
        print("[OK] backend smoke test passed")
        return 0
    except Exception as exc:
        print(f"[FAIL] backend smoke test failed: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
