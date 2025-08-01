import openai
from flask import current_app
import re
from textblob import TextBlob
import json

class SentimentService:
    def _init_(self):
        openai.api_key = current_app.config.get('OPENAI_API_KEY')
        self.use_openai = bool(openai.api_key)
    
    def analyze_sentiment(self, text):
        """Analyze sentiment of given text"""
        try:
            if self.use_openai:
                return self._analyze_with_openai(text)
            else:
                return self._analyze_with_textblob(text)
        except Exception as e:
            print(f"Error in sentiment analysis: {e}")
            return self._analyze_with_textblob(text)  # Fallback
    
    def _analyze_with_openai(self, text):
        """Use OpenAI for more accurate sentiment analysis"""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a sentiment analysis expert. Analyze the sentiment of the given text and respond with a JSON object containing 'label' (positive, negative, or neutral), 'score' (float between -1 and 1), and 'confidence' (float between 0 and 1)."
                    },
                    {
                        "role": "user",
                        "content": f"Analyze the sentiment of this text: '{text}'"
                    }
                ],
                max_tokens=100,
                temperature=0.1
            )
            
            result = response.choices[0].message.content.strip()
            
            # Try to parse JSON response
            try:
                sentiment_data = json.loads(result)
                return {
                    'label': sentiment_data.get('label', 'neutral'),
                    'score': float(sentiment_data.get('score', 0)),
                    'confidence': float(sentiment_data.get('confidence', 0.5)),
                    'method': 'openai'
                }
            except json.JSONDecodeError:
                # Fallback to regex parsing
                return self._parse_openai_response(result)
                
        except Exception as e:
            print(f"OpenAI sentiment analysis failed: {e}")
            return self._analyze_with_textblob(text)
    
    def _parse_openai_response(self, response):
        """Parse OpenAI response if JSON parsing fails"""
        # Extract sentiment label
        if 'positive' in response.lower():
            label = 'positive'
        elif 'negative' in response.lower():
            label = 'negative'
        else:
            label = 'neutral'
        
        # Try to extract score
        score_match = re.search(r'score[\'"]?\s*:\s*([+-]?\d*\.?\d+)', response)
        score = float(score_match.group(1)) if score_match else 0
        
        # Try to extract confidence
        confidence_match = re.search(r'confidence[\'"]?\s*:\s*(\d*\.?\d+)', response)
        confidence = float(confidence_match.group(1)) if confidence_match else 0.5
        
        return {
            'label': label,
            'score': score,
            'confidence': confidence,
            'method': 'openai_parsed'
        }
    
    def _analyze_with_textblob(self, text):
        """Fallback sentiment analysis using TextBlob"""
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity
            
            # Convert polarity to label
            if polarity > 0.1:
                label = 'positive'
            elif polarity < -0.1:
                label = 'negative'
            else:
                label = 'neutral'
            
            return {
                'label': label,
                'score': polarity,
                'confidence': abs(polarity),
                'subjectivity': subjectivity,
                'method': 'textblob'
            }
            
        except Exception as e:
            print(f"TextBlob sentiment analysis failed: {e}")
            return {
                'label': 'neutral',
                'score': 0.0,
                'confidence': 0.0,
                'method': 'fallback'
            }
    
    def analyze_batch_sentiments(self, texts):
        """Analyze sentiment for multiple texts"""
        results = []
        for text in texts:
            if text and text.strip():
                sentiment = self.analyze_sentiment(text.strip())
                results.append(sentiment)
            else:
                results.append({
                    'label': 'neutral',
                    'score': 0.0,
                    'confidence': 0.0,
                    'method': 'empty_text'
                })
        return results
    
    def get_sentiment_summary(self, sentiments):
        """Get summary statistics from sentiment analysis results"""
        if not sentiments:
            return {
                'total': 0,
                'positive': 0,
                'negative': 0,
                'neutral': 0,
                'average_score': 0.0,
                'overall_sentiment': 'neutral'
            }
        
        total = len(sentiments)
        positive = sum(1 for s in sentiments if s['label'] == 'positive')
        negative = sum(1 for s in sentiments if s['label'] == 'negative')
        neutral = sum(1 for s in sentiments if s['label'] == 'neutral')
        
        average_score = sum(s['score'] for s in sentiments) / total
        
        # Determine overall sentiment
        if average_score > 0.1:
            overall_sentiment = 'positive'
        elif average_score < -0.1:
            overall_sentiment = 'negative'
        else:
            overall_sentiment = 'neutral'
        
        return {
            'total': total,
            'positive': positive,
            'negative': negative,
            'neutral': neutral,
            'positive_percentage': (positive / total) * 100,
            'negative_percentage': (negative / total) * 100,
            'neutral_percentage': (neutral / total) * 100,
            'average_score': average_score,
            'overall_sentiment': overall_sentiment
        }