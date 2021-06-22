#!/usr/bin/env python

import sys
import requests
import bs4
import pprint
import time
import datetime

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

tables = soup.find_all('table', attrs={'class': 'tab21'})

infotable = tables[0]

if len(tables) == 1:
  borrowtable = None
elif len(tables) == 2:
  borrowtable = tables[1]
else:
  print('unexpected number of tables')
  print('maybe layout of website changed')
  for table in tables:
    print(table.prettify())
  sys.exit(1)

infotds = infotable.find_all('td')

name = ''.join(infotds[1].stripped_strings)
print('name', name)

fee = ''.join(infotds[2].stripped_strings)
if fee != '':
  print('gebühren', fee)

validity = ''.join(infotds[5].stripped_strings)
_, validity = validity.split()
delta = datetime.datetime.strptime(validity, '%d.%m.%Y') - datetime.datetime.today()
#print(validity)
#print(delta.days)

if delta.days < 0:
  print(f'ausweis abgelaufen ({validity})')
  print(f'in tagen: {delta.days}')
elif delta.days < 14:
  print(f'ausweis läuft bald ab ({validity})')
  print(f'in tagen: {delta.days}')
