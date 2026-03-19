import os
import requests
from datetime import datetime
from typing import List, Dict

class InstagramClient:
    def __init__(self, key_manager):
        self.key_manager = key_manager
        self.base_url = "https://graph.facebook.com/v18.0"

    def fetch_posts(self, query: str, max_results: int = 30) -> List[Dict]:
        """Fetch recent IG media captions via Graph API and filter by query.
        Requires a long-lived INSTAGRAM_ACCESS_TOKEN connected to an IG Business/Creator account.
        """
        access_token_tuple = self.key_manager.get_available_key('instagram')
        access_token = None
        if isinstance(access_token_tuple, (list, tuple)) and len(access_token_tuple) >= 3:
            access_token = access_token_tuple[2]
        elif isinstance(access_token_tuple, str):
            access_token = access_token_tuple

        if not access_token:
            return self._get_demo_data()

        try:
            # Prefer explicit Instagram Business/Creator user id if provided
            ig_user_id = os.getenv('INSTAGRAM_USER_ID')
            endpoint = f"{self.base_url}/{ig_user_id}/media" if ig_user_id else f"{self.base_url}/me/media"
            params = {
                'fields': 'caption,permalink,timestamp,username',
                'access_token': access_token,
                'limit': min(max_results, 50)
            }
            resp = requests.get(endpoint, params=params, timeout=20)
            if resp.status_code != 200:
                return self._get_demo_data()
            data = resp.json()
            items = []
            for m in data.get('data', []):
                caption = m.get('caption') or ''
                if query.lower() in caption.lower():
                    items.append({
                        'platform': 'Instagram',
                        'content': caption,
                        'author': m.get('username', 'Unknown'),
                        'id': m.get('id', ''),
                        'timestamp': m.get('timestamp', datetime.now().isoformat()),
                        'url': m.get('permalink', '')
                    })
                if len(items) >= max_results:
                    break
            return items if items else self._get_demo_data()
        except Exception:
            return self._get_demo_data()

    def _get_demo_data(self) -> List[Dict]:
        return [
            {
                'platform': 'Instagram',
                'content': 'Awareness post against misinformation targeting India. Stay informed. #StopPropaganda',
                'author': 'ig_demo_user',
                'id': 'demo_ig_1',
                'timestamp': datetime.now().isoformat(),
                'url': 'https://instagram.com/p/demo1'
            }
        ]


