#! /usr/bin/env python

from selenium import webdriver

driver = webdriver.Firefox()
driver.get('https://opac.karlsruhe.de/')
assert "Stadtbibliothek" in driver.title
driver.quit()
