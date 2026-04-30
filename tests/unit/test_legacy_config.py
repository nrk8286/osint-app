"""Unit tests for the legacy Config class in osint_app/utils/config.py."""

import os
from unittest.mock import patch

import pytest

from osint_app.utils.config import Config


class TestConfig:
    """Tests for the Config class."""

    def test_default_database_path(self):
        config = Config()
        assert config.database_path == "./data/osint.db"

    def test_custom_database_path_from_env(self):
        with patch.dict(os.environ, {"DATABASE_PATH": "/tmp/custom.db"}):
            config = Config()
        assert config.database_path == "/tmp/custom.db"

    def test_default_log_level_is_info(self):
        config = Config()
        assert config.log_level == "INFO"

    def test_custom_log_level_from_env(self):
        with patch.dict(os.environ, {"LOG_LEVEL": "DEBUG"}):
            config = Config()
        assert config.log_level == "DEBUG"

    def test_optional_api_keys_default_to_none(self):
        with patch.dict(os.environ, {}, clear=False):
            config = Config()
        # Without env vars set, these should be None
        if "TWITTER_API_KEY" not in os.environ:
            assert config.twitter_api_key is None
        if "REDDIT_CLIENT_ID" not in os.environ:
            assert config.reddit_client_id is None

    def test_to_dict_returns_expected_keys(self):
        config = Config()
        result = config.to_dict()
        assert "database_path" in result
        assert "log_level" in result
        assert "twitter_configured" in result
        assert "reddit_configured" in result

    def test_to_dict_twitter_configured_false_by_default(self):
        with patch.dict(os.environ, {}, clear=False):
            config = Config()
        result = config.to_dict()
        # Without API key set, twitter_configured should be False
        if not os.environ.get("TWITTER_API_KEY"):
            assert result["twitter_configured"] is False

    def test_to_dict_twitter_configured_true_when_key_set(self):
        with patch.dict(os.environ, {"TWITTER_API_KEY": "fake-key"}):
            config = Config()
        result = config.to_dict()
        assert result["twitter_configured"] is True

    def test_to_dict_reddit_configured_true_when_id_set(self):
        with patch.dict(os.environ, {"REDDIT_CLIENT_ID": "fake-id"}):
            config = Config()
        result = config.to_dict()
        assert result["reddit_configured"] is True
