#! /usr/bin/env python

from selenium import webdriver

import secret

def initdriver():
  options = webdriver.FirefoxOptions()
  options.set_headless(True)
  driver = webdriver.Firefox(options=options)
  return driver

def dotheclicks(driver):
  driver.get('https://karlsruhe.bibdia-mobil.de/?action=konto')
  usernamefield = driver.find_element_by_id('unr')
  usernamefield.clear()
  usernamefield.send_keys(secret.username)
  passwordfield = driver.find_element_by_id('password')
  passwordfield.clear()
  passwordfield.send_keys(secret.password)
  loginbutton = driver.find_element_by_id('loginbtn')
  loginbutton.click()
  assert 'Leserkonto' in driver.title

def quitdriver(driver):
  driver.quit()

def main():
  print('start ka bib cli')
  driver = initdriver()
  dotheclicks(driver)
  quitdriver(driver)

if __name__ == '__main__':
  main()
