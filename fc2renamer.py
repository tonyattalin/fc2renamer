#!/usr/bin/python3

import argparse
import logging
import os
import re
import sys

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


logging.basicConfig(stream=sys.stdout)
logger = logging.getLogger("fc2rename")
chrome = None


def remove_punctuation_map(_unistr):
    remove_punctuation_map = dict((ord(char), None) for char in '\/*?:"<>|')
    return _unistr.translate(remove_punctuation_map)


def str2code(filename):
    # Parse the filename
    rules = [r"(\d{6,7})"]
    for rule in rules:
        m = re.search(rule, filename)
        if m:
            return m.group(1)


def code2filename(code, browser=False):
    global chrome
    if not chrome:
        options = Options()
        options.add_argument("--disable-notifications")
        if not browser:
            options.headless = True

        # chromedriver = os.path.join(os.path.dirname(os.path.realpath(__file__)), "chromedriver")
        # chromedriver = "/snap/bin/chromium.chromedriver"
        # options.add_argument("user-data-dir={}".format("chrome-fc2renamer"))
        options.add_argument("--disable-notifications") 
        prefs = {"profile.managed_default_content_settings.images": 2}
        options.add_experimental_option("prefs", prefs)

        # chrome = webdriver.Chrome(chromedriver, options=options)
        # [ ] DeprecationWarning: executable_path has been deprecated selenium python - Stack Overflow - https://stackoverflow.com/questions/64717302/deprecationwarning-executable-path-has-been-deprecated-selenium-python

        chrome = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        # chrome.set_page_load_timeout(5)
        # chrome.implicitly_wait(10) 

    url = "https://adult.contents.fc2.com/article/{}/".format(code)
    chrome.get(url)

    # wait = WebDriverWait(chrome, 10)
    # wait.until(EC.presence_of_element_located((By.XPATH, '//div[@class="items_article_headerInfo"]')))

    title = chrome.find_elements(By.XPATH, '//div[@class="items_article_headerInfo"]/h3')
    seller = chrome.find_elements(By.XPATH, '//div[@class="items_article_headerInfo"]//a[contains(@href, "https://adult.contents.fc2.com/users/")]')

    if title and seller:
        seller_str = remove_punctuation_map(seller[0].text)[:80]
        title_str = remove_punctuation_map(title[0].text)[:80]
        return os.path.join(seller_str, "FC2-{}-{}".format(code, title_str))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='filename')
    parser.add_argument('-v', dest='verbose', help='verbose', action='store_true')
    parser.add_argument('-b', dest='browser', action='store_true')

    args, unparsed = parser.parse_known_args()
    if args.verbose:
        logger.setLevel(logging.DEBUG)

    if unparsed == []:
        sys.exit()

    seen = {}
    for filename in unparsed:
        if not os.path.isfile(filename):
            continue

        # parse folder name
        dirname = os.path.dirname(filename)
        basename = os.path.basename(filename)
        code = str2code(basename)
        if code in seen:
            folder = seen[code]
        else:
            folder = code2filename(code, args.browser)
            seen[code] = folder
        logger.debug("title of %s = \"%s\"" % (basename, folder))

        if folder:
            try:
                if not os.path.exists(folder):
                    os.makedirs(folder)

                new_file = os.path.join(folder, basename)
                # Do not overwrite the old file.
                if not os.path.exists(new_file):
                    logger.debug("renaming %s to %s" % (filename, new_file))
                    os.rename(filename, new_file)
                else:
                    logger.error("%s exist" % (new_file))
            except OSError as e:
                logger.error(e)
    if chrome is not None:
        chrome.quit()
