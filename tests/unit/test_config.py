"""Unit tests for the Config singleton."""

from quiet_riot import config


def test_config_is_singleton():
    a = config.get_config()
    b = config.get_config()
    assert a is b


def test_scan_objects_roundtrip():
    cfg = config.get_config()
    cfg.clear_scan_objects()
    cfg.add_scan_object("bucket-1")
    cfg.add_scan_object("topic-1")
    assert cfg.scan_objects == ["bucket-1", "topic-1"]
    cfg.clear_scan_objects()
    assert cfg.scan_objects == []


def test_set_log_level_updates_handlers():
    cfg = config.get_config()
    cfg.set_log_level("DEBUG")
    assert cfg.log_level == "DEBUG"
    import logging

    assert logging.getLogger().level == logging.DEBUG


def test_init_populates_identity(moto_session):
    cfg = config.get_config()
    cfg.init(moto_session)
    assert cfg.account_no is not None
    assert cfg.account_arn is not None
