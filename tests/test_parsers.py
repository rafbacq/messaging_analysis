import pytest
from bs4 import BeautifulSoup
from src.parser.imessage import IMessageParser
from src.parser.instagram import InstagramParser

def test_imessage_can_parse():
    html = """<html><body><div class="message"><div class="sent iMessage"></div></div></body></html>"""
    soup = BeautifulSoup(html, "lxml")
    assert IMessageParser.can_parse(soup) == True
    assert InstagramParser.can_parse(soup) == False

def test_instagram_can_parse():
    html = """<html><body><div class="pam _3-95 _2ph- _a6-g uiBoxWhite noborder"><div class="_3-95 _a6-p"></div></div></body></html>"""
    soup = BeautifulSoup(html, "lxml")
    assert InstagramParser.can_parse(soup) == True
    assert IMessageParser.can_parse(soup) == False
