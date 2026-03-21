import pytest
from src.utils.logger import get_logger, set_log_context
import logging

def test_logger_functionality():
    logger = get_logger("test_logger")
    assert logger.name == "test_logger"
    
    set_log_context(session_id="sess1", agent_name="agent1")
    logger.info("Test message with context")
    
    # Check if context filter is working (internally)
    for f in logger.handlers[0].filters if logger.handlers else []:
        if "ContextFilter" in str(type(f)):
            # Force a filter run to see if it works
            record = MagicMock()
            f.filter(record)
            assert record.session_id == "sess1"


def test_logger_levels():
    logger = get_logger("test_levels")
    logger.debug("debug")
    logger.info("info")
    logger.warning("warning")
    logger.error("error")
    # Just exercising the code for coverage
