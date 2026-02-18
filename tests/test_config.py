import textwrap

import pytest

from riskline.config import ConfigError, load_config


def _write_yaml(path, content: str) -> None:
    path.write_text(textwrap.dedent(content).strip() + "\n")


def test_load_config_happy_path_and_booleans(tmp_path, monkeypatch) -> None:
    monkeypatch.delenv("CMC_API_KEY", raising=False)
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    monkeypatch.delenv("TELEGRAM_CHAT_ID", raising=False)
    monkeypatch.delenv("RISKLINE_DRY_RUN", raising=False)

    config_path = tmp_path / "config.yaml"
    env_path = tmp_path / ".env"

    _write_yaml(
        config_path,
        """
        poll_interval_minutes: 15
        alert_cooldown_hours: 4
        enable_liquidations_proxy: "yes"
        symbols:
          futures: ETHUSDT
          spot: ETHUSDT
        http:
          timeout_seconds: 9
          max_retries: 2
          backoff_seconds: 0.5
        state_file: custom-state.json
        """,
    )
    env_path.write_text(
        "\n".join(
            [
                "CMC_API_KEY=test-cmc",
                "TELEGRAM_BOT_TOKEN=test-bot",
                "TELEGRAM_CHAT_ID=test-chat",
                "RISKLINE_DRY_RUN=1",
            ]
        )
        + "\n"
    )

    cfg = load_config(path=str(config_path), env_path=str(env_path))

    assert cfg.poll_interval_minutes == 15
    assert cfg.alert_cooldown_hours == 4
    assert cfg.symbols.futures == "ETHUSDT"
    assert cfg.http.timeout_seconds == 9
    assert cfg.state_file == "custom-state.json"
    assert cfg.dry_run is True
    assert cfg.enable_liquidations_proxy is True


def test_load_config_uses_defaults_when_yaml_sparse(tmp_path, monkeypatch) -> None:
    monkeypatch.delenv("CMC_API_KEY", raising=False)
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    monkeypatch.delenv("TELEGRAM_CHAT_ID", raising=False)
    monkeypatch.delenv("RISKLINE_DRY_RUN", raising=False)

    config_path = tmp_path / "config.yaml"
    env_path = tmp_path / ".env"

    _write_yaml(config_path, "{}")
    env_path.write_text(
        "\n".join(
            [
                "CMC_API_KEY=abc",
                "TELEGRAM_BOT_TOKEN=def",
                "TELEGRAM_CHAT_ID=ghi",
            ]
        )
        + "\n"
    )

    cfg = load_config(path=str(config_path), env_path=str(env_path))

    assert cfg.poll_interval_minutes == 30
    assert cfg.alert_cooldown_hours == 6
    assert cfg.symbols.futures == "BTCUSDT"
    assert cfg.symbols.spot == "BTCUSDT"
    assert cfg.http.max_retries == 3
    assert cfg.enable_liquidations_proxy is False


def test_load_config_raises_on_missing_required_env(tmp_path, monkeypatch) -> None:
    monkeypatch.delenv("CMC_API_KEY", raising=False)
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    monkeypatch.delenv("TELEGRAM_CHAT_ID", raising=False)
    monkeypatch.delenv("RISKLINE_DRY_RUN", raising=False)

    config_path = tmp_path / "config.yaml"
    env_path = tmp_path / ".env"

    _write_yaml(config_path, "{}")
    env_path.write_text(
        "\n".join(
            [
                "CMC_API_KEY=abc",
                "TELEGRAM_BOT_TOKEN=def",
            ]
        )
        + "\n"
    )

    with pytest.raises(ConfigError, match="TELEGRAM_CHAT_ID"):
        load_config(path=str(config_path), env_path=str(env_path))
