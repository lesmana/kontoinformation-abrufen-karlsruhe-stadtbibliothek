#!/usr/bin/env python

import sys
import requests
import bs4
import pprint
import time

baseurl = 'https://karlsruhe.bibdia-mobil.de'

try:
  user = sys.argv[1]
except:
  print('need argument: name of user')
  sys.exit(1)

#print(user)
secretfilename = user if user.endswith('.secret') else user + '.secret'
#print(secretfilename)

try:
  with open(secretfilename) as secretfile:
    username, password = secretfile.read().splitlines()
except:
  print('error trying to read credentials from file: ' + secretfilename)
  sys.exit(1)

#print(username)
#print(password)

session = requests.Session()

formdata = {}
formdata['action'] = 'konto'
formdata['unr'] = username
formdata['password'] = password
url = baseurl + '/?action=konto'
response = session.post(url, data=formdata)
assert(response.status_code == 200)

soup = bs4.BeautifulSoup(response.content, 'html.parser')



[tableelem] = soup.find_all('table', attrs={'id': 'ausl-table'})
#print(tableelem.prettify())
trelems = tableelem.find_all('tr')[2:]
if len(trelems) < 1:
  print('seems to be nothing')
  sys.exit()
for trelem in trelems:
  print(trelem.prettify())
