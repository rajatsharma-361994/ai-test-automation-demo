

# AI Test Automation Demo

## Overview
This project demonstrates a simple Selenium-based automation framework enhanced with AI-assisted failure analysis.

## Features
- Automated login test using Selenium (Python)
- Exception handling with intelligent suggestions
- Demonstrates AI usage in Software Development Life Cycle (SDLC)

## Test Scenario
- Navigate to login page
- Enter credentials
- Validate successful login
- Capture and analyze failures

## AI Integration
In case of test failures, the system:
- Captures error messages
- Provides intelligent suggestions for debugging
- Simulates AI-driven failure analysis

## How to Run
```bash
pip install -r requirements.txt
python test_login.py




# ---- Summary ---------
# Script executed successfully
# Result: login test passed
# Output observed:
# “Login Result: You logged into a secure area!”

# ------- Environment ----------
# Python runtime: available through the project virtual environment
# Dependencies used: Selenium and webdriver-manager from requirements.txt

# -------- What happened ------------
# The script launched a browser.
# It navigated to the login page.
# It entered the test credentials.
# It submitted the form.
# It verified the success message and printed the result.
# Status
# Overall: Pass