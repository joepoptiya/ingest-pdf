from __future__ import annotations
import os
import threading
from functools import lru_cache
from pathlib import Path

try:
    import tomllib  # Py ≥3.11
except ModuleNotFoundError:
    import tomli as tomllib  # pip install tomli (Py ≤3.10)

_LOCK = threading.RLock()


def _project_root() -> Path:
    # 1) APP_CONFIG_DIR takes precedence (absolute or relative to CWD)
    if (env := os.getenv("APP_CONFIG_DIR")):
        return Path(env).resolve()

    # 2) If running from project root, prefer CWD
    cwd = Path.cwd()
    if (cwd / "config.toml").exists():
        return cwd

    # 3) Walk up from this file to find a folder that contains config.toml
    here = Path(__file__).resolve()
    for parent in [here.parent, *here.parents]:
        if (parent / "config.toml").exists():
            return parent

    # 4) Fallback to this file’s folder (works if you later move the TOML)
    return here.parent


def _read_toml(p: Path) -> dict:
    return tomllib.loads(p.read_text()) if p.exists() else {}


def _coerce(s: str):
    t = s.lower()
    if t in {"true", "false"}:
        return t == "true"
    try:
        if "." in s:
            return float(s)
        return int(s)
    except ValueError:
        return s


def _apply_env_overrides(cfg: dict) -> dict:
    # APP__APP__PORT=9090 -> cfg["app"]["port"]=9090
    prefix = os.getenv("APP_PREFIX", "APP__")
    for k, v in os.environ.items():
        if not k.startswith(prefix):
            continue
        path = k[len(prefix):].split("__")
        cur = cfg
        for key in path[:-1]:
            cur = cur.setdefault(key.lower(), {})
        cur[path[-1].lower()] = _coerce(v)
    return cfg


def _merge(a: dict, b: dict) -> dict:
    for k, v in b.items():
        if k in a and isinstance(a[k], dict) and isinstance(v, dict):
            _merge(a[k], v)
        else:
            a[k] = v
    return a


def _load() -> dict:
    root = _project_root()
    base = _read_toml(root / "config.toml")
    env = os.getenv("APP_ENV")
    if env:
        _merge(base, _read_toml(root / f"config.{env}.toml"))
    _apply_env_overrides(base)
    return base


@lru_cache(maxsize=1)
def settings() -> dict:
    with _LOCK:
        return _load()


def reload_settings() -> dict:
    with _LOCK:
        settings.cache_clear()  # type: ignore[attr-defined]
        return settings()
