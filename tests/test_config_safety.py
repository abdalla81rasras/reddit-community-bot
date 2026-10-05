import config

def test_safe_defaults():
    assert config.DRY_RUN is True
    assert config.POST_ENABLED is False
    assert config.MAX_REPLIES_PER_HOUR <= 5
    assert config.MAX_REPLIES_PER_USER_PER_DAY <= 1
    assert config.MIN_REPLY_INTERVAL_SECONDS >= 60
    assert config.MAX_COMMENTS_PER_CYCLE <= 20
