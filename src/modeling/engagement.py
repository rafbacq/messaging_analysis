import pandas as pd
from typing import Dict, Any, Tuple
import logging

try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler
except ImportError:
    pass

logger = logging.getLogger(__name__)

class EngagementModel:
    def __init__(self, use_rf: bool = True):
        self.use_rf = use_rf
        self.model = None
        self.scaler = None
        self.feature_names = [
            "message_count", 
            "duration_seconds",
            "me_messages",
            "other_messages",
            "avg_sentiment",
            "has_questions",
            "time_since_last_session"
        ]

    def _extract_features(self, sessions: list) -> pd.DataFrame:
        data = []
        for i, s in enumerate(sessions):
            me_msgs = sum(1 for m in s.messages if m.normalized_sender == 'me')
            other_msgs = s.message_count - me_msgs
            has_q = any("?" in str(m.text) for m in s.messages if m.text)
            
            time_since = 0
            if i > 0 and s.start_time and sessions[i-1].end_time:
                time_since = (s.start_time - sessions[i-1].end_time).total_seconds()
                
            # Target: did another session happen within 24 hours?
            target = 0
            if i < len(sessions) - 1 and sessions[i+1].start_time and s.end_time:
                if (sessions[i+1].start_time - s.end_time).total_seconds() < 86400:
                    target = 1
                    
            data.append({
                "message_count": s.message_count,
                "duration_seconds": s.duration_seconds,
                "me_messages": me_msgs,
                "other_messages": other_msgs,
                "avg_sentiment": 0.0, # To be filled if we pass NLP features
                "has_questions": 1 if has_q else 0,
                "time_since_last_session": time_since,
                "target": target
            })
        return pd.DataFrame(data)

    def train(self, sessions: list) -> Dict[str, Any]:
        df = self._extract_features(sessions)
        if df.empty or len(df) < 10:
            return {"error": "Not enough data to train"}
            
        # Chronological split (last 20% for testing)
        split_idx = int(len(df) * 0.8)
        train_df = df.iloc[:split_idx]
        test_df = df.iloc[split_idx:]
        
        X_train = train_df[self.feature_names]
        y_train = train_df["target"]
        X_test = test_df[self.feature_names]
        y_test = test_df["target"]
        
        # Scale
        try:
            self.scaler = StandardScaler()
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            if self.use_rf:
                self.model = RandomForestClassifier(n_estimators=100, random_state=42)
            else:
                self.model = LogisticRegression(random_state=42)
                
            self.model.fit(X_train_scaled, y_train)
            
            acc = self.model.score(X_test_scaled, y_test)
            
            importances = []
            if self.use_rf:
                importances = list(zip(self.feature_names, self.model.feature_importances_))
            else:
                importances = list(zip(self.feature_names, self.model.coef_[0]))
                
            return {
                "accuracy": acc,
                "feature_importances": sorted(importances, key=lambda x: abs(x[1]), reverse=True),
                "train_size": len(X_train),
                "test_size": len(X_test)
            }
        except NameError:
            return {"error": "scikit-learn not installed"}

    def predict(self, session) -> float:
        if not self.model or not self.scaler:
            return 0.0
        # In a real pipeline, we'd extract and scale a single session's features here
        return 0.5
