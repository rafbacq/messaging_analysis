import uuid
from typing import List
from datetime import datetime
from bs4 import BeautifulSoup, Tag
from src.schemas.models import Message
from src.parser.base import BaseParser
import logging

logger = logging.getLogger(__name__)

class IMessageParser(BaseParser):
    @classmethod
    def can_parse(cls, soup: BeautifulSoup) -> bool:
        # Check for typical iMessage HTML structure
        return len(soup.find_all("div", class_="sent iMessage")) > 0 or \
               len(soup.find_all("div", class_="received")) > 0 or \
               len(soup.find_all("span", class_="bubble")) > 0

    def parse(self) -> List[Message]:
        messages = []
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f, "lxml")
        except Exception as e:
            logger.error(f"Failed to read file {self.file_path}: {e}")
            return []

        message_divs = soup.find_all("div", class_="message")
        
        for div in message_divs:
            # Determine if sent or received
            is_sent = div.find("div", class_=lambda c: c and "sent" in c) is not None
            is_received = div.find("div", class_=lambda c: c and "received" in c) is not None
            
            if not is_sent and not is_received:
                continue

            inner_div = div.find("div", class_=lambda c: c and ("sent" in c or "received" in c))
            
            # Extract sender
            sender_span = inner_div.find("span", class_="sender")
            sender = sender_span.text.strip() if sender_span else ("Me" if is_sent else "Other")
            
            # Extract timestamp
            timestamp_span = inner_div.find("span", class_="timestamp")
            raw_timestamp = ""
            dt = None
            if timestamp_span:
                a_tag = timestamp_span.find("a")
                if a_tag:
                    raw_timestamp = a_tag.text.strip()
                else:
                    raw_timestamp = timestamp_span.text.strip().split("(")[0].strip()
                
                try:
                    # Apr 04, 2024 10:27:00 PM
                    dt = datetime.strptime(raw_timestamp, "%b %d, %Y %I:%M:%S %p")
                except ValueError:
                    try:
                        # Apr 05, 2024  2:31:10 AM
                        dt = datetime.strptime(raw_timestamp.replace("  ", " "), "%b %d, %Y %I:%M:%S %p")
                    except ValueError:
                        pass
            
            # Extract message text
            message_parts = inner_div.find_all("div", class_="message_part")
            text_blocks = []
            has_attachment = False
            for part in message_parts:
                bubble = part.find("span", class_="bubble")
                if bubble:
                    text_blocks.append(bubble.get_text(separator=" ", strip=True))
                attachment = part.find("div", class_="attachment")
                if attachment:
                    has_attachment = True

            text = " ".join(text_blocks)
            
            # Message ID
            msg_id = None
            if timestamp_span and timestamp_span.find("a"):
                href = timestamp_span.find("a").get("href", "")
                if "message-guid=" in href:
                    msg_id = href.split("message-guid=")[1]
            if not msg_id:
                msg_id = str(uuid.uuid4())
                
            norm_sender = self._normalize_sender(sender)
            
            msg = Message(
                source_file=self.file_path.split("/")[-1].split("\\")[-1],
                platform="imessage",
                message_id=msg_id,
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
            
        return messages
