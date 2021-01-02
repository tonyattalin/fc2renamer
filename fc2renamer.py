#!/usr/bin/python3

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

def code2filename(code):
    options = Options()
    options.add_argument("--disable-notifications")
    options.headless = True

    chromedriver = os.path.join(os.path.dirname(os.path.realpath(__file__)), "chromedriver")
    chrome = webdriver.Chrome(chromedriver, options=options)
    url = "https://adult.contents.fc2.com/article/{}/".format(code)
    chrome.get(url)
    seller = chrome.find_elements(By.XPATH, '//div[@class="items_article_headerInfo"]//a[contains(@href, "https://adult.contents.fc2.com/users/")]')
    title = chrome.find_elements(By.XPATH, '//div[@class="items_article_headerInfo"]/h3')
    
    if title and seller:
        seller_str = seller[0].text
        title_str = remove_punctuation_map(title[0].text)[:80]
        return os.path.join(seller_str, "FC2-{}-{}".format(code, title_str))

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
        folder = code2filename(code)
        logger.debug("title of %s = \"%s\"" % (basename, folder))
            
        if folder:
            # remove ! from title
            # folder = "FC2-{}-{}".format(code, title[:80])
            # folder = os.path.join(dirname, folder)
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

