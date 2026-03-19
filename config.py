import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Config:
    BASEDIR = Path(__file__).resolve().parent
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    # Build a cross-platform absolute path and normalize to POSIX for SQLAlchemy URI
    _DEFAULT_DB_PATH = (BASEDIR / 'data' / 'database.sqlite').resolve()
    _ENV_DB_URL = os.environ.get('DATABASE_URL')
    if _ENV_DB_URL and _ENV_DB_URL.startswith('sqlite:///'):
        # Normalize any relative sqlite path to absolute under BASEDIR
        _raw_path = _ENV_DB_URL.replace('sqlite:///','')
        # If path looks absolute (drive letter or starts with /<drive>:) leave it; else make absolute
        _path_is_abs = (
            Path(_raw_path).is_absolute() or
            (len(_raw_path) > 2 and _raw_path[1] == ':' and _raw_path[2] == '/') or
            (len(_raw_path) > 3 and _raw_path[0] == '/' and _raw_path[2] == ':' and _raw_path[3] == '/')
        )
        _db_path = Path(_raw_path)
        if not _path_is_abs:
            _db_path = (BASEDIR / _raw_path).resolve()
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{_db_path.as_posix()}"
        _DB_PATH = _db_path
    elif _ENV_DB_URL:
        SQLALCHEMY_DATABASE_URI = _ENV_DB_URL
        _DB_PATH = _DEFAULT_DB_PATH
    else:
        _DB_PATH = _DEFAULT_DB_PATH
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{_DB_PATH.as_posix()}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FLASK_ENV = os.environ.get('FLASK_ENV') or 'development'
    
    # API Keys
    TWITTER_API_KEY = os.environ.get('TWITTER_API_KEY')
    TWITTER_API_SECRET = os.environ.get('TWITTER_API_SECRET')
    TWITTER_BEARER_TOKEN = os.environ.get('TWITTER_BEARER_TOKEN')
    
    REDDIT_CLIENT_ID = os.environ.get('REDDIT_CLIENT_ID')
    REDDIT_CLIENT_SECRET = os.environ.get('REDDIT_CLIENT_SECRET')
    REDDIT_USER_AGENT = os.environ.get('REDDIT_USER_AGENT')
    
    HUGGINGFACEHUB_API_KEY = os.environ.get('HUGGINGFACEHUB_API_KEY')
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    GROQCLOUD_API_KEY = os.environ.get('GROQCLOUD_API_KEY')
    DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY')
    
    TWILIO_SID = os.environ.get('TWILIO_SID')
    TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
    TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER')
    
    GOOGLE_TRANSLATE_KEY = os.environ.get('GOOGLE_TRANSLATE_KEY')
    NEWS_API_KEY = os.environ.get('NEWS_API_KEY')