from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False)

class Post(db.Model):
    __tablename__ = 'posts'
    
    id = db.Column(db.Integer, primary_key=True)
    platform = db.Column(db.String(50), nullable=False)  # Twitter, Reddit, News
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(100))
    post_id = db.Column(db.String(200))  # Original platform post ID
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    analyses = db.relationship('Analysis', backref='post', lazy=True, cascade='all, delete-orphan')

class Analysis(db.Model):
    __tablename__ = 'analyses'
    
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    
    # Analysis results
    sentiment = db.Column(db.String(20))  # positive, negative, neutral
    emotion = db.Column(db.String(50))    # joy, anger, fear, sadness, etc.
    toxicity_score = db.Column(db.Float)  # 0.0 to 1.0
    propaganda_score = db.Column(db.Float)  # 0.0 to 1.0
    keywords = db.Column(db.Text)  # Comma-separated keywords
    language = db.Column(db.String(10))  # Language code
    translation = db.Column(db.Text)  # English translation if needed
    
    # AI model info
    ai_model_used = db.Column(db.String(100))  # Which AI model was used
    confidence_score = db.Column(db.Float)  # Model confidence
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class History(db.Model):
    __tablename__ = 'history'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    
    # Daily aggregated stats
    total_posts = db.Column(db.Integer, default=0)
    propaganda_posts = db.Column(db.Integer, default=0)
    negative_sentiment_posts = db.Column(db.Integer, default=0)
    high_toxicity_posts = db.Column(db.Integer, default=0)
    
    # Platform breakdown
    twitter_posts = db.Column(db.Integer, default=0)
    reddit_posts = db.Column(db.Integer, default=0)
    news_posts = db.Column(db.Integer, default=0)
    
    # Average scores
    avg_propaganda_score = db.Column(db.Float)
    avg_toxicity_score = db.Column(db.Float)
    avg_sentiment_score = db.Column(db.Float)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Alert(db.Model):
    __tablename__ = 'alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    alert_type = db.Column(db.String(50))  # propaganda, toxicity, volume
    message = db.Column(db.Text)
    severity = db.Column(db.String(20))  # low, medium, high, critical
    triggered_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)