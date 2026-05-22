import uuid
from typing import List
from datetime import timedelta
from src.schemas.models import Message, Session

class Sessionizer:
    def __init__(self, session_gap_minutes: float = 120.0):
        self.session_gap = timedelta(minutes=session_gap_minutes)

    def group_into_sessions(self, messages: List[Message]) -> List[Session]:
        sessions = []
        if not messages:
            return sessions

        current_session_msgs = []
        
        # Skip messages without timestamps for sessionizing, or put them in a "misc" session
        valid_messages = [m for m in messages if m.timestamp is not None]
        
        if not valid_messages:
            return sessions

        current_session_msgs.append(valid_messages[0])
        
        for msg in valid_messages[1:]:
            prev_msg = current_session_msgs[-1]
            time_diff = msg.timestamp - prev_msg.timestamp
            
            if time_diff > self.session_gap:
                sessions.append(self._create_session(current_session_msgs))
                current_session_msgs = [msg]
            else:
                current_session_msgs.append(msg)
                
        if current_session_msgs:
            sessions.append(self._create_session(current_session_msgs))
            
        return sessions

    def _create_session(self, messages: List[Message]) -> Session:
        start_time = messages[0].timestamp
        end_time = messages[-1].timestamp
        participants = list(set([m.normalized_sender for m in messages]))
        duration = (end_time - start_time).total_seconds() if end_time and start_time else 0.0
        
        return Session(
            session_id=str(uuid.uuid4()),
            start_time=start_time,
            end_time=end_time,
            messages=messages,
            participants=participants,
            message_count=len(messages),
            duration_seconds=duration
        )
