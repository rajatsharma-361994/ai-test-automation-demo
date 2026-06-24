from utils.ai_helper import get_ai_suggestion


def test_get_ai_suggestion_handles_no_such_element():
    suggestion = get_ai_suggestion("NoSuchElementException")
    assert "Locator might have changed" in suggestion


def test_get_ai_suggestion_handles_timeout():
    suggestion = get_ai_suggestion("TimeoutException")
    assert "Increase wait time" in suggestion


def test_get_ai_suggestion_handles_unknown_error():
    suggestion = get_ai_suggestion("RandomError")
    assert "Analyze logs" in suggestion