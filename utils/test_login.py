import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from utils.ai_helper import get_ai_suggestion


LOGIN_URL = "https://the-internet.herokuapp.com/login"
USERNAME = "tomsmith"
PASSWORD = "SuperSecretPassword!"   


@pytest.fixture
def driver():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.maximize_window()
    yield driver
    driver.quit()


def test_login_success(driver):
    driver.get(LOGIN_URL)

    try:
        wait = WebDriverWait(driver, 10)

        username = wait.until(EC.presence_of_element_located((By.ID, "username")))
        password = wait.until(EC.presence_of_element_located((By.ID, "password")))
        login_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))

        username.send_keys(USERNAME)
        password.send_keys(PASSWORD)
        login_btn.click()

        success_msg = wait.until(EC.visibility_of_element_located((By.ID, "flash"))).text

        assert "You logged into a secure area!" in success_msg

    except Exception as e:
        screenshot_path = f"screenshots/failure_{int(time.time())}.png"
        driver.save_screenshot(screenshot_path)

        
        suggestion = get_ai_suggestion(str(e))

        pytest.fail(
            f"Test failed.\n"
            f"Screenshot: {screenshot_path}\n"
            f"AI Suggestion:\n{suggestion}"
        )