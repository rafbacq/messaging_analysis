import re
import unicodedata
from typing import List
from src.schemas.models import Message

class DataCleaner:
    def __init__(self, redact_pii: bool = True):
        self.redact_pii = redact_pii
        self.phone_pattern = re.compile(r'\b(?:\+?1[-.\s]?)?\(?[2-9]\d{2}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b')
        self.url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')

    def clean_messages(self, messages: List[Message]) -> List[Message]:
        cleaned = []
        seen_ids = set()
        
        for msg in messages:
            # Deduplicate
            if msg.message_id in seen_ids:
                continue
            seen_ids.add(msg.message_id)
            
            # Clean text
            text = msg.text
            if text:
                # Normalize unicode
                text = unicodedata.normalize('NFKC', text)
                
                # Strip excessive whitespace
                text = re.sub(r'\s+', ' ', text).strip()
                
                if self.redact_pii:
                    text = self.phone_pattern.sub('[PHONE]', text)
                    text = self.email_pattern.sub('[EMAIL]', text)
                    text = self.url_pattern.sub('[URL]', text)
                    
            msg.text = text
            cleaned.append(msg)
            
        # Sort chronologically, putting messages with missing timestamps at the start
        cleaned.sort(key=lambda x: x.timestamp.timestamp() if x.timestamp else 0.0)
        return cleaned
