from typing import List, Dict, Any
import pandas as pd
from src.schemas.models import Message, Session

class StatsExtractor:
    def __init__(self):
        pass

    def compute_overall_stats(self, messages: List[Message]) -> Dict[str, Any]:
        if not messages:
            return {}
            
        df = pd.DataFrame([m.__dict__ for m in messages if m.timestamp])
        if df.empty:
            return {}
            
        return {
            "total_messages": len(messages),
            "first_message_date": df['timestamp'].min(),
            "last_message_date": df['timestamp'].max(),
            "active_days": df['timestamp'].dt.date.nunique(),
            "total_words": sum(len(str(m.text).split()) for m in messages if m.text),
            "total_characters": sum(len(str(m.text)) for m in messages if m.text),
        }

    def compute_person_stats(self, messages: List[Message]) -> Dict[str, Dict[str, Any]]:
        stats = {}
        for msg in messages:
            sender = msg.normalized_sender
            if sender not in stats:
                stats[sender] = {
                    "message_count": 0,
                    "word_count": 0,
                    "char_count": 0,
                    "attachments": 0
                }
            
            stats[sender]["message_count"] += 1
            if msg.text:
                words = len(str(msg.text).split())
                chars = len(str(msg.text))
                stats[sender]["word_count"] += words
                stats[sender]["char_count"] += chars
            if msg.has_attachment:
                stats[sender]["attachments"] += 1
                
        # Calculate averages
        for sender in stats:
            count = stats[sender]["message_count"]
            stats[sender]["avg_message_length"] = stats[sender]["word_count"] / count if count > 0 else 0
            
        return stats

    def compute_session_stats(self, sessions: List[Session]) -> Dict[str, Any]:
        if not sessions:
            return {}
            
        return {
            "total_sessions": len(sessions),
            "avg_session_duration": sum(s.duration_seconds for s in sessions) / len(sessions),
            "avg_messages_per_session": sum(s.message_count for s in sessions) / len(sessions),
        }
