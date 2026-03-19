import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict

class NewsClient:
    def __init__(self, key_manager):
        self.key_manager = key_manager
        self.base_url = "https://newsapi.org/v2"
    
    def fetch_articles(self, query: str, max_results: int = 30) -> List[Dict]:
        """Fetch news articles related to the query"""
        try:
            api_key = self.key_manager.get_available_key('news')
            if not api_key:
                return self._get_demo_data()
            
            # Search for articles from the last 7 days
            from_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            
            params = {
                'q': f'"{query}" OR "India propaganda" OR "anti-India"',
                'from': from_date,
                'sortBy': 'publishedAt',
                'language': 'en',
                'pageSize': min(max_results, 100),
                'apiKey': api_key
            }
            
            response = requests.get(
                f"{self.base_url}/everything",
                params=params,
                timeout=30
            )
            
            if response.status_code == 429:  # Rate limited
                self.key_manager.mark_key_limited('news', api_key)
                return self._get_demo_data()
            
            if response.status_code != 200:
                print(f"News API error: {response.status_code} - {response.text}")
                return self._get_demo_data()
            
            data = response.json()
            
            if data['status'] != 'ok' or not data.get('articles'):
                return self._get_demo_data()
            
            processed_articles = []
            for article in data['articles']:
                # Skip articles without proper content
                if not article.get('title') or article.get('title') == '[Removed]':
                    continue
                
                content = article.get('title', '')
                if article.get('description'):
                    content += '\n\n' + article['description']
                if article.get('content'):
                    content += '\n\n' + article['content'].split('[+')[0]  # Remove "read more" text
                
                processed_articles.append({
                    'platform': 'News',
                    'content': content,
                    'author': article.get('author', article.get('source', {}).get('name', 'Unknown')),
                    'id': article['url'],
                    'timestamp': article.get('publishedAt', datetime.now().isoformat()),
                    'url': article['url'],
                    'source': article.get('source', {}).get('name', 'Unknown'),
                    'title': article.get('title', ''),
                    'image_url': article.get('urlToImage')
                })
            
            return processed_articles
            
        except Exception as e:
            print(f"Error fetching news data: {str(e)}")
            return self._get_demo_data()
    
    def _get_demo_data(self) -> List[Dict]:
        """Return demo news data when API is not available"""
        demo_articles = [
            {
                'platform': 'News',
                'content': 'Investigation Reveals Coordinated Anti-India Propaganda Campaign\n\nA comprehensive investigation has uncovered a sophisticated disinformation campaign targeting India across multiple social media platforms...',
                'author': 'Reuters Investigation Team',
                'id': 'demo_news_1',
                'timestamp': datetime.now().isoformat(),
                'url': 'https://reuters.com/investigation/anti-india-propaganda',
                'source': 'Reuters',
                'title': 'Investigation Reveals Coordinated Anti-India Propaganda Campaign',
                'image_url': 'https://images.pexels.com/photos/96612/pexels-photo-96612.jpeg'
            },
            {
                'platform': 'News',
                'content': 'Social Media Giants Combat Foreign Interference in Indian Elections\n\nMajor social media platforms announce new measures to detect and prevent foreign propaganda campaigns...',
                'author': 'Tech News Daily',
                'id': 'demo_news_2',
                'timestamp': datetime.now().isoformat(),
                'url': 'https://technewsdaily.com/social-media-combat-interference',
                'source': 'Tech News Daily',
                'title': 'Social Media Giants Combat Foreign Interference in Indian Elections',
                'image_url': 'https://images.pexels.com/photos/267350/pexels-photo-267350.jpeg'
            },
            {
                'platform': 'News',
                'content': 'Fact-Checkers Unite Against Misinformation Targeting India\n\nInternational fact-checking organizations collaborate to combat false narratives and propaganda campaigns...',
                'author': 'Global Media Watch',
                'id': 'demo_news_3',
                'timestamp': datetime.now().isoformat(),
                'url': 'https://globalmediawatch.com/fact-checkers-unite-india',
                'source': 'Global Media Watch',
                'title': 'Fact-Checkers Unite Against Misinformation Targeting India',
                'image_url': 'https://images.pexels.com/photos/518543/pexels-photo-518543.jpeg'
            }
        ]
        
        return demo_articles