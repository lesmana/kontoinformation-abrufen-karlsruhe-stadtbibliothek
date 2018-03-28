#! /usr/bin/env python

from selenium import webdriver

driver = webdriver.Firefox()
driver.get('https://karlsruhe.bibdia-mobil.de/')
welcomeelement = driver.find_element_by_id('welcome')
assert 'Stadtbibliothek Karlsruhe' in welcomeelement.text
driver.quit()
