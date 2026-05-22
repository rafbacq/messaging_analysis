from datetime import datetime
from src.schemas.models import Message
from src.processing.cleaner import DataCleaner
from src.processing.sessionizer import Sessionizer

def test_cleaner_redaction():
    cleaner = DataCleaner(redact_pii=True)
    msgs = [
        Message("test.html", "test", "1", "Me", "me", datetime.now(), "", "Call me at 555-123-4567 or email at test@example.com", True)
    ]
    cleaned = cleaner.clean_messages(msgs)
    assert "[PHONE]" in cleaned[0].text
    assert "[EMAIL]" in cleaned[0].text

def test_sessionizer():
    sessionizer = Sessionizer(session_gap_minutes=120)
    msgs = [
        Message("test.html", "test", "1", "Me", "me", datetime(2023, 1, 1, 10, 0), "", "Hello", True),
        Message("test.html", "test", "2", "Other", "other", datetime(2023, 1, 1, 10, 5), "", "Hi", False),
        Message("test.html", "test", "3", "Me", "me", datetime(2023, 1, 1, 15, 0), "", "Later", True),
    ]
    sessions = sessionizer.group_into_sessions(msgs)
    assert len(sessions) == 2
    assert sessions[0].message_count == 2
    assert sessions[1].message_count == 1
