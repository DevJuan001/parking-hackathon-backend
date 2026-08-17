import logging
from app.utils.logger import get_logger


def test_get_logger_returns_logger_instance():
    assert isinstance(get_logger("test.utils.logger"), logging.Logger)


def test_get_logger_same_name_returns_same_instance():
    a = get_logger("test.utils.singleton")
    b = get_logger("test.utils.singleton")

    assert a is b


def test_get_logger_is_idempotent():
    logger = get_logger("test.utils.idempotent")

    handlers_before = len(logger.handlers)

    get_logger("test.utils.idempotent")

    assert len(logger.handlers) == handlers_before


def test_get_logger_sets_debug_level_on_first_call():
    logger = get_logger("test.utils.level")

    assert logger.level == logging.DEBUG
