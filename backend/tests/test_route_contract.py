"""
Contract test: OpenAPI paths must match registered FastAPI routes.

Uses app.openapi() because FastAPI 0.139 nests routers as _IncludedRouter
and does not flatten APIRoute objects onto app.routes.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from backend.main import app

SPEC_PATH = Path(__file__).resolve().parents[2] / "specs" / "openapi" / "v1.yaml"


def _normalize_path(path: str) -> str:
    return path.rstrip("/") or "/"


def _spec_operations() -> set[tuple[str, str]]:
    raw = yaml.safe_load(SPEC_PATH.read_text(encoding="utf-8"))
    ops: set[tuple[str, str]] = set()
    for path, methods in (raw.get("paths") or {}).items():
        for method, detail in methods.items():
            if method.startswith("x-") or not isinstance(detail, dict):
                continue
            if method.lower() in {"get", "post", "put", "patch", "delete", "head", "options"}:
                ops.add((_normalize_path(path), method.upper()))
    return ops


def _app_operations() -> set[tuple[str, str]]:
    """Derive operations from the live OpenAPI schema FastAPI generates."""
    schema = app.openapi()
    ops: set[tuple[str, str]] = set()
    for path, methods in (schema.get("paths") or {}).items():
        for method in methods:
            if method.lower() in {"get", "post", "put", "patch", "delete"}:
                ops.add((_normalize_path(path), method.upper()))
    return ops


def test_openapi_spec_paths_are_registered():
    spec = _spec_operations()
    registered = _app_operations()
    missing = sorted(spec - registered)
    assert not missing, (
        "OpenAPI paths missing from FastAPI app (stale server / missing include_router):\n"
        + "\n".join(f"  {m} {p}" for p, m in missing)
    )


def test_registered_api_v1_paths_are_in_spec():
    """Every /api/v1 business route should appear in the locked OpenAPI contract."""
    spec = _spec_operations()
    registered = {
        (p, m)
        for p, m in _app_operations()
        if p.startswith("/api/v1")
    }
    extra = sorted(registered - spec)
    assert not extra, (
        "FastAPI routes not documented in specs/openapi/v1.yaml:\n"
        + "\n".join(f"  {m} {p}" for p, m in extra)
    )


def test_critical_student_routes_present():
    """Regression: these were returning HTTP 404 from a zombie uvicorn process."""
    registered = _app_operations()
    required = {
        ("/api/v1/tasks", "GET"),
        ("/api/v1/checkins/history", "GET"),
        ("/api/v1/profiles/me/stats", "GET"),
        ("/api/v1/checkins/current/mood", "PATCH"),
    }
    missing = sorted(required - registered)
    assert not missing, f"Critical routes missing: {missing}"
