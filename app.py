from flask import Flask, render_template, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from config import Config
import os
from datetime import datetime
from services.twitter_client import TwitterClient
from services.reddit_client import RedditClient
from services.news_client import NewsClient
from services.analyzer import AnalysisService
from services.key_manager import APIKeyManager
from services.alerts import AlertService
from services.instagram_client import InstagramClient
from services.facebook_client import FacebookClient
from services.telegram_client import TelegramClient
from models.db_models import db, Post, Analysis, History, User

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Ensure database directory exists before initializing SQLAlchemy/connecting
    try:
        db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
        print(f"[Startup] SQLALCHEMY_DATABASE_URI = {db_uri}")
        if db_uri.startswith('sqlite:///'):
            # Extract filesystem path from URI
            db_path = db_uri.replace('sqlite:///','')
            # Handle absolute Windows paths produced by Path.as_posix(), e.g. /E:/...
            if os.name == 'nt' and len(db_path) > 2 and db_path[0] == '/' and db_path[2] == ':':
                db_path = db_path[1:]
            db_dir = os.path.dirname(db_path)
            if db_dir and not os.path.isdir(db_dir):
                os.makedirs(db_dir, exist_ok=True)
            # Try to create the file if it doesn't exist to validate the path is writable
            try:
                if not os.path.exists(db_path):
                    with open(db_path, 'a', encoding='utf-8'):
                        pass
            except Exception as f_err:
                print(f"[Startup] Failed to pre-create SQLite file at {db_path}: {f_err}")
    except Exception as e:
        print(f"[Startup] DB path preparation error: {e}")
        # Non-fatal; SQLAlchemy will raise a clearer error if it still can't open
        pass

    # Initialize database
    db.init_app(app)

    # Create tables at app startup
    with app.app_context():
        db.create_all()
    
    # Initialize services
    api_manager = APIKeyManager()
    twitter_client = TwitterClient(api_manager)
    reddit_client = RedditClient(api_manager)
    news_client = NewsClient(api_manager)
    instagram_client = InstagramClient(api_manager)
    facebook_client = FacebookClient(api_manager)
    telegram_client = TelegramClient(api_manager)
    analyzer = AnalysisService(api_manager)
    alert_service = AlertService(api_manager)
    
    def parse_timestamp(value: str):
        try:
            if not value:
                return datetime.now()
            # Handle RFC3339 'Z' suffix
            if value.endswith('Z'):
                value = value.replace('Z', '+00:00')
            return datetime.fromisoformat(value)
        except Exception:
            try:
                # Fallback to current time if unparsable
                return datetime.now()
            except Exception:
                return datetime.now()
    
    @app.route('/')
    def dashboard():
        return render_template('dashboard.html')
    
    @app.route('/insights')
    def insights():
        return render_template('insights.html')
    
    @app.route('/visualization')
    def visualization():
        return render_template('visualization.html')
    
    @app.route('/history')
    def history():
        return render_template('history.html')
    
    @app.route('/chatbot')
    def chatbot():
        return render_template('chatbot.html')
    
    @app.route('/api/collect-data', methods=['POST'])
    def collect_data():
        try:
            query = request.json.get('query', 'anti-india propaganda')
            
            # Collect data from all sources
            twitter_data = twitter_client.fetch_posts(query)
            reddit_data = reddit_client.fetch_posts(query)
            news_data = news_client.fetch_articles(query)
            instagram_data = instagram_client.fetch_posts(query)
            facebook_data = facebook_client.fetch_posts(query)
            telegram_data = telegram_client.fetch_posts(query)
            
            all_posts = twitter_data + reddit_data + news_data + instagram_data + facebook_data + telegram_data
            # Filter out demo items so we don't persist placeholders
            def is_demo(item):
                demo_id = item.get('id', '')
                return isinstance(demo_id, str) and demo_id.startswith('demo')
            real_posts = [p for p in all_posts if not is_demo(p)]
            
            # Analyze each post
            analyzed_posts = []
            for post_data in real_posts:
                # Store raw post
                post = Post(
                    platform=post_data['platform'],
                    content=post_data['content'],
                    author=post_data.get('author', 'Unknown'),
                    post_id=post_data.get('id', ''),
                    timestamp=parse_timestamp(post_data.get('timestamp', datetime.now().isoformat())),
                    url=post_data.get('url', '')
                )
                db.session.add(post)
                db.session.flush()  # Get the ID
                
                # Analyze post
                analysis_result = analyzer.analyze_post(post_data['content'])
                
                analysis = Analysis(
                    post_id=post.id,
                    sentiment=analysis_result['sentiment'],
                    emotion=analysis_result['emotion'],
                    toxicity_score=analysis_result['toxicity'],
                    propaganda_score=analysis_result['propaganda'],
                    keywords=','.join(analysis_result['keywords']),
                    language=analysis_result['language'],
                    translation=analysis_result.get('translation', '')
                )
                db.session.add(analysis)
                
                analyzed_posts.append({
                    'post': post_data,
                    'analysis': analysis_result
                })
            
            db.session.commit()
            
            # Check for alerts
            high_risk_posts = [p for p in analyzed_posts if p['analysis']['propaganda'] > 0.7]
            if high_risk_posts:
                alert_service.send_alert(f"High propaganda activity detected: {len(high_risk_posts)} posts")
            
            return jsonify({
                'success': True,
                'posts_collected': len(real_posts),
                'high_risk_posts': len(high_risk_posts),
                'data': analyzed_posts[:10]  # Return first 10 for preview
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/dashboard-stats')
    def dashboard_stats():
        try:
            # Get recent analyses
            recent_analyses = db.session.query(Analysis).join(Post).filter(
                Post.timestamp >= datetime.now().replace(hour=0, minute=0, second=0)
            ).all()
            
            if not recent_analyses:
                # Return demo data if no real data
                return jsonify({
                    'total_posts': 150,
                    'propaganda_percentage': 23,
                    'negative_sentiment': 45,
                    'suspicious_posts': 34,
                    'sentiment_distribution': {
                        'positive': 30,
                        'neutral': 25,
                        'negative': 45
                    },
                    'platform_activity': {
                        'Twitter': 80,
                        'Reddit': 45,
                        'News': 25
                    }
                })
            
            total_posts = len(recent_analyses)
            propaganda_posts = sum(1 for a in recent_analyses if a.propaganda_score > 0.5)
            negative_posts = sum(1 for a in recent_analyses if a.sentiment == 'negative')
            suspicious_posts = sum(1 for a in recent_analyses if a.toxicity_score > 0.6)
            
            sentiment_counts = {'positive': 0, 'neutral': 0, 'negative': 0}
            platform_counts = {'Twitter': 0, 'Reddit': 0, 'News': 0}
            
            for analysis in recent_analyses:
                sentiment_counts[analysis.sentiment] = sentiment_counts.get(analysis.sentiment, 0) + 1
                platform_counts[analysis.post.platform] = platform_counts.get(analysis.post.platform, 0) + 1
            
            return jsonify({
                'total_posts': total_posts,
                'propaganda_percentage': round((propaganda_posts / total_posts) * 100, 1) if total_posts > 0 else 0,
                'negative_sentiment': round((negative_posts / total_posts) * 100, 1) if total_posts > 0 else 0,
                'suspicious_posts': suspicious_posts,
                'sentiment_distribution': sentiment_counts,
                'platform_activity': platform_counts
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/recent-posts')
    def recent_posts():
        try:
            limit = int(request.args.get('limit', 20))
            # Most recent posts with their analysis
            posts = db.session.query(Post, Analysis).join(Analysis, Analysis.post_id == Post.id).order_by(Post.timestamp.desc()).limit(limit).all()
            items = []
            for post, analysis in posts:
                items.append({
                    'id': post.id,
                    'platform': post.platform,
                    'author': post.author,
                    'content': post.content,
                    'timestamp': post.timestamp.isoformat() if post.timestamp else None,
                    'url': post.url,
                    'analysis': {
                        'sentiment': analysis.sentiment,
                        'emotion': analysis.emotion,
                        'toxicity': analysis.toxicity_score,
                        'propaganda': analysis.propaganda_score,
                        'keywords': analysis.keywords.split(',') if analysis.keywords else []
                    }
                })
            return jsonify(items)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/insights-data')
    def insights_data():
        try:
            # Pull recent analyses (last 7 days)
            from datetime import timedelta
            since = datetime.now() - timedelta(days=7)
            records = db.session.query(Analysis, Post).join(Post, Post.id == Analysis.post_id).filter(Post.timestamp >= since).all()
            if not records:
                return jsonify({
                    'summary': 'No recent analyses available yet. Collect data to generate AI insights.',
                    'message_similarity': 0,
                    'coordinated_accounts': 0,
                    'active_campaigns': 0,
                    'sentiment': {'positive': 0, 'neutral': 0, 'negative': 0},
                    'emotions': {'anger': 0, 'fear': 0, 'sadness': 0, 'joy': 0},
                    'threat': {'score': 0.0, 'label': 'LOW'},
                    'keywords': [],
                    'languages': {'en': 0, 'hi': 0, 'other': 0},
                    'updated_at': datetime.now().isoformat()
                })

            # Aggregations
            sentiment_counts = {'positive': 0, 'neutral': 0, 'negative': 0}
            emotion_counts = {}
            language_counts = {}
            keyword_freq = {}
            author_suspicious_counts = {}
            propaganda_scores = []

            for analysis, post in records:
                sentiment_counts[analysis.sentiment] = sentiment_counts.get(analysis.sentiment, 0) + 1
                emotion_counts[analysis.emotion] = emotion_counts.get(analysis.emotion, 0) + 1
                language_counts[analysis.language or 'en'] = language_counts.get(analysis.language or 'en', 0) + 1
                if analysis.keywords:
                    for kw in (k.strip() for k in analysis.keywords.split(',') if k.strip()):
                        keyword_freq[kw] = keyword_freq.get(kw, 0) + 1
                propaganda_scores.append(analysis.propaganda_score or 0.0)
                # Count suspicious posts per author (propaganda > 0.6)
                if (analysis.propaganda_score or 0.0) > 0.6:
                    author = post.author or 'Unknown'
                    author_suspicious_counts[author] = author_suspicious_counts.get(author, 0) + 1

            total = len(records)
            # Message similarity proxy: concentration of top keywords
            top_keywords = sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True)[:10]
            top_total = sum(freq for _, freq in top_keywords)
            message_similarity = round((top_total / max(1, sum(keyword_freq.values()))) * 100, 1) if keyword_freq else 0

            # Coordinated accounts: authors with >= 3 suspicious posts
            coordinated_accounts = sum(1 for c in author_suspicious_counts.values() if c >= 3)
            coordinated_authors = sorted(
                (
                    {'author': a, 'count': c}
                    for a, c in author_suspicious_counts.items() if c >= 3
                ),
                key=lambda x: x['count'],
                reverse=True
            )[:15]

            # Active campaigns proxy: keywords that appear in >= 5 posts
            active_campaigns = sum(1 for _, freq in keyword_freq.items() if freq >= 5)

            # Threat score: average propaganda scaled to 0-10
            avg_propaganda = (sum(propaganda_scores) / len(propaganda_scores)) if propaganda_scores else 0.0
            threat_score_10 = round(avg_propaganda * 10, 1)
            if avg_propaganda > 0.7:
                threat_label = 'HIGH'
            elif avg_propaganda > 0.4:
                threat_label = 'MEDIUM'
            else:
                threat_label = 'LOW'

            # Emotions reduced to key set
            emotions_map = {k: emotion_counts.get(k, 0) for k in ['anger', 'fear', 'sadness', 'joy']}

            # Languages reduced
            en = language_counts.get('en', 0)
            hi = language_counts.get('hi', 0)
            other = max(0, sum(language_counts.values()) - en - hi)

            return jsonify({
                'summary': 'Insights generated from recent analyzed posts.',
                'message_similarity': message_similarity,
                'coordinated_accounts': coordinated_accounts,
                'coordinated_authors': coordinated_authors,
                'active_campaigns': active_campaigns,
                'sentiment': sentiment_counts,
                'emotions': emotions_map,
                'threat': {'score': threat_score_10, 'label': threat_label},
                'keywords': [{'text': k, 'count': f} for k, f in top_keywords],
                'languages': {'en': en, 'hi': hi, 'other': other},
                'updated_at': datetime.now().isoformat()
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/chat', methods=['POST'])
    def chat():
        try:
            message = request.json.get('message')
            response = analyzer.chat_response(message)
            return jsonify({'response': response})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/3d-data')
    def get_3d_data():
        try:
            # Get recent analyses for 3D visualization
            analyses = db.session.query(Analysis).join(Post).limit(100).all()
            
            if not analyses:
                # Return demo 3D data
                import random
                demo_data = []
                emotions = ['joy', 'anger', 'fear', 'sadness', 'surprise']
                sentiments = ['positive', 'neutral', 'negative']
                
                for i in range(50):
                    demo_data.append({
                        'x': random.uniform(-1, 1),  # sentiment score
                        'y': random.uniform(0, 1),   # emotion intensity
                        'z': random.uniform(0, 1),   # propaganda score
                        'size': random.randint(5, 20),
                        'color': random.choice(['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#fcea2b']),
                        'platform': random.choice(['Twitter', 'Reddit', 'News']),
                        'emotion': random.choice(emotions),
                        'sentiment': random.choice(sentiments)
                    })
                return jsonify(demo_data)
            
            data_points = []
            for analysis in analyses:
                sentiment_score = {'positive': 1, 'neutral': 0, 'negative': -1}.get(analysis.sentiment, 0)
                
                data_points.append({
                    'x': sentiment_score,
                    'y': analysis.toxicity_score,
                    'z': analysis.propaganda_score,
                    'size': len(analysis.keywords.split(',')) * 3 if analysis.keywords else 10,
                    'color': '#ff6b6b' if analysis.propaganda_score > 0.7 else '#4ecdc4',
                    'platform': analysis.post.platform,
                    'emotion': analysis.emotion,
                    'sentiment': analysis.sentiment
                })
            
            return jsonify(data_points)
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/history-data')
    def history_data():
        try:
            from datetime import timedelta
            since = datetime.now() - timedelta(days=30)

            # Fetch flagged posts (propaganda_score > 0.5)
            flagged = db.session.query(Analysis, Post).join(Post, Post.id == Analysis.post_id).\
                filter(Analysis.propaganda_score > 0.5, Post.timestamp >= since).\
                order_by(Post.timestamp.desc()).limit(200).all()

            flagged_items = []
            for analysis, post in flagged:
                flagged_items.append({
                    'id': post.id,
                    'platform': post.platform,
                    'author': post.author,
                    'content': post.content,
                    'timestamp': post.timestamp.isoformat() if post.timestamp else None,
                    'url': post.url,
                    'scores': {
                        'propaganda': analysis.propaganda_score,
                        'toxicity': analysis.toxicity_score
                    },
                    'sentiment': analysis.sentiment,
                    'emotion': analysis.emotion
                })

            # Build daily aggregates for trends
            records = db.session.query(Analysis, Post).join(Post, Post.id == Analysis.post_id).\
                filter(Post.timestamp >= since).all()

            from collections import defaultdict
            day_buckets = {}
            def day_key(dt):
                return (dt or datetime.now()).strftime('%Y-%m-%d')

            platforms_seen = set()
            for analysis, post in records:
                key = day_key(post.timestamp)
                if key not in day_buckets:
                    day_buckets[key] = {
                        'propaganda_sum': 0.0,
                        'count': 0,
                        'sentiment': defaultdict(int),
                        'platform': defaultdict(int)
                    }
                b = day_buckets[key]
                b['propaganda_sum'] += (analysis.propaganda_score or 0.0)
                b['count'] += 1
                b['sentiment'][analysis.sentiment or 'neutral'] += 1
                platform_name = post.platform or 'Unknown'
                b['platform'][platform_name] += 1
                platforms_seen.add(platform_name)

            # Sort by date
            labels = sorted(day_buckets.keys())
            propaganda_avg = []
            sent_pos, sent_neg, sent_neu = [], [], []
            platform_series = {p: [] for p in sorted(platforms_seen)}
            for label in labels:
                b = day_buckets[label]
                c = max(1, b['count'])
                propaganda_avg.append(round(b['propaganda_sum'] / c, 2))
                sent_pos.append(b['sentiment'].get('positive', 0))
                sent_neg.append(b['sentiment'].get('negative', 0))
                sent_neu.append(b['sentiment'].get('neutral', 0))
                for p in platform_series.keys():
                    platform_series[p].append(b['platform'].get(p, 0))

            return jsonify({
                'flagged': flagged_items,
                'trends': {
                    'labels': labels,
                    'propaganda_avg': propaganda_avg,
                    'sentiment': {
                        'positive': sent_pos,
                        'negative': sent_neg,
                        'neutral': sent_neu
                    },
                    'platform': platform_series
                }
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/diagnostics')
    def diagnostics():
        try:
            keys = {
                'twitter_bearer': bool(os.environ.get('TWITTER_BEARER_TOKEN')),
                'reddit_client_id': bool(os.environ.get('REDDIT_CLIENT_ID')),
                'reddit_client_secret': bool(os.environ.get('REDDIT_CLIENT_SECRET')),
                'news_api_key': bool(os.environ.get('NEWS_API_KEY'))
            }
            # Count rows to ensure DB is writable
            post_count = db.session.query(Post).count()
            analysis_count = db.session.query(Analysis).count()
            return jsonify({'keys_present': keys, 'db': {'posts': post_count, 'analyses': analysis_count}})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/source-status')
    def source_status():
        results = {}
        try:
            # Twitter test
            try:
                t = twitter_client.fetch_posts('india', max_results=5)
                results['twitter'] = {'count': len(t), 'demo': all(str(it.get('id','')).startswith('demo') for it in t)}
            except Exception as e:
                results['twitter'] = {'error': str(e)}
            # Reddit test
            try:
                r = reddit_client.fetch_posts('india', max_results=5)
                results['reddit'] = {'count': len(r), 'demo': all(str(it.get('id','')).startswith('demo') for it in r)}
            except Exception as e:
                results['reddit'] = {'error': str(e)}
            # News test
            try:
                n = news_client.fetch_articles('india', max_results=5)
                results['news'] = {'count': len(n), 'demo': all(str(it.get('id','')).startswith('demo') for it in n)}
            except Exception as e:
                results['news'] = {'error': str(e)}
            # Instagram
            try:
                ig = instagram_client.fetch_posts('india', max_results=5)
                results['instagram'] = {'count': len(ig), 'demo': all(str(it.get('id','')).startswith('demo') for it in ig)}
            except Exception as e:
                results['instagram'] = {'error': str(e)}
            # Facebook
            try:
                fb = facebook_client.fetch_posts('india', max_results=5)
                results['facebook'] = {'count': len(fb), 'demo': all(str(it.get('id','')).startswith('demo') for it in fb)}
            except Exception as e:
                results['facebook'] = {'error': str(e)}
            # Telegram
            try:
                tg = telegram_client.fetch_posts('india', max_results=5)
                results['telegram'] = {'count': len(tg), 'demo': all(str(it.get('id','')).startswith('demo') for it in tg)}
            except Exception as e:
                results['telegram'] = {'error': str(e)}
            return jsonify(results)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return app

if __name__ == '__main__':
# if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5001)