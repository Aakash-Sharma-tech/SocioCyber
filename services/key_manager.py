import os
from dotenv import load_dotenv
import time
import random
from typing import Dict, List, Optional

class APIKeyManager:
    def __init__(self):
        # Ensure environment variables from .env are loaded
        try:
            load_dotenv()
        except Exception:
            pass
        self.api_keys = {
            'huggingface': [os.getenv('HUGGINGFACEHUB_API_KEY')],
            'gemini': [os.getenv('GEMINI_API_KEY')],
            'groq': [os.getenv('GROQCLOUD_API_KEY')],
            'deepseek': [os.getenv('DEEPSEEK_API_KEY')],
            'twitter': [os.getenv('TWITTER_BEARER_TOKEN')],
            'reddit': [(os.getenv('REDDIT_CLIENT_ID'), os.getenv('REDDIT_CLIENT_SECRET'))],
            'news': [os.getenv('NEWS_API_KEY')],
            'translate': [os.getenv('GOOGLE_TRANSLATE_KEY')]
        }
        # Social platform additions
        self.api_keys['instagram'] = [
            (
                os.getenv('INSTAGRAM_APP_ID'),
                os.getenv('INSTAGRAM_APP_SECRET'),
                os.getenv('INSTAGRAM_ACCESS_TOKEN')
            )
        ]
        self.api_keys['facebook'] = [
            (
                os.getenv('FACEBOOK_APP_ID'),
                os.getenv('FACEBOOK_APP_SECRET'),
                os.getenv('FACEBOOK_ACCESS_TOKEN')
            )
        ]
        self.api_keys['telegram'] = [
            (
                os.getenv('TELEGRAM_API_ID'),
                os.getenv('TELEGRAM_API_HASH')
            )
        ]
        
        # Rate limiting tracking
        self.rate_limits = {}
        self.current_key_index = {}
        
        # Initialize current key indices
        for service in self.api_keys:
            self.current_key_index[service] = 0
    
    def get_key(self, service: str) -> Optional[str]:
        """Get current API key for service with automatic failover"""
        if service not in self.api_keys:
            return None
            
        keys = [k for k in self.api_keys[service] if k is not None]
        if not keys:
            return None
            
        current_index = self.current_key_index[service]
        return keys[current_index % len(keys)]
    
    def mark_key_limited(self, service: str, key: str):
        """Mark a key as rate limited and switch to next"""
        if service in self.current_key_index:
            self.current_key_index[service] = (self.current_key_index[service] + 1) % len(self.api_keys[service])
            self.rate_limits[key] = time.time() + 3600  # Rate limit for 1 hour
    
    def is_key_available(self, service: str, key: str) -> bool:
        """Check if key is available (not rate limited)"""
        if key in self.rate_limits:
            return time.time() > self.rate_limits[key]
        return True
    
    def get_available_key(self, service: str) -> Optional[str]:
        """Get next available key that's not rate limited"""
        if service not in self.api_keys:
            return None
            
        keys = [k for k in self.api_keys[service] if k is not None]
        if not keys:
            return None
            
        # Try each key until we find an available one
        for _ in range(len(keys)):
            key = self.get_key(service)
            if self.is_key_available(service, key):
                return key
            self.mark_key_limited(service, key)
        
        # If all keys are limited, return the first one anyway
        return keys[0]
    
    def add_backup_keys(self, service: str, keys: List[str]):
        """Add backup API keys for a service"""
        if service in self.api_keys:
            self.api_keys[service].extend(keys)
        else:
            self.api_keys[service] = keys