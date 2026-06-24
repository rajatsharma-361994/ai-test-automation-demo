from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from ai_helper import get_ai_suggestion

def test_login():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get("https://the-internet.herokuapp.com/login")

    try:
        driver.find_element(By.ID, "username").send_keys("tomsmith")
        driver.find_element(By.ID, "password").send_keys("SuperSecretPassword!")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        success_msg = driver.find_element(By.ID, "flash").text
        print("Login Result:", success_msg)

    except Exception as e:
        print("Error occurred:", str(e))

        # AI-assisted suggestion
        suggestion = get_ai_suggestion(str(e))
        print("AI Suggestion:", suggestion)

    time.sleep(3)
    driver.quit()

test_login()