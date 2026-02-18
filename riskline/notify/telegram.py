from __future__ import annotations

import requests


class NotificationError(RuntimeError):
    """Raised when Telegram notification fails."""


def send_telegram_alert(
    *,
    text: str,
    bot_token: str,
    chat_id: str,
    timeout_seconds: int = 12,
    dry_run: bool = False,
) -> None:
    if dry_run:
        print("[DRY RUN] Telegram message:")
        print(text)
        return

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    response = requests.post(
        url,
        json={"chat_id": chat_id, "text": text},
        timeout=timeout_seconds,
    )
    response.raise_for_status()
    data = response.json()
    if not data.get("ok"):
        raise NotificationError(f"Telegram API returned error payload: {data}")
