# Riskline v1

Lightweight, cron-friendly crypto risk signal engine that combines sentiment and futures context, then sends concise Telegram alerts only when market regime changes.

## Why this exists

Most crypto signal bots either spam too often or rely on a single indicator. Riskline v1 is built to be practical:
- combine a few high-signal indicators
- score market regime
- send alerts only on meaningful state changes

## v1 Signal Stack

- **CoinMarketCap Fear & Greed** (`/v3/fear-and-greed/latest`)
- **Binance Futures funding** (`/fapi/v1/premiumIndex`)
- **Binance Futures open interest** (`/fapi/v1/openInterest`)
- **BTC trend filter** (200D MA from daily klines)
- **Optional liquidation proxy** (`/fapi/v1/forceOrders` or volatility/volume proxy)

## Decision model (v1)

Riskline computes a `0-100` score and maps it to an action label:
- `BUY` (with DCA tranche guidance)
- `HOLD`
- `REDUCE`

Default thresholds (tunable):
- F&G BUY-bias when `<= 20`; SELL-bias when `>= 70`
- Risk-off when BTC is meaningfully below 200D MA
- Crowded shorts when funding < `-0.01% / 8h`
- Crowded longs when funding > `+0.01% / 8h`

## Anti-spam behavior

Alerts are sent only when:
1. market regime flips, or
2. cooldown expires (default 6h)

A tiny local state file is used to track previous regime and deltas (e.g., OI change).

## Project structure

```
riskline/
  README.md
  requirements.txt
  .env.example
  config.yaml
  main.py
  riskline/
    __init__.py
    config.py
    state.py
    sources/
      __init__.py
      cmc_fear_greed.py
      binance_spot.py
      binance_futures.py
    indicators/
      __init__.py
      trend.py
      volatility.py
    engine/
      __init__.py
      score.py
      decision.py
      format_message.py
    notify/
      __init__.py
      telegram.py
  scripts/
    cron_example.txt
  systemd/
    riskline.service
    riskline.timer
```

## Quick start

1. Clone and enter repo
2. Create venv and install deps
3. Copy `.env.example` to `.env` and set secrets
4. Run once

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python main.py
```

## Environment variables

- `CMC_API_KEY`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

Never commit `.env` or secrets.

## Deployment (Hetzner-friendly)

Recommended run model is cron/systemd timer every 15-60 minutes depending on API quota.

- cron template: `scripts/cron_example.txt`
- systemd examples: `systemd/riskline.service`, `systemd/riskline.timer`

## v1 done criteria

- Alert triggers on confirmed fear/greed + futures regime
- No duplicate alerts every run (state-based)
- One command to run locally and on server

## Roadmap

- **v1.1**: persist daily history, add chart, multi-asset support
- **v2**: on-chain inputs, portfolio sizing, dashboard

## Disclaimer

Riskline is an educational decision-support tool, not financial advice.
