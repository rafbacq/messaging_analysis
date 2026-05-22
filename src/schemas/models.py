from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any

@dataclass
class Message:
    source_file: str
    platform: str
    message_id: str
    sender: str
    normalized_sender: str  # 'me' or 'other'
    timestamp: Optional[datetime]
    raw_timestamp: str
    text: str
    is_sender_me: bool
    message_type: str = "text"
    has_attachment: bool = False
    reactions: List[Dict[str, str]] = field(default_factory=list)
    reply_to: Optional[str] = None
    parsing_warnings: List[str] = field(default_factory=list)
    
@dataclass
class Session:
    session_id: str
    start_time: datetime
    end_time: datetime
    messages: List[Message]
    participants: List[str]
    message_count: int
    duration_seconds: float
