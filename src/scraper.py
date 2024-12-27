from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from datetime import datetime
import uuid
import requests
import time
from pymongo import MongoClient
from config import *


class TwitterScraper:
    def __init__(self):
        self.client = MongoClient(MONGODB_URI)
        self.db = self.client['twitter_trends']
        self.collection = self.db['trends']

    def setup_driver(self):
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        service = Service()
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver

    def login_to_twitter(self, driver):
        try:
            print("Starting Twitter login process...")
            driver.get("https://twitter.com/i/flow/login")
            time.sleep(6)

            print("Entering username...")
            username_input = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="text"]'))
            )
            username_input.send_keys(TWITTER_USERNAME)
            time.sleep(1)
            username_input.send_keys(Keys.RETURN)
            time.sleep(2)

            print("Entering password...")
            password_input = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="password"]'))
            )
            password_input.send_keys(TWITTER_PASSWORD)
            time.sleep(1)
            password_input.send_keys(Keys.RETURN)
            time.sleep(5) 

            print("Login completed...")
            return True

        except Exception as e:
            print(f"Login failed: {str(e)}")
            return False

    def get_trending_topics(self):
        driver = None
        try:
            driver = self.setup_driver()

            if not self.login_to_twitter(driver):
                raise Exception("Failed to login to Twitter")

            print("Going to explore page...")
            driver.get("https://twitter.com/explore/tabs/trending")
            time.sleep(5)

            print("Looking for trends...")
            trend_elements = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, '.css-175oi2r.r-16y2uox.r-bnwqim')
                )
            )

            record = {
                "_id": str(uuid.uuid4()),
                "datetime": datetime.now(),
                "ip_address": requests.get('https://api.ipify.org').text
            }

            found_trends = 0
            for element in trend_elements:
                try:
                    trend_text = element.find_element(
                        By.CSS_SELECTOR,
                        '.css-146c3p1.r-bcqeeo.r-1ttztb7.r-qvutc0.r-37j5jr.r-a023e6.r-rjixqe.r-b88u0q.r-1bymd8e'
                    ).text.strip()

                    if trend_text and not any(x in trend_text.lower() for x in ['sign in', 'sign up', 'next', 'or', 'password']):
                        found_trends += 1
                        record[f'nameoftrend{found_trends}'] = trend_text
                        record[f'trend_category{found_trends}'] = "Trending"
                        print(f"Found trend {found_trends}: {trend_text}")

                    if found_trends >= 5:
                        break

                except Exception as e:
                    print(f"Error processing trend element: {str(e)}")
                    continue

            for i in range(found_trends + 1, 6):
                record[f'nameoftrend{i}'] = ""
                record[f'trend_category{i}'] = ""

            self.collection.insert_one(record)
            return record

        except Exception as e:
            print(f"Error: {str(e)}")
            if driver:
                driver.save_screenshot('error.png')
            raise

        finally:
            if driver:
                driver.quit()
