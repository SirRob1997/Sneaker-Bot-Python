import os
import sys
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


NIKE_URL = "https://www.nike.com/de/de_de/"
LOGGER = logging.getLogger()

#def run(driver, username, password, url, shoe_size, login_time = None, release_time=None, page_load_timeout=None, screenshot_path=None, html_path=None, select_payment=False, purchase=False, num_retries=None):


def main():
    parser = argparse.ArgumentParser(description='Processing input values for run')
    parser.add_argument("--username", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--url", required=True)
    parser.add_argument("--shoe_size", required=True)
    parser.add_argument("--login_time", default=None)
    parser.add_argument("--release_time", default=None)
    #parser.add_argument("--screenshot_path", default=None)
    #parser.add_argument("--html_path", default=None)
    parser.add_argument("--page_load_timeout", type=int, default=2)
    parser.add_argument("--driver_type", default="chrome", choices=("firefox", "chrome"))
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--select_payment", action="store_true")
    parser.add_argument("--purchase", action="store_true")
    parser.add_argument("--num_retries", type=int, default=1)
    args = parser.parse_args()
    print(args.username)
    driver = None

main()
