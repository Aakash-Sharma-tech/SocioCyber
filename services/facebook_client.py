import requests
from datetime import datetime
from typing import List, Dict

class FacebookClient:
    def __init__(self, key_manager):
        self.key_manager = key_manager
        self.base_url = "https://graph.facebook.com/v18.0"

    def fetch_posts(self, query: str, max_results: int = 30) -> List[Dict]:
        creds = self.key_manager.get_available_key('facebook')
        access_token = None
        if isinstance(creds, (list, tuple)) and len(creds) >= 3:
            access_token = creds[2]
        elif isinstance(creds, str):
            access_token = creds
        if not access_token:
            return self._get_demo_data()

        try:
            # Prefer page feed if FACEBOOK_PAGE_ID is provided (recommended)
            import os
            page_id = os.getenv('FACEBOOK_PAGE_ID')
            fields = 'message,permalink_url,created_time,from'
            params = {
                'fields': fields,
                'access_token': access_token,
                'limit': min(max_results, 50)
            }
            endpoint = f"{self.base_url}/{page_id}/feed" if page_id else f"{self.base_url}/me/feed"
            resp = requests.get(endpoint, params=params, timeout=20)
            if resp.status_code != 200:
                return self._get_demo_data()
            data = resp.json()
            items = []
            for p in data.get('data', []):
                content = p.get('message') or ''
                if query.lower() in content.lower():
                    items.append({
                        'platform': 'Facebook',
                        'content': content,
                        'author': (p.get('from') or {}).get('name', 'Unknown'),
                        'id': p.get('id', ''),
                        'timestamp': p.get('created_time', datetime.now().isoformat()),
                        'url': p.get('permalink_url', '')
                    })
                if len(items) >= max_results:
                    break
            return items if items else self._get_demo_data()
        except Exception:
            return self._get_demo_data()

    def _get_demo_data(self) -> List[Dict]:
        return [
            {
                'platform': 'Facebook',
                'content': 'Community update: combating disinformation with verified sources. #StopPropaganda',
                'author': 'fb_demo_user',
                'id': 'demo_fb_1',
                'timestamp': datetime.now().isoformat(),
                'url': 'https://facebook.com/posts/demo1'
            }
        ]


