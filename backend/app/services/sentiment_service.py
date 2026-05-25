import google.generativeai as genai
from textblob import TextBlob
from flask import current_app
import json

class SentimentService:
    def __init__(self, api_key=None):
        self.api_key = api_key or current_app.config.get("GEMINI_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel("gemini-pro")

    def analyze_sentiment(self, text):
        if not text.strip():
            return {
                "sentiment": "neutral",
                "score": 0.0,
                "confidence": 0.0,
                "method": "empty_text"
            }

        try:
            if self.api_key:
                prompt = (
                    "Analyze the sentiment of this text and respond ONLY in JSON format like this:\n"
                    '{ "sentiment": "positive", "score": 0.8, "confidence": 0.9 }\n'
                    f'Text: "{text}"'
                )
                response = self.model.generate_content(prompt)
                result = response.text.strip()

                # Try parsing the JSON
                sentiment_data = json.loads(result)
                sentiment_data["method"] = "gemini"
                return sentiment_data

        except Exception as e:
            current_app.logger.warning(f"Gemini API failed: {e}")

        # Fallback to TextBlob
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        sentiment = "positive" if polarity > 0 else "negative" if polarity < 0 else "neutral"

        return {
            "sentiment": sentiment,
            "score": polarity,
            "confidence": abs(polarity),
            "method": "textblob"
        }
