# scraper.py
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from database_setup import Unsorted
from utils import session_scope
import config
import time

def setup_driver():
    chrome_options = Options()
    # Uncomment the next line to run Chrome in headless mode
    # chrome_options.add_argument("--headless")
    service = Service(config.CHROME_DRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver


def login_to_linkedin(driver, email, password):
    driver.get("https://www.linkedin.com/login")
    email_elem = driver.find_element(By.ID, "username")
    email_elem.send_keys(email)
    password_elem = driver.find_element(By.ID, "password")
    password_elem.send_keys(password)
    password_elem.send_keys(Keys.RETURN)

    try:
        # Wait for the URL to change to the feed page
        WebDriverWait(driver, 10).until(
            EC.url_contains("https://www.linkedin.com/feed"))
        print("Login successful.")
        return True
    except TimeoutException:
        print("Login failed.")
        return False

def fetch_notifications(driver):
    with session_scope() as session:
        driver.get("https://www.linkedin.com/notifications/?filter=all")
        last_height = driver.execute_script(
            "return document.body.scrollHeight")
        while True:
            driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # Sleep to allow page to load
            new_height = driver.execute_script(
                "return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        try:
            # Wait for the notifications to be present
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, "//div[@data-finite-scroll-hotkey-item]"))
            )
            notifications = driver.find_elements(
                By.XPATH, "//div[@data-finite-scroll-hotkey-item]")

            for notification in notifications:
                try:
                    title = notification.find_element(By.XPATH, ".//strong").text if notification.find_elements(
                        By.XPATH, ".//strong") else "General Notification"
                    content_elements = notification.find_elements(
                        By.XPATH, ".//span")
                    content = " ".join(
                        [elem.text for elem in content_elements if elem.text.strip() != ""])
                    new_notification = Unsorted(title=title, content=content)
                    session.add(new_notification)
                except Exception as e:
                    print(f"Error processing notification: {e}")
                    continue

            session.commit()
            print(
                f"Notifications fetched and saved successfully. Total: {len(notifications)}")
        except TimeoutException:
            print("Failed to load notifications.")

def main():
    driver = setup_driver()
    email = input("Enter your LinkedIn email: ")
    password = input("Enter your LinkedIn password: ")
    if login_to_linkedin(driver, email, password):
        fetch_notifications(driver)
    else:
        print("Login failed. Exiting...")
    driver.quit()


if __name__ == "__main__":
    main()
