import requests
import json
from datetime import datetime
from typing import List, Dict
import time

class RedditClient:
    def __init__(self, key_manager):
        self.key_manager = key_manager
        self.base_url = "https://www.reddit.com"
        self.access_token = None
        self.token_expires_at = 0
    
    def _get_access_token(self):
        """Get Reddit OAuth access token"""
        try:
            client_id = self.key_manager.get_available_key('reddit')[0] if self.key_manager.get_available_key('reddit') else None
            client_secret = self.key_manager.get_available_key('reddit')[1] if self.key_manager.get_available_key('reddit') else None
            
            if not client_id or not client_secret:
                return None
            
            auth = requests.auth.HTTPBasicAuth(client_id, client_secret)
            data = {
                'grant_type': 'client_credentials'
            }
            headers = {
                'User-Agent': 'CampaignDetector/1.0'
            }
            
            response = requests.post(
                'https://www.reddit.com/api/v1/access_token',
                auth=auth,
                data=data,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data['access_token']
                self.token_expires_at = time.time() + token_data['expires_in'] - 60  # 60 second buffer
                return self.access_token
            
            return None
            
        except Exception as e:
            print(f"Error getting Reddit access token: {str(e)}")
            return None
    
    def fetch_posts(self, query: str, max_results: int = 50) -> List[Dict]:
        """Fetch Reddit posts related to the query"""
        try:
            # Check if we need a new token
            if not self.access_token or time.time() > self.token_expires_at:
                token = self._get_access_token()
                if not token:
                    return self._get_demo_data()
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'User-Agent': 'CampaignDetector/1.0'
            }
            
            # Search across multiple subreddits
            subreddits = ['worldnews', 'news', 'india', 'geopolitics', 'IndiaSpeaks']
            all_posts = []
            
            for subreddit in subreddits:
                if len(all_posts) >= max_results:
                    break
                
                try:
                    params = {
                        'q': query,
                        'sort': 'new',
                        'limit': min(25, max_results - len(all_posts)),
                        'type': 'link',
                        'restrict_sr': 'true'
                    }
                    
                    response = requests.get(
                        f"https://oauth.reddit.com/r/{subreddit}/search",
                        headers=headers,
                        params=params,
                        timeout=30
                    )
                    
                    if response.status_code == 429:  # Rate limited
                        continue
                    
                    if response.status_code != 200:
                        continue
                    
                    data = response.json()
                    
                    if 'data' in data and 'children' in data['data']:
                        for post in data['data']['children']:
                            post_data = post['data']
                            
                            # Skip deleted or removed posts
                            if post_data.get('removed_by_category') or not post_data.get('title'):
                                continue
                            
                            content = post_data.get('title', '')
                            if post_data.get('selftext'):
                                content += '\n\n' + post_data['selftext']
                            
                            all_posts.append({
                                'platform': 'Reddit',
                                'content': content,
                                'author': post_data.get('author', 'Unknown'),
                                'id': post_data['id'],
                                'timestamp': datetime.fromtimestamp(post_data['created_utc']).isoformat(),
                                'url': f"https://reddit.com{post_data['permalink']}",
                                'subreddit': post_data['subreddit'],
                                'score': post_data.get('score', 0),
                                'num_comments': post_data.get('num_comments', 0)
                            })
                    
                    time.sleep(0.5)  # Rate limiting
                    
                except Exception as e:
                    print(f"Error fetching from r/{subreddit}: {str(e)}")
                    continue
            
            return all_posts[:max_results] if all_posts else self._get_demo_data()
            
        except Exception as e:
            print(f"Error fetching Reddit data: {str(e)}")
            return self._get_demo_data()
    
    def _get_demo_data(self) -> List[Dict]:
        """Return demo Reddit data when API is not available"""
        demo_posts = [
            {
                'platform': 'Reddit',
                'content': 'Analysis: Recent propaganda campaigns targeting India - patterns and sources\n\nI\'ve been tracking suspicious coordinated posts across multiple platforms...',
                'author': 'digital_detective',
                'id': 'demo_reddit_1',
                'timestamp': datetime.now().isoformat(),
                'url': 'https://reddit.com/r/geopolitics/comments/demo_reddit_1',
                'subreddit': 'geopolitics',
                'score': 234,
                'num_comments': 45
            },
            {
                'platform': 'Reddit',
                'content': 'Fact-check: Debunking false claims about Indian democracy and institutions',
                'author': 'fact_checker_in',
                'id': 'demo_reddit_2',
                'timestamp': datetime.now().isoformat(),
                'url': 'https://reddit.com/r/india/comments/demo_reddit_2',
                'subreddit': 'india',
                'score': 156,
                'num_comments': 78
            },
            {
                'platform': 'Reddit',
                'content': 'Foreign interference in social media: How to identify and report propaganda',
                'author': 'security_expert',
                'id': 'demo_reddit_3',
                'timestamp': datetime.now().isoformat(),
                'url': 'https://reddit.com/r/worldnews/comments/demo_reddit_3',
                'subreddit': 'worldnews',
                'score': 445,
                'num_comments': 123
            }
        ]
        
        return demo_posts