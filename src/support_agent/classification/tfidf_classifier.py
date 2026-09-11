"""TF-IDF + Logistic Regression Intent Classifier.

Pipeline:
customer text/context -> TF-IDF -> LogisticRegression
Trained strictly on development conversations with conversation-level isolation.
"""

from __future__ import annotations

import json
from pathlib import Path
import pickle
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

from support_agent.classification.majority import INTENT_TO_AREA


class TfidfIntentClassifier:
    """TF-IDF + Logistic Regression multi-class intent classifier."""

    def __init__(
        self,
        max_features: int = 10000,
        ngram_range: Tuple[int, int] = (1, 2),
        C: float = 1.0,
        max_iter: int = 1000,
        random_state: int = 42,
    ):
        self.max_features = max_features
        self.ngram_range = ngram_range
        self.C = C
        self.max_iter = max_iter
        self.random_state = random_state

        self.vectorizer = TfidfVectorizer(
            ngram_range=self.ngram_range,
            max_features=self.max_features,
            sublinear_tf=True,
            stop_words="english",
        )
        self.classifier = LogisticRegression(
            C=self.C,
            max_iter=self.max_iter,
            class_weight="balanced",
            random_state=self.random_state,
        )
        self.classes_: List[str] = []
        self.is_fitted: bool = False

    def _prepare_text(self, text: Optional[str], context: Optional[str] = None) -> str:
        """Combine customer text and turn context."""
        parts = []
        if text and str(text).strip():
            parts.append(str(text).strip())
        if context and str(context).strip():
            # Add context without redundant customer turn
            parts.append(str(context).strip())
        return " \n ".join(parts) if parts else ""

    def fit(
        self,
        texts: List[str],
        labels: List[str],
    ) -> "TfidfIntentClassifier":
        """Fit TF-IDF vectorizer and Logistic Regression classifier."""
        if len(texts) != len(labels):
            raise ValueError(f"Mismatch: {len(texts)} texts vs {len(labels)} labels")

        X = self.vectorizer.fit_transform(texts)
        self.classifier.fit(X, labels)
        self.classes_ = list(self.classifier.classes_)
        self.is_fitted = True
        return self

    def predict(self, texts: List[str]) -> List[str]:
        """Predict primary intent labels."""
        if not self.is_fitted:
            raise RuntimeError("Classifier must be fitted before predict.")
        X = self.vectorizer.transform(texts)
        preds = self.classifier.predict(X)
        return list(preds)

    def predict_proba(self, texts: List[str]) -> np.ndarray:
        """Predict class probability distribution."""
        if not self.is_fitted:
            raise RuntimeError("Classifier must be fitted before predict_proba.")
        X = self.vectorizer.transform(texts)
        return self.classifier.predict_proba(X)

    def predict_cases(self, cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Predict standardized classification output records for golden cases."""
        texts = [self._prepare_text(c.get("customer_message"), c.get("context")) for c in cases]
        preds = self.predict(texts)
        probas = self.predict_proba(texts)

        records = []
        for i, (pred, prob_dist) in enumerate(zip(preds, probas)):
            max_prob = float(np.max(prob_dist))
            area = INTENT_TO_AREA.get(pred, "DELIVERY_AND_FULFILLMENT")
            records.append({
                "classification_status": "NORMAL",
                "areas": [area],
                "intents": [pred],
                "primary_intent": pred,
                "is_multi_intent": False,
                "states": ["INITIAL_INQUIRY"],
                "confidence": round(max_prob, 4),
            })
        return records

    def save(self, output_dir: Path | str) -> Path:
        """Serialize model artifacts to disk."""
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)

        bundle = {
            "vectorizer": self.vectorizer,
            "classifier": self.classifier,
            "classes_": self.classes_,
            "params": {
                "max_features": self.max_features,
                "ngram_range": self.ngram_range,
                "C": self.C,
                "max_iter": self.max_iter,
                "random_state": self.random_state,
            },
        }

        model_file = out_path / "tfidf_model.pkl"
        with open(model_file, "wb") as f:
            pickle.dump(bundle, f)

        meta_file = out_path / "metadata.json"
        with open(meta_file, "w", encoding="utf-8") as f:
            json.dump({
                "classes": self.classes_,
                "num_classes": len(self.classes_),
                "vocabulary_size": len(self.vectorizer.vocabulary_),
                "model_type": "TfidfVectorizer + LogisticRegression",
            }, f, indent=2)

        return model_file

    @classmethod
    def load(cls, model_dir: Path | str) -> "TfidfIntentClassifier":
        """Load serialized model bundle from disk."""
        model_path = Path(model_dir) / "tfidf_model.pkl"
        if not model_path.exists():
            raise FileNotFoundError(f"Model file not found at: {model_path}")

        with open(model_path, "rb") as f:
            bundle = pickle.load(f)

        clf = cls(**bundle["params"])
        clf.vectorizer = bundle["vectorizer"]
        clf.classifier = bundle["classifier"]
        clf.classes_ = bundle["classes_"]
        clf.is_fitted = True
        return clf
