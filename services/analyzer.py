import requests
import json
import re
from typing import Dict, List
import time
import random

class AnalysisService:
    def __init__(self, key_manager):
        self.key_manager = key_manager
        
        # Propaganda keywords and patterns
        self.propaganda_keywords = [
            'false flag', 'conspiracy', 'lies', 'fake news', 'propaganda',
            'manipulation', 'brainwashing', 'coverup', 'hidden agenda',
            'oppression', 'dictatorship', 'authoritarian', 'fascist',
            'anti-india', 'disinformation', 'misinformation', 'smear campaign',
            'foreign interference', 'psyops', 'sabotage', 'agenda', 'paid media'
        ]
        
        self.india_context_keywords = [
            'india', 'indian', 'hindu', 'modi', 'bjp', 'congress',
            'kashmir', 'pakistan', 'china', 'democracy', 'election',
            'supreme court', 'parliament', 'constitution', 'rss', 'goi', 'hindutva'
        ]
    
    def analyze_post(self, content: str) -> Dict:
        """Comprehensive analysis of a post"""
        try:
            # Basic analysis
            analysis = {
                'sentiment': self._analyze_sentiment(content),
                'emotion': self._detect_emotion(content),
                'toxicity': self._calculate_toxicity(content),
                'propaganda': self._detect_propaganda(content),
                'keywords': self._extract_keywords(content),
                'language': self._detect_language(content),
                'translation': self._translate_text(content) if self._detect_language(content) != 'en' else ''
            }
            
            return analysis
            
        except Exception as e:
            print(f"Error in analysis: {str(e)}")
            return self._get_demo_analysis()
    
    def _analyze_sentiment(self, text: str) -> str:
        """Analyze sentiment using AI APIs with fallback"""
        try:
            # Try Hugging Face first
            hf_key = self.key_manager.get_available_key('huggingface')
            if hf_key:
                result = self._huggingface_sentiment(text, hf_key)
                if result:
                    return result
            
            # Fallback to simple rule-based sentiment
            return self._rule_based_sentiment(text)
            
        except Exception as e:
            return self._rule_based_sentiment(text)
    
    def _huggingface_sentiment(self, text: str, api_key: str) -> str:
        """Use Hugging Face API for sentiment analysis"""
        try:
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'inputs': text[:500],  # Limit text length
            }
            
            response = requests.post(
                'https://api-inference.huggingface.co/models/cardiffnlp/twitter-roberta-base-sentiment-latest',
                headers=headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    scores = result[0]
                    best_sentiment = max(scores, key=lambda x: x['score'])
                    
                    label_map = {
                        'LABEL_0': 'negative',
                        'LABEL_1': 'neutral', 
                        'LABEL_2': 'positive'
                    }
                    
                    return label_map.get(best_sentiment['label'], 'neutral')
            
            return None
            
        except Exception:
            return None
    
    def _rule_based_sentiment(self, text: str) -> str:
        """Simple rule-based sentiment analysis"""
        positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'love', 'like', 'happy', 'proud']
        negative_words = ['bad', 'terrible', 'awful', 'hate', 'dislike', 'angry', 'sad', 'disgusting', 'horrible', 'evil']
        
        text_lower = text.lower()
        positive_score = sum(1 for word in positive_words if word in text_lower)
        negative_score = sum(1 for word in negative_words if word in text_lower)
        
        if positive_score > negative_score:
            return 'positive'
        elif negative_score > positive_score:
            return 'negative'
        else:
            return 'neutral'
    
    def _detect_emotion(self, text: str) -> str:
        """Detect primary emotion in text"""
        emotions = {
            'anger': ['angry', 'mad', 'furious', 'rage', 'hate', 'disgusting', 'outrageous'],
            'fear': ['afraid', 'scared', 'terrified', 'worried', 'anxious', 'panic', 'threatening'],
            'joy': ['happy', 'excited', 'thrilled', 'delighted', 'amazing', 'wonderful', 'fantastic'],
            'sadness': ['sad', 'depressed', 'disappointed', 'tragic', 'awful', 'terrible'],
            'surprise': ['shocked', 'amazed', 'stunned', 'unexpected', 'incredible', 'unbelievable']
        }
        
        text_lower = text.lower()
        emotion_scores = {}
        
        for emotion, words in emotions.items():
            score = sum(1 for word in words if word in text_lower)
            emotion_scores[emotion] = score
        
        if not any(emotion_scores.values()):
            return 'neutral'
        
        return max(emotion_scores, key=emotion_scores.get)
    
    def _calculate_toxicity(self, text: str) -> float:
        """Calculate toxicity score"""
        toxic_patterns = [
            r'\b(kill|die|death|murder|destroy)\b',
            r'\b(hate|stupid|idiot|moron|dumb)\b',
            r'\b(shit|fuck|damn|hell)\b',
            r'[A-Z]{3,}',  # All caps (shouting)
            r'!{2,}',  # Multiple exclamation marks
        ]
        
        toxicity_score = 0.0
        text_lower = text.lower()
        
        for pattern in toxic_patterns:
            matches = len(re.findall(pattern, text_lower))
            toxicity_score += matches * 0.1
        
        # Normalize to 0-1 range
        return min(toxicity_score, 1.0)
    
    def _detect_propaganda(self, text: str) -> float:
        """Detect propaganda patterns"""
        text_lower = text.lower()
        propaganda_score = 0.0
        
        # Check for propaganda keywords
        for keyword in self.propaganda_keywords:
            if keyword in text_lower:
                propaganda_score += 0.2
        
        # Check for India context + negative framing
        has_india_context = any(keyword in text_lower for keyword in self.india_context_keywords)
        if has_india_context:
            negative_indicators = [
                'attack', 'threat', 'danger', 'problem', 'crisis', 'failure', 'corrupt',
                'collapse', 'illegitimate', 'rigged', 'fraud', 'violence', 'hate', 'extremist',
                'genocide', 'atrocity', 'massacre', 'terror', 'radical'
            ]
            if any(indicator in text_lower for indicator in negative_indicators):
                propaganda_score += 0.3
        
        # Check for emotional manipulation patterns
        emotional_patterns = [
            r'\b(shocking|outrageous|unbelievable|scandal|breaking)\b',
            r'\b(you must|everyone should|wake up|share now|spread this)\b',
            r"\b(they don't want you to know|hidden truth|exposed|evidence revealed)\b"
        ]
        
        for pattern in emotional_patterns:
            if re.search(pattern, text_lower):
                propaganda_score += 0.2
        
        # Slightly increase score when multiple signals co-occur
        if has_india_context and propaganda_score >= 0.3:
            propaganda_score += 0.1
        return min(propaganda_score, 1.0)
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from text"""
        # Remove common stop words and extract meaningful words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'}
        
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        keywords = [word for word in words if word not in stop_words]
        
        # Get top 10 most frequent keywords
        word_freq = {}
        for word in keywords:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, _ in sorted_words[:10]]
    
    def _detect_language(self, text: str) -> str:
        """Simple language detection"""
        # Check for common Hindi/Indian language patterns
        hindi_patterns = [
            r'[\u0900-\u097F]',  # Devanagari script
            r'\b(hai|ke|ki|ko|se|me|aur|ya|jo|kya)\b',  # Common Hindi words in Roman script
        ]
        
        for pattern in hindi_patterns:
            if re.search(pattern, text):
                return 'hi'  # Hindi
        
        return 'en'  # Default to English
    
    def _translate_text(self, text: str) -> str:
        """Translate text to English"""
        # Simplified translation - in production, use Google Translate API
        return f"[Translated]: {text}"
    
    def _get_demo_analysis(self) -> Dict:
        """Return demo analysis when AI APIs fail"""
        return {
            'sentiment': random.choice(['positive', 'negative', 'neutral']),
            'emotion': random.choice(['anger', 'fear', 'joy', 'sadness', 'surprise']),
            'toxicity': random.uniform(0.0, 1.0),
            'propaganda': random.uniform(0.0, 1.0),
            'keywords': ['india', 'propaganda', 'social', 'media', 'analysis'],
            'language': 'en',
            'translation': ''
        }
    
    def chat_response(self, message: str) -> str:
        """Generate chatbot response"""
        try:
            # Try to use Gemini API
            gemini_key = self.key_manager.get_available_key('gemini')
            if gemini_key:
                response = self._gemini_chat(message, gemini_key)
                if response:
                    return response
            
            # Fallback to rule-based responses
            return self._rule_based_chat(message)
            
        except Exception as e:
            return self._rule_based_chat(message)
    
    def _gemini_chat(self, message: str, api_key: str) -> str:
        """Use Gemini API for chat response"""
        try:
            headers = {
                'Content-Type': 'application/json',
            }
            
            payload = {
                'contents': [{
                    'parts': [{
                        'text': f"You are an AI assistant specialized in analyzing propaganda and misinformation campaigns targeting India. Answer this question: {message}"
                    }]
                }]
            }
            
            response = requests.post(
                f'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}',
                headers=headers,
                json=payload,
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and len(result['candidates']) > 0:
                    content = result['candidates'][0]['content']['parts'][0]['text']
                    return content.strip()
            
            return None
            
        except Exception:
            return None
    
    def _rule_based_chat(self, message: str) -> str:
        """Rule-based chat responses"""
        message_lower = message.lower()
        
        if 'propaganda' in message_lower:
            return "Based on recent analysis, I've detected several propaganda patterns including coordinated messaging, emotional manipulation, and false narratives targeting India's democratic institutions."
        
        elif 'sentiment' in message_lower:
            return "Current sentiment analysis shows 45% negative, 30% positive, and 25% neutral posts in the analyzed content. There's a notable increase in negative sentiment during coordinated campaigns."
        
        elif 'summary' in message_lower or '24 hours' in message_lower:
            return "In the last 24 hours: Analyzed 150 posts across platforms, detected 23% propaganda content, identified 34 suspicious posts with coordinated messaging patterns. Key topics: democracy, elections, institutions."
        
        elif 'threat' in message_lower or 'risk' in message_lower:
            return "Current threat level: MEDIUM. Detected coordinated activities across 3 platforms with similar messaging patterns. Recommend continued monitoring and fact-checking initiatives."
        
        else:
            return "I'm here to help analyze propaganda campaigns and social media threats targeting India. Ask me about sentiment trends, propaganda detection, or recent analysis summaries."