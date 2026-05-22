from abc import ABC, abstractmethod
from typing import List, Optional
from bs4 import BeautifulSoup
from src.schemas.models import Message
import logging

logger = logging.getLogger(__name__)

class BaseParser(ABC):
    def __init__(self, file_path: str, my_name: str = "Me"):
        self.file_path = file_path
        self.my_name = my_name

    @abstractmethod
    def parse(self) -> List[Message]:
        """Parses the file and returns a list of Message objects."""
        pass

    @classmethod
    @abstractmethod
    def can_parse(cls, soup: BeautifulSoup) -> bool:
        """Determines if this parser can handle the provided HTML structure."""
        pass
        
    def _normalize_sender(self, sender: str) -> str:
        if not sender:
            return "unknown"
        sender_lower = sender.lower().strip()
        my_name_lower = self.my_name.lower().strip()
        if sender_lower == my_name_lower or "me" in sender_lower or "tristan" in sender_lower:
            return "me"
        return "other"
