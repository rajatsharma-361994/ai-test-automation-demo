def get_ai_suggestion(error_message):
    if "NoSuchElementException" in error_message:
        return "AI Insight: Locator might have changed. Consider updating selectors or adding waits."
    elif "TimeoutException" in error_message:
        return "AI Insight: Increase wait time or check page load performance."
    else:
        return "AI Insight: Analyze logs and improve synchronization."