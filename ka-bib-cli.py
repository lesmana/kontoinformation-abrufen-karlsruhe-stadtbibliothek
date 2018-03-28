#! /usr/bin/env python

from selenium import webdriver

driver = webdriver.Firefox()
driver.get('https://karlsruhe.bibdia-mobil.de/?action=konto')
usernamefield = driver.find_element_by_id('unr')
usernamefield.clear()
usernamefield.send_keys('username')
passwordfield = driver.find_element_by_id('password')
passwordfield.clear()
passwordfield.send_keys('password')
loginbutton = driver.find_element_by_id('loginbtn')
driver.quit()
