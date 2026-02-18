import pytest

from riskline.notify.telegram import NotificationError, send_telegram_alert


def test_send_telegram_alert_dry_run_does_not_call_http(monkeypatch, capsys) -> None:
    def _fail_post(*args, **kwargs):  # pragma: no cover
        raise AssertionError("requests.post should not be called in dry_run")

    monkeypatch.setattr("riskline.notify.telegram.requests.post", _fail_post)

    send_telegram_alert(
        text="hello",
        bot_token="bot",
        chat_id="chat",
        timeout_seconds=1,
        dry_run=True,
    )

    output = capsys.readouterr().out
    assert "[DRY RUN] Telegram message:" in output
    assert "hello" in output


def test_send_telegram_alert_success(monkeypatch) -> None:
    called = {"count": 0}

    class _Resp:
        @staticmethod
        def raise_for_status() -> None:
            return None

        @staticmethod
        def json() -> dict:
            return {"ok": True}

    def _fake_post(*args, **kwargs):
        called["count"] += 1
        return _Resp()

    monkeypatch.setattr("riskline.notify.telegram.requests.post", _fake_post)

    send_telegram_alert(
        text="hello",
        bot_token="bot",
        chat_id="chat",
        timeout_seconds=1,
        dry_run=False,
    )
    assert called["count"] == 1


def test_send_telegram_alert_raises_when_api_payload_not_ok(monkeypatch) -> None:
    class _Resp:
        @staticmethod
        def raise_for_status() -> None:
            return None

        @staticmethod
        def json() -> dict:
            return {"ok": False, "description": "bad request"}

    monkeypatch.setattr("riskline.notify.telegram.requests.post", lambda *args, **kwargs: _Resp())

    with pytest.raises(NotificationError, match="Telegram API returned error payload"):
        send_telegram_alert(
            text="hello",
            bot_token="bot",
            chat_id="chat",
            timeout_seconds=1,
            dry_run=False,
        )
