def get_ai_suggestion(error_message):
    normalized_message = (error_message or "").lower()

    if "nosuchelementexception" in normalized_message:
        return (
            "AI Insight:\n"
            "- Locator might have changed\n"
            "- Use explicit waits (WebDriverWait)\n"
            "- Prefer stable locators like ID"
        )

    if "timeoutexception" in normalized_message:
        return (
            "AI Insight:\n"
            "- Increase wait time\n"
            "- Check page load or API delays"
        )

    if "invalid" in normalized_message or "password" in normalized_message:
        return (
            "AI Insight:\n"
            "- Login failed due to invalid credentials\n"
            "- Verify test data (username/password)\n"
            "- Consider negative test scenarios"
        )

    return (
        "AI Insight:\n"
        "- Analyze logs\n"
        "- Improve synchronization strategy"
    )