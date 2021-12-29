#! /usr/bin/env python3

import unittest

import bs4

t = __import__('ka-bib-info')

with open('testfiles/ausweis-ok.html') as openfile:
  ausweis_ok_html = openfile.read()

with open('testfiles/ausweis-abgelaufen.html') as openfile:
  ausweis_abgelaufen_html = openfile.read()

with open('testfiles/ausweis-gebuehren.html') as openfile:
  ausweis_gebuehren_html = openfile.read()

class TestGetUserInfo(unittest.TestCase):

  def test_ok(self):
    infotable =  bs4.BeautifulSoup(ausweis_ok_html, 'html.parser')
    userinfo = t.getuserinfo(infotable)
    expecteduserinfo = {
      'name': 'voller name',
      'expire': 'datum-noch-gültig'
    }
    self.assertEqual(userinfo, expecteduserinfo)

  def test_abgelaufen(self):
    infotable =  bs4.BeautifulSoup(ausweis_abgelaufen_html, 'html.parser')
    userinfo = t.getuserinfo(infotable)
    expecteduserinfo = {
      'name': 'voller name',
      'expire': 'datum-abgelaufen'
    }
    self.assertEqual(userinfo, expecteduserinfo)

  def test_gebuehren(self):
    infotable =  bs4.BeautifulSoup(ausweis_gebuehren_html, 'html.parser')
    userinfo = t.getuserinfo(infotable)
    expecteduserinfo = {
      'name': 'voller name',
      'fee': '3,50',
      'expire': 'datum-noch-gültig'
    }
    self.assertEqual(userinfo, expecteduserinfo)

if __name__ == '__main__':
  unittest.main()
