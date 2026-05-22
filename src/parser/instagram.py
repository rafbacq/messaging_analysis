import uuid
from typing import List
from datetime import datetime
from bs4 import BeautifulSoup
from src.schemas.models import Message
from src.parser.base import BaseParser
import logging

logger = logging.getLogger(__name__)

class InstagramParser(BaseParser):
    @classmethod
    def can_parse(cls, soup: BeautifulSoup) -> bool:
        # Check for typical Instagram/Meta HTML export structure
        return len(soup.find_all("div", class_=lambda c: c and "uiBoxWhite" in c)) > 0 and \
               len(soup.find_all("div", class_=lambda c: c and "_a6-p" in c)) > 0

    def parse(self) -> List[Message]:
        messages = []
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f, "lxml")
        except Exception as e:
            logger.error(f"Failed to read file {self.file_path}: {e}")
            return []

        message_divs = soup.find_all("div", class_=lambda c: c and "uiBoxWhite" in c)
        
        for div in message_divs:
            # Extract sender
            sender_h2 = div.find("h2")
            sender = sender_h2.text.strip() if sender_h2 else "Unknown"
            
            # Extract timestamp
            timestamp_div = div.find("div", class_=lambda c: c and "_a6-o" in c)
            raw_timestamp = timestamp_div.text.strip() if timestamp_div else ""
            dt = None
            if raw_timestamp:
                try:
                    # Mar 26, 2026 2:50 pm
                    dt = datetime.strptime(raw_timestamp, "%b %d, %Y %I:%M %p")
                except ValueError:
                    pass
            
            # Extract message text
            text_div = div.find("div", class_=lambda c: c and "_a6-p" in c)
            text = ""
            has_attachment = False
            if text_div:
                # Remove reaction lists if any (usually ul)
                ul = text_div.find("ul")
                if ul:
                    ul.decompose()
                    
                # Look for images/videos
                if text_div.find("img") or text_div.find("video"):
                    has_attachment = True
                    
                # Get clean text
                text = text_div.get_text(separator=" ", strip=True)
                
            norm_sender = self._normalize_sender(sender)
            
            msg = Message(
                source_file=self.file_path.split("/")[-1].split("\\")[-1],
                platform="instagram",
                message_id=str(uuid.uuid4()),
                sender=sender,
                normalized_sender=norm_sender,
                timestamp=dt,
                raw_timestamp=raw_timestamp,
                text=text,
                is_sender_me=norm_sender == "me",
                message_type="text" if text else "attachment",
                has_attachment=has_attachment
            )
            messages.append(msg)
            
        # Meta exports are usually newest first, so reverse to chronological
        messages.reverse()
        return messages
