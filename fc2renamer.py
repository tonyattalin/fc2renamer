#!env python3

import argparse
import logging
import os
import re
import sys

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

logging.basicConfig(stream=sys.stdout)
logger = logging.getLogger("fc2rename")


def str2code(filename):
    # Parse the filename
    rules = [r"(\d{6,7})"]
    for rule in rules:
        m = re.search(rule, filename)
        if m:
            return m.group(1)

def code2title(code):
    options = Options()
    options.add_argument("--disable-notifications")
    options.headless = True

    chrome = webdriver.Chrome(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'chromedriver'), options=options)
    url = "https://adult.contents.fc2.com/article/{}/".format(code)
    chrome.get(url)
    title = chrome.find_elements(By.XPATH, '//div[@class="items_article_headerInfo"]/h3')
    if title:
        return title[0].text

    # email = chrome.find_element_by_id("email")
    # password = chrome.find_element_by_id("pass")
    # email.send_keys('example@gmail.com')
    # password.send_keys('*****')
    # password.submit()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='filename')
    parser.add_argument('-v', dest='verbose', help='verbose', action='store_true')

    args, unparsed = parser.parse_known_args()
    if args.verbose:
        logger.setLevel(logging.DEBUG)

    if unparsed == []:
        sys.exit()
    for filename in unparsed:
        if not os.path.isfile(filename):
            continue

        # parse folder namek
        dirname = os.path.dirname(filename)
        basename = os.path.basename(filename)
        code = str2code(basename)
        title = code2title(code)
        logger.debug("title of %s = \"%s\"" % (basename, title))
            
        if title:
            folder = "FC2-{}-{}".format(code, title[:80])
            folder = os.path.join(dirname, folder)
            if not os.path.exists(folder):
                os.makedirs(folder)

            new_file = os.path.join(folder, basename)
            # Do not overwrite the old file.
            if not os.path.exists(new_file):
                logger.debug("renaming %s to %s" % (filename, new_file))
                os.rename(filename, new_file)
            else:
                logger.error("%s exist" % (new_file))
