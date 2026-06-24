# AGENTS.md

## Project overview
This repository is a small Selenium-based demo for automated login testing with simple AI-style failure suggestions. The main entry point is [test_login.py](test_login.py), and the helper logic lives in [ai_helper.py](ai_helper.py). For project context and usage, see [README.md](README.md).

## Working conventions
- Keep changes small and focused. This project is a lightweight demo rather than a large test framework.
- Preserve the current simple script style unless a task explicitly asks for a larger refactor.
- Prefer minimal dependency changes. Any new package should be justified by the task.

## Run and validation
Use the following flow when validating changes:

```bash
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
python3 test_login.py
```

## Important implementation notes
- [test_login.py](test_login.py) opens a Chrome browser, navigates to the login page, submits credentials, and prints the result.
- [ai_helper.py](ai_helper.py) provides heuristic suggestions for common Selenium failures such as missing elements or timeouts.
- Browser and driver issues are common in local runs; if execution fails, verify that Chrome is available and that the Selenium environment is set up correctly.

## Expectations for agents
- When modifying the automation flow, keep the behavior understandable and easy to follow for a demo audience.
- When adding or changing failure handling, preserve the existing AI suggestion pattern rather than introducing a new framework.
- If you add new functionality, prefer clear, self-contained code over abstractions that are unnecessary for this small project.
