#! /usr/bin/env python

from selenium import webdriver

import secret

def main():
  print('start ka bib cli')
  options = webdriver.FirefoxOptions()
  options.set_headless(True)
  driver = webdriver.Firefox(options=options)
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
  driver.quit()

if __name__ == '__main__':
  main()
