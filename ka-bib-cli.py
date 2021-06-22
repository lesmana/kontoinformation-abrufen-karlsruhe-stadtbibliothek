#!/usr/bin/env python

import sys
import requests
import bs4
import pprint
import time

baseurl = 'https://opac.karlsruhe.de'

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
formdata['LANG'] = 'de'
formdata['FUNC'] = 'medk'
formdata['BENUTZER'] = username
formdata['PASSWORD'] = password
url = baseurl + '/opax/user.C'
response = session.post(url, data=formdata)
assert(response.status_code == 200)

soup = bs4.BeautifulSoup(response.content, 'html.parser')

tableelems = soup.find_all('table', attrs={'class': 'tab21'})
for tableelem in tableelems:
  print(tableelem.prettify())
