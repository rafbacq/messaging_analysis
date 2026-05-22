from typing import List, Dict, Any
from src.schemas.models import Message
import logging

logger = logging.getLogger(__name__)

class NLPProcessor:
    def __init__(self, use_transformers: bool = False):
        self.use_transformers = use_transformers
        self.sentiment_analyzer = None
        self._init_sentiment()

    def _init_sentiment(self):
        try:
            from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
            self.sentiment_analyzer = SentimentIntensityAnalyzer()
        except ImportError:
            logger.warning("vaderSentiment not installed. Sentiment analysis will be disabled.")

    def compute_sentiment(self, text: str) -> float:
        if not self.sentiment_analyzer or not text:
            return 0.0
        try:
            return self.sentiment_analyzer.polarity_scores(text)['compound']
        except Exception:
            return 0.0

    def extract_dialogue_acts(self, text: str) -> List[str]:
        acts = []
        if not text:
            return acts
        
        text_lower = text.lower()
        if "?" in text or text_lower.startswith(("what", "why", "how", "where", "when", "who", "do ", "is ", "are ", "can ", "could ")):
            acts.append("question")
        if any(w in text_lower for w in ["haha", "lol", "lmao", "rofl", "hehe"]):
            acts.append("laugh")
        if any(w in text_lower for w in ["sorry", "my bad", "apologies"]):
            acts.append("apology")
        if any(w in text_lower for w in ["thanks", "thank you", "appreciate"]):
            acts.append("gratitude")
            
        return acts

    def process_messages(self, messages: List[Message]) -> List[Dict[str, Any]]:
        features = []
        for msg in messages:
            sentiment = self.compute_sentiment(msg.text)
            acts = self.extract_dialogue_acts(msg.text)
            features.append({
                "message_id": msg.message_id,
                "sentiment": sentiment,
                "dialogue_acts": acts,
                "word_count": len(str(msg.text).split()) if msg.text else 0
            })
        return features
