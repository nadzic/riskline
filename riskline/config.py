from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv


class ConfigError(ValueError):
    """Raised when required configuration is missing or invalid."""


@dataclass(frozen=True)
class Thresholds:
    fear_greed_buy: int
    fear_greed_sell: int
    funding_short_crowded: float
    funding_long_crowded: float
    trend_risk_off_pct: float
    oi_deleveraging_pct: float
    oi_leverage_build_pct: float
    high_volatility_pct: float


@dataclass(frozen=True)
class Symbols:
    futures: str
    spot: str


@dataclass(frozen=True)
class HttpConfig:
    timeout_seconds: int
    max_retries: int
    backoff_seconds: float


@dataclass(frozen=True)
class AppConfig:
    poll_interval_minutes: int
    alert_cooldown_hours: int
    state_file: str
    thresholds: Thresholds
    symbols: Symbols
    http: HttpConfig
    cmc_api_key: str
    telegram_bot_token: str
    telegram_chat_id: str
    dry_run: bool
    enable_liquidations_proxy: bool


def _to_bool(value: Any, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    normalized = str(value).strip().lower()
    return normalized in {"1", "true", "yes", "on"}


def _required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise ConfigError(f"Missing required environment variable: {name}")
    return value


def load_config(path: str = "config.yaml", env_path: str = ".env") -> AppConfig:
    load_dotenv(env_path)
    raw = yaml.safe_load(Path(path).read_text()) or {}

    thresholds_raw = raw.get("thresholds", {})
    symbols_raw = raw.get("symbols", {})
    http_raw = raw.get("http", {})

    thresholds = Thresholds(
        fear_greed_buy=int(thresholds_raw.get("fear_greed_buy", 20)),
        fear_greed_sell=int(thresholds_raw.get("fear_greed_sell", 70)),
        funding_short_crowded=float(thresholds_raw.get("funding_short_crowded", -0.0001)),
        funding_long_crowded=float(thresholds_raw.get("funding_long_crowded", 0.0001)),
        trend_risk_off_pct=float(thresholds_raw.get("trend_risk_off_pct", -1.0)),
        oi_deleveraging_pct=float(thresholds_raw.get("oi_deleveraging_pct", -2.0)),
        oi_leverage_build_pct=float(thresholds_raw.get("oi_leverage_build_pct", 2.0)),
        high_volatility_pct=float(thresholds_raw.get("high_volatility_pct", 3.0)),
    )
    symbols = Symbols(
        futures=str(symbols_raw.get("futures", "BTCUSDT")),
        spot=str(symbols_raw.get("spot", "BTCUSDT")),
    )
    http = HttpConfig(
        timeout_seconds=int(http_raw.get("timeout_seconds", 12)),
        max_retries=int(http_raw.get("max_retries", 3)),
        backoff_seconds=float(http_raw.get("backoff_seconds", 1.0)),
    )

    return AppConfig(
        poll_interval_minutes=int(raw.get("poll_interval_minutes", 30)),
        alert_cooldown_hours=int(raw.get("alert_cooldown_hours", 6)),
        state_file=str(raw.get("state_file", ".riskline_state.json")),
        thresholds=thresholds,
        symbols=symbols,
        http=http,
        cmc_api_key=_required_env("CMC_API_KEY"),
        telegram_bot_token=_required_env("TELEGRAM_BOT_TOKEN"),
        telegram_chat_id=_required_env("TELEGRAM_CHAT_ID"),
        dry_run=_to_bool(os.getenv("RISKLINE_DRY_RUN"), default=False),
        enable_liquidations_proxy=_to_bool(raw.get("enable_liquidations_proxy", False), default=False),
    )
