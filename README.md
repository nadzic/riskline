# Riskline v1

Riskline is a scheduled multi-agent signal engine for BTC risk regime monitoring. It combines sentiment (Fear & Greed), trend, and futures positioning signals, then sends Telegram alerts only on meaningful change.

## What v1 does

- Pulls **CoinMarketCap Fear & Greed**
- Pulls **Binance spot daily closes** for MA200 trend filter
- Pulls **Binance futures funding + open interest**
- Computes a deterministic **0-100 risk score**
- Maps score to **BUY / HOLD / REDUCE** with practical guidance
- Sends Telegram alerts only on:
  - regime flip, or
  - cooldown expiry (default 6h)

## Agent-style module design

- `CollectorAgent`:
  - `riskline/sources/cmc_fear_greed.py`
  - `riskline/sources/binance_spot.py`
  - `riskline/sources/binance_futures.py`
- `ScoringAgent`:
  - `riskline/indicators/trend.py`
  - `riskline/indicators/volatility.py`
  - `riskline/engine/score.py`
  - `riskline/engine/decision.py`
- `StateGuardAgent`:
  - `riskline/state.py`
- `NotifierAgent`:
  - `riskline/engine/format_message.py`
  - `riskline/notify/telegram.py`
- `OrchestratorAgent`:
  - `main.py`

## Requirements

- Python 3.9+
- A CoinMarketCap API key
- A Telegram bot token and target chat ID

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Set secrets in `.env`:

- `CMC_API_KEY`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`
- `RISKLINE_DRY_RUN=false` (set `true` to print message instead of sending)

Never commit `.env`.

## Config

Main runtime config is in `config.yaml`:

- polling and cooldown
- scoring thresholds
- symbols
- HTTP timeout/retry/backoff
- optional liquidation proxy toggle
- state file path

## Run locally

```bash
.venv/bin/python main.py
```

Expected behavior:

- fetches all signals once
- computes score/regime/action
- checks anti-spam state
- sends alert if needed (or prints in dry-run)
- writes `.riskline_state.json`

## Testing

Run all tests:

```bash
.venv/bin/python -m pytest -q
```

Test suite includes:

- indicator math
- score/decision boundaries
- anti-spam state logic
- message formatting
- source parsing with mocked HTTP
- retry/failure behavior
- orchestrator end-to-end with mocks

## Deploy on Hetzner

### Option A: cron

Use `scripts/cron_example.txt` as baseline.

### Option B: systemd timer (recommended)

1. Copy `systemd/riskline.service` to `/etc/systemd/system/riskline.service`
2. Copy `systemd/riskline.timer` to `/etc/systemd/system/riskline.timer`
3. Adjust paths and user/group
4. Enable + start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now riskline.timer
sudo systemctl status riskline.timer
```

## Troubleshooting

- **429/rate limits**: increase poll interval and/or retry backoff.
- **No Telegram messages**: verify bot token, chat ID, and bot permissions in target chat.
- **No alert on run**: cooldown/regime gate may be blocking duplicates by design.
- **Config error on startup**: required env variable is missing.

## Security notes

- Keep `CMC_API_KEY` and Telegram token private.
- Keep bot in private chat/group when possible.
- Do not commit secrets or state files with sensitive metadata.

## Disclaimer

Riskline is a decision-support tool and not financial advice.
