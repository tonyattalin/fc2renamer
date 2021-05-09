#!/usr/bin/python3

import argparse
import logging
import os
import re
import sys

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

logging.basicConfig(stream=sys.stdout)
logger = logging.getLogger("fc2rename")
chrome = None


def remove_punctuation_map(_unistr):
    remove_punctuation_map = dict((ord(char), None) for char in '\/*?:"<>|')
    return _unistr.translate(remove_punctuation_map)


def str2code(filename):
    # Parse the filename
    rules = [
        r"(\w{3,5}-\d{3,5})",
    ]
    for rule in rules:
        m = re.search(rule, filename)
        if m:
            return m.group(1)


def code2filename(code, browser=False, no_actor=True):
    global chrome
    if not chrome:
        options = Options()
        options.add_argument("--disable-notifications")
        if not browser:
            options.headless = True

        chromedriver = os.path.join(os.path.dirname(os.path.realpath(__file__)), "chromedriver")
        # options.add_argument("user-data-dir={}".format("chrome-fc2renamer"))
        options.add_argument("--disable-notifications") 
        prefs = {"profile.managed_default_content_settings.images": 2}
        options.add_experimental_option("prefs", prefs)

        chrome = webdriver.Chrome(chromedriver, options=options)

    url = "https://www.javbus.com/{}".format(code)
    chrome.get(url)

    actor = chrome.find_elements(By.XPATH, '//a[contains(@href, "https://www.javbus.com/star/")]/img')
    if "404" in chrome.title:
        return ''
    elif not no_actor and len(actor) == 1:
        title = remove_punctuation_map(chrome.title[:-9][:80])
        return os.path.join(actor[0].get_attribute('title'), title)
    else:
        title = remove_punctuation_map(chrome.title[:-9][:80])
        return title


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='filename')
    parser.add_argument('-v', dest='verbose', help='verbose', action='store_true')
    parser.add_argument('-b', dest='browser', help='open browser session', action='store_true')
    parser.add_argument('--no_actor', dest='no_actor', help='do not create folder for actor', action='store_true')

    args, unparsed = parser.parse_known_args()
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    # DEBUG
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
        logger.debug("found %s from %s" % (code,filename))
        if code in seen:
            folder = seen[code]
        else:
            folder = code2filename(code, args.browser, args.no_actor)
            seen[code] = folder
        logger.debug("title of %s = \"%s\"" % (basename, folder))

        if folder:
            folder = os.path.join(dirname, folder)
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
