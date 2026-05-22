from typing import List, Dict, Any
from src.schemas.models import Session
import logging

logger = logging.getLogger(__name__)

class DynamicsScorer:
    def __init__(self, weights: Dict[str, float] = None):
        self.weights = weights or {
            "response_time": 0.3,
            "initiation": 0.2,
            "sentiment": 0.2,
            "length": 0.15,
            "questions": 0.15
        }

    def compute_session_scores(self, session: Session, nlp_features: Dict[str, Dict[str, Any]]) -> Dict[str, float]:
        """
        Calculates interpretable, probabilistic scores for a session.
        Never claims to read minds.
        """
        if not session.messages:
            return {"engagement": 0.0, "warmth": 0.0, "reciprocity": 0.0}

        # Engagement: combination of message count, duration, and text length
        total_msgs = session.message_count
        duration = session.duration_seconds
        engagement_score = min(100.0, (total_msgs * 2) + (duration / 3600.0 * 10))

        # Warmth: average sentiment
        sentiments = []
        for msg in session.messages:
            feat = nlp_features.get(msg.message_id, {})
            sentiments.append(feat.get("sentiment", 0.0))
            
        avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0.0
        # Map -1..1 to 0..100
        warmth_score = (avg_sentiment + 1.0) * 50.0

        # Reciprocity: balance of messages between me and other
        me_count = sum(1 for m in session.messages if m.normalized_sender == "me")
        other_count = total_msgs - me_count
        
        if total_msgs > 0:
            ratio = min(me_count, other_count) / max(me_count, other_count) if max(me_count, other_count) > 0 else 0
            reciprocity_score = ratio * 100.0
        else:
            reciprocity_score = 0.0

        return {
            "engagement": round(engagement_score, 2),
            "warmth": round(warmth_score, 2),
            "reciprocity": round(reciprocity_score, 2)
        }
