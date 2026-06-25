# AI Test Automation Demo

## Overview

This project demonstrates a **Selenium-based test automation framework** built using **Python and Pytest**, enhanced with **AI-assisted failure analysis**.

It showcases how intelligent insights can be integrated into automation workflows to improve debugging efficiency and overall test reliability within the Software Development Life Cycle (SDLC).

---

## Features

* UI automation using Selenium WebDriver
* Pytest-based test framework
* Explicit waits for stable and reliable execution
* AI-assisted failure analysis (simulated)
* Unit testing for AI helper logic
* HTML test reporting

---

## Test Scenario

* Automates login functionality
* Validates successful login
* Handles failure scenarios (e.g., invalid credentials)
* Provides AI-based suggestions on test failure

---


## Future Enhancements
- GitHub Actions CI/CD pipeline
- Page Object Model implementation
- Self-healing locator strategy


## Run Instructions

```bash
python3 -m pip install -r requirements.txt
pytest
```

## AI-enabled test runs

To enable AI failure analysis during pytest execution, run:

```bash
pytest --ai-analyze
```

When a test fails, the framework will capture the failure, send it to the analyzer, and print a concise AI summary in the test output. Reports are written to the ai-analysis directory.

