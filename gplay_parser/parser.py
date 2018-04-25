#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from typing import Dict


PERMISSIONS_STRINGS = {
    'en': 'Permissions',
    'ru': 'Разрешения',
}


def do_parse(id_: str, hl: str) -> Dict[str, str]:
    if hl not in PERMISSIONS_STRINGS:
        raise ValueError('Unknown language')

    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--window-size=1366x768')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--no-proxy-server')
    prefs = {'profile.managed_default_content_settings.images': 2}
    chrome_options.add_experimental_option('prefs', prefs)
    driver = webdriver.Chrome(chrome_options=chrome_options)

    try:
        driver.get(
            'https://play.google.com/store/apps/details?id={}&hl={}'.format(
                id_, hl))

        link = driver.find_element_by_xpath(
            "//div[contains(text(), '{}')]/..//a".format(
                PERMISSIONS_STRINGS[hl]))
        link.click()

        dialog = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[@role="dialog"]'))
        )

        perms = dialog.find_elements_by_xpath('//content/c-wiz/div/div')
        result = []
        for perm in perms:
            try:
                title = perm.find_element_by_xpath('div').text
                icon = perm.find_element_by_xpath('div/img').get_attribute('src')
                items = [e.text for e in perm.find_elements_by_xpath(
                    'ul/li/span')]
                result.append({'title': title, 'icon': icon, 'items': items})
            except NoSuchElementException as e:
                import traceback
                traceback.print_exc()
                pass
        return result
    finally:
        driver.quit()
