#! /usr/bin/env python3

import unittest

import bs4

t = __import__('ka-bib-info')

class TestGetUserInfo(unittest.TestCase):

  def test_ok(self):
    with open('testfiles/ausweis-ok.html') as openfile:
      htmlstr = openfile.read()
    infotable =  bs4.BeautifulSoup(htmlstr, 'html.parser')
    userinfo = t.getuserinfo(infotable)
    expecteduserinfo = {
      'name': 'voller name',
      'expire': 'datum-noch-gültig'
    }
    self.assertEqual(userinfo, expecteduserinfo)

  def test_abgelaufen(self):
    with open('testfiles/ausweis-abgelaufen.html') as openfile:
      htmlstr = openfile.read()
    infotable =  bs4.BeautifulSoup(htmlstr, 'html.parser')
    userinfo = t.getuserinfo(infotable)
    expecteduserinfo = {
      'name': 'voller name',
      'expire': 'datum-abgelaufen'
    }
    self.assertEqual(userinfo, expecteduserinfo)

  def test_gebuehren(self):
    with open('testfiles/ausweis-gebuehren.html') as openfile:
      htmlstr = openfile.read()
    infotable =  bs4.BeautifulSoup(htmlstr, 'html.parser')
    userinfo = t.getuserinfo(infotable)
    expecteduserinfo = {
      'name': 'voller name',
      'fee': '3,50',
      'expire': 'datum-noch-gültig'
    }
    self.assertEqual(userinfo, expecteduserinfo)

if __name__ == '__main__':
  unittest.main()
