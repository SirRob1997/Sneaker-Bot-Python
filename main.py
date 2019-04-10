import os
import sys
import time
import six
import pause
import argparse
import logging.config
from selenium import webdriver
from dateutil import parser as date_parser
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC

logging.config.dictConfig({
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s [PID %(process)d] [Thread %(thread)d] [%(levelname)s] [%(name)s] %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "default",
            "stream": "ext://sys.stdout"
        }
    },
    "root": {
        "level": "INFO",
        "handlers": [
            "console"
        ]
    }
})

NIKE_URL = "https://www.nike.com/de/de_de"
LOGGER = logging.getLogger()

def run(driver, username, password, url, shoe_size, login_time = None, release_time=None, page_load_timeout=None, screenshot_path=None, html_path=None, select_payment=False, purchase=False, num_retries=None):
    driver.maximize_window()
    driver.set_page_load_timeout(page_load_timeout)

    #Starting login process
    if login_time:
        LOGGER.info("Waiting until login time: " + login_time)
        pause.until(date_parser.parse(login_time))

    try:
        login(driver=driver, username=username, password=password)
    except Exception as e:
        LOGGER.exception("Failed to login: " + str(e))
        six.reraise(Exception, e, sys.exc_info()[2])

    if release_time:
        LOGGER.info("Waiting until release time: " + release_time)
        pause.until(date_parser.parse(release_time))

    #Starting page request process
    num_retries_attempted = 0
    try:
        LOGGER.info("Requesting page: " + url)
        driver.get(url)
    except TimeoutException:
        LOGGER.info("Page load timed out but continuing anyway")

    try:
        select_shoe_size(driver=driver, shoe_size=shoe_size)
    except Exception as e:
        # If we fail to select shoe size, try to buy anyway
        LOGGER.exception("Failed to select shoe size: " + str(e))

def login(driver, username, password):
    try:
        LOGGER.info("Requesting page: " + NIKE_URL)
        driver.get(NIKE_URL)
    except TimeoutException:
        LOGGER.info("Page load timed out but continuing anyway")

    #We swith to the MEN tab here to simulate user interaction, because the "login" button doesn't always show
    LOGGER.info("Waiting for Men button to become clickable")
    wait_until_clickable(driver=driver, xpath="//a[@class='nav-brand fs16-nav-sm prl5-sm pt6-sm pb6-sm nav-uppercase d-sm-ib va-sm-m']", duration=10)

    LOGGER.info("Clicking men button")
    driver.find_element_by_xpath("//a[@class='nav-brand fs16-nav-sm prl5-sm pt6-sm pb6-sm nav-uppercase d-sm-ib va-sm-m']").click()

    LOGGER.info("Waiting for men label to be visible")
    wait_until_visible(driver=driver, xpath="//span[@class='nike-cq-subtitle-line-1 nike-cq-title-line nike-cq-line1 nsg-text--dark-grey nike-cq-font60px nike-cq-nospacing nsg-font-family--platform']")

    LOGGER.info("Waiting for login button to become clickable")
    wait_until_clickable(driver=driver, xpath="//button[@class='nav-btn p0-sm prl3-sm pt2-sm pb2-sm fs12-nav-sm d-sm-b nav-color-grey hover-color-black']", duration=10)

    LOGGER.info("Clicking login button")
    driver.find_element_by_xpath("//button[@class='nav-btn p0-sm prl3-sm pt2-sm pb2-sm fs12-nav-sm d-sm-b nav-color-grey hover-color-black']").click()

    LOGGER.info("Waiting for login fields to become visible")
    wait_until_visible(driver=driver, xpath="//input[@name='emailAddress']")

    LOGGER.info("Entering username and password")
    email_input = driver.find_element_by_xpath("//input[@name='emailAddress']")
    email_input.clear()
    email_input.send_keys(username)
    password_input = driver.find_element_by_xpath("//input[@name='password']")
    password_input.clear()
    password_input.send_keys(password)

    LOGGER.info("Logging in")
    driver.find_element_by_xpath("//input[@value='ANMELDEN']").click()
    wait_until_visible(driver=driver, xpath="//span[text()='Mein Konto']")

    LOGGER.info("Successfully logged in")

def wait_until_clickable(driver, xpath=None, class_name=None, duration=10000, frequency=0.01):
    if xpath:
        WebDriverWait(driver, duration, frequency).until(EC.element_to_be_clickable((By.XPATH, xpath)))
    elif class_name:
        WebDriverWait(driver, duration, frequency).until(EC.element_to_be_clickable((By.CLASS_NAME, class_name)))


def wait_until_visible(driver, xpath=None, class_name=None, duration=10000, frequency=0.01):
    if xpath:
        WebDriverWait(driver, duration, frequency).until(EC.visibility_of_element_located((By.XPATH, xpath)))
    elif class_name:
        WebDriverWait(driver, duration, frequency).until(EC.visibility_of_element_located((By.CLASS_NAME, class_name)))

def select_shoe_size(driver, shoe_size):
    LOGGER.info("Waiting for size dropdown button to become clickable")
    wait_until_clickable(driver, xpath="//select[@id='skuAndSize']", duration=10)

    LOGGER.info("Clicking size dropdown button")
    driver.find_element_by_id("skuAndSize").click()

    LOGGER.info("Waiting for size dropdown to appear")
    wait_until_visible(driver, xpath="//option[text()='{}']".format("EU 40"), duration=10)

    LOGGER.info("Selecting size from dropdown")
    driver.find_element_by_id("skuAndSize").find_element_by_xpath("//option[text()='{}']".format(shoe_size)).click()

    LOGGER.info("Selected size "+ shoe_size +" from dropdown")

def main():
    parser = argparse.ArgumentParser(description='Processing input values for run')
    parser.add_argument("--username", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--url", required=True)
    parser.add_argument("--shoe_size", required=True)
    parser.add_argument("--login_time", default=None)
    parser.add_argument("--release_time", default=None)
    parser.add_argument("--screenshot_path", default=None)
    parser.add_argument("--html_path", default=None)
    parser.add_argument("--page_load_timeout", type=int, default=2)
    parser.add_argument("--driver_type", default="chrome", choices=("firefox", "chrome"))
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--select_payment", action="store_true")
    parser.add_argument("--purchase", action="store_true")
    parser.add_argument("--num_retries", type=int, default=1)
    args = parser.parse_args()
    driver = None

    if args.driver_type == "chrome":
        options = webdriver.ChromeOptions()
        if args.headless:
            options.add_argument("headless")
        if sys.platform == "win32":
            executable_path = "./bin/win_chromedriver.exe"
        else:
            raise Exception("Unsupported operating system. Please add your own Selenium driver for it.")
        driver = webdriver.Chrome(executable_path=executable_path, options=options)
    else:
        raise Exception("Unsupported browser. Please use chrome for now")

    run(driver=driver, username=args.username, password=args.password, url=args.url, shoe_size=args.shoe_size,
        login_time=args.login_time, release_time=args.release_time, page_load_timeout=args.page_load_timeout,
        screenshot_path=args.screenshot_path, html_path=args.html_path, select_payment=args.select_payment,
        purchase=args.purchase, num_retries=args.num_retries)


main()
