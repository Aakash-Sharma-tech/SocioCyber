import requests
import json
from datetime import datetime
from typing import List, Dict
import time

class TwitterClient:
    def __init__(self, key_manager):
        self.key_manager = key_manager
        self.base_url = "https://api.twitter.com/2"
    
    def fetch_posts(self, query: str, max_results: int = 50) -> List[Dict]:
        """Fetch tweets related to the query"""
        try:
            bearer_token = self.key_manager.get_available_key('twitter')
            if not bearer_token:
                return self._get_demo_data()
            
            headers = {
                'Authorization': f'Bearer {bearer_token}',
                'Content-Type': 'application/json'
            }
            
            params = {
                'query': query + ' -is:retweet lang:en',
                'max_results': min(max_results, 100),
                'tweet.fields': 'created_at,author_id,public_metrics,lang,context_annotations',
                'user.fields': 'username,public_metrics',
                'expansions': 'author_id'
            }
            
            response = requests.get(
                f"{self.base_url}/tweets/search/recent",
                headers=headers,
                params=params,
                timeout=30
            )
            
            if response.status_code == 429:  # Rate limited
                self.key_manager.mark_key_limited('twitter', bearer_token)
                return self._get_demo_data()
            
            if response.status_code != 200:
                print(f"Twitter API error: {response.status_code} - {response.text}")
                return self._get_demo_data()
            
            data = response.json()
            
            if 'data' not in data:
                return self._get_demo_data()
            
            # Process tweets
            tweets = data['data']
            users = {user['id']: user for user in data.get('includes', {}).get('users', [])}
            
            processed_tweets = []
            for tweet in tweets:
                author_id = tweet.get('author_id', '')
                author_info = users.get(author_id, {})
                
                processed_tweets.append({
                    'platform': 'Twitter',
                    'content': tweet['text'],
                    'author': author_info.get('username', 'Unknown'),
                    'id': tweet['id'],
                    'timestamp': tweet.get('created_at', datetime.now().isoformat()),
                    'url': f"https://twitter.com/{author_info.get('username', 'unknown')}/status/{tweet['id']}",
                    'metrics': tweet.get('public_metrics', {}),
                    'language': tweet.get('lang', 'en')
                })
            
            return processed_tweets
            
        except Exception as e:
            print(f"Error fetching Twitter data: {str(e)}")
            return self._get_demo_data()
    
    def _get_demo_data(self) -> List[Dict]:
        """Return demo Twitter data when API is not available"""
        demo_tweets = [
            {
                'platform': 'Twitter',
                'content': 'Stop spreading false narratives about India. Our democracy is strong and vibrant. #StopPropaganda',
                'author': 'demo_user1',
                'id': 'demo_1',
                'timestamp': datetime.now().isoformat(),
                'url': 'https://twitter.com/demo_user1/status/demo_1',
                'metrics': {'retweet_count': 45, 'like_count': 120},
                'language': 'en'
            },
            {
                'platform': 'Twitter',
                'content': 'The recent article about India contains several misleading statements. Here are the facts...',
                'author': 'fact_checker',
                'id': 'demo_2',
                'timestamp': datetime.now().isoformat(),
                'url': 'https://twitter.com/fact_checker/status/demo_2',
                'metrics': {'retweet_count': 78, 'like_count': 203},
                'language': 'en'
            },
            {
                'platform': 'Twitter',
                'content': 'Another coordinated attack on India trending. Same patterns, same timing. Investigate the sources.',
                'author': 'security_analyst',
                'id': 'demo_3',
                'timestamp': datetime.now().isoformat(),
                'url': 'https://twitter.com/security_analyst/status/demo_3',
                'metrics': {'retweet_count': 156, 'like_count': 389},
                'language': 'en'
            }
        ]
        
        return demo_tweets