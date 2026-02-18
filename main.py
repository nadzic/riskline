from __future__ import annotations

import logging
import time

from riskline.config import ConfigError, load_config
from riskline.engine.decision import decide_action
from riskline.engine.format_message import format_alert
from riskline.engine.score import compute_score
from riskline.indicators.trend import ma200, pct_distance_from_ma
from riskline.indicators.volatility import daily_return_volatility_pct
from riskline.notify.telegram import send_telegram_alert
from riskline.sources.binance_futures import fetch_futures_snapshot
from riskline.sources.binance_spot import fetch_daily_klines
from riskline.sources.cmc_fear_greed import fetch_fear_greed
from riskline.state import compute_oi_delta_pct, load_state, save_state, should_send_alert


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("riskline")


def run_once() -> int:
    config = load_config()
    state = load_state(config.state_file)

    fear_greed = fetch_fear_greed(api_key=config.cmc_api_key, http=config.http)
    futures = fetch_futures_snapshot(
        symbol=config.symbols.futures,
        http=config.http,
        include_liquidations_proxy=config.enable_liquidations_proxy,
    )
    closes = fetch_daily_klines(symbol=config.symbols.spot, http=config.http)

    current_price = closes[-1]
    moving_average_200 = ma200(closes)
    trend_pct = pct_distance_from_ma(current_price, moving_average_200)
    volatility_pct = daily_return_volatility_pct(closes)
    oi_delta_pct = compute_oi_delta_pct(state.prev_oi, futures["open_interest"])

    score = compute_score(
        fear_greed_value=fear_greed["value"],
        trend_pct_vs_200d=trend_pct,
        funding_rate=futures["funding_rate"],
        oi_delta_pct=oi_delta_pct,
        volatility_pct=volatility_pct,
        thresholds=config.thresholds,
    )
    decision = decide_action(score.score)

    send_allowed, reason = should_send_alert(
        state=state,
        current_regime=score.regime,
        cooldown_hours=config.alert_cooldown_hours,
        now_ts=int(time.time()),
    )

    if send_allowed:
        message = format_alert(
            fear_greed_value=fear_greed["value"],
            fear_greed_label=fear_greed["label"],
            btc_price=current_price,
            trend_pct_vs_200d=trend_pct,
            funding_rate=futures["funding_rate"],
            oi_delta_pct=oi_delta_pct,
            liquidations_proxy=futures["liquidations_proxy"],
            score=score,
            decision=decision,
            send_reason=reason,
        )
        send_telegram_alert(
            text=message,
            bot_token=config.telegram_bot_token,
            chat_id=config.telegram_chat_id,
            timeout_seconds=config.http.timeout_seconds,
            dry_run=config.dry_run,
        )
        state.last_alert_ts = int(time.time())
        state.last_regime = score.regime
        logger.info("Alert sent (%s)", reason)
    else:
        logger.info("Alert skipped (%s)", reason)

    state.prev_oi = futures["open_interest"]
    state.prev_daily_close = current_price
    save_state(config.state_file, state)
    return 0


def main() -> None:
    try:
        raise_code = run_once()
        raise SystemExit(raise_code)
    except ConfigError as exc:
        logger.error("Configuration error: %s", exc)
        raise SystemExit(2) from exc
    except Exception as exc:  # noqa: BLE001
        logger.exception("Run failed: %s", exc)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
