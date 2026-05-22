from bs4 import BeautifulSoup
from src.parser.base import BaseParser
from src.parser.imessage import IMessageParser
from src.parser.instagram import InstagramParser
import logging

logger = logging.getLogger(__name__)

def get_parser(file_path: str, my_name: str = "Me") -> BaseParser:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            # Read first few KB to determine type
            head = f.read(8192)
            soup = BeautifulSoup(head, "lxml")
            
            if IMessageParser.can_parse(soup):
                return IMessageParser(file_path, my_name)
            elif InstagramParser.can_parse(soup):
                return InstagramParser(file_path, my_name)
            else:
                raise ValueError(f"No suitable parser found for {file_path}")
    except Exception as e:
        logger.error(f"Error determining parser for {file_path}: {e}")
        raise
