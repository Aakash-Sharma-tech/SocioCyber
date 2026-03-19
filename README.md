# SocioCyber

A comprehensive social media monitoring and analysis platform that integrates multiple social networks to provide real-time insights, threat detection, and sentiment analysis.

## Features

- **Multi-Platform Integration**: Connect to Twitter, Facebook, Instagram, Reddit, Telegram, and news sources
- **Real-Time Monitoring**: Track mentions, keywords, and trends across platforms
- **Sentiment Analysis**: Analyze sentiment and emotional context of social media content
- **Threat Detection & Alerts**: Automated alert system for suspicious activities and security threats
- **Interactive Dashboard**: Visual analytics and insights from social media data
- **AI-Powered Chatbot**: Conversational interface for querying and analyzing data
- **Content History**: Track and manage historical data for trend analysis

## Tech Stack

### Backend
- **Framework**: Flask (Python)
- **Database**: SQLAlchemy ORM
- **Key Libraries**: 
  - Social media APIs (Twitter, Facebook, Instagram, Reddit, Telegram)
  - News aggregation APIs
  - Sentiment analysis and NLP

### Frontend
- **HTML/CSS/JavaScript**: Interactive web interface
- **Dashboard**: Real-time data visualization
- **Chatbot Interface**: Conversational UI

## Project Structure

```
├── app.py                    # Flask application entry point
├── config.py                 # Configuration settings
├── package.json              # JavaScript dependencies
├── test.py                   # Testing suite
├── models/
│   └── db_models.py         # Database models and schemas
├── services/
│   ├── alerts.py            # Alert management system
│   ├── analyzer.py          # Data analysis and sentiment analysis
│   ├── facebook_client.py    # Facebook API integration
│   ├── instagram_client.py   # Instagram API integration
│   ├── key_manager.py        # API key management
│   ├── news_client.py        # News aggregation
│   ├── reddit_client.py      # Reddit API integration
│   ├── telegram_client.py    # Telegram API integration
│   └── twitter_client.py     # Twitter API integration
├── static/
│   ├── css/
│   │   └── main.css         # Main stylesheet
│   └── js/
│       ├── chatbot.js       # Chatbot functionality
│       └── dashboard.js     # Dashboard interactions
├── templates/
│   ├── base.html            # Base template
│   ├── chatbot.html         # Chatbot interface
│   ├── dashboard.html       # Main dashboard
│   ├── history.html         # Data history view
│   ├── insights.html        # Analytics insights
│   └── visualization.html   # Data visualization
├── data/                    # Data storage
└── instance/                # Instance-specific files
```

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Aakash-Sharma-tech/SocioCyber.git
   cd SocioCyber
   ```

2. **Create a virtual environment** (Python)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   npm install
   ```

4. **Configure API Keys**
   - Copy `config.py` and add your API keys for:
     - Twitter API
     - Facebook Graph API
     - Instagram API
     - Reddit API
     - Telegram Bot Token
     - News API
   - Update the configuration with your credentials

5. **Initialize the database**
   ```bash
   python
   >>> from app import app, db
   >>> with app.app_context():
   ...     db.create_all()
   ```

## Usage

1. **Start the Flask server**
   ```bash
   python app.py
   ```

2. **Access the application**
   - Open your browser and navigate to `http://localhost:5000`
   - Use the dashboard to monitor social media
   - Chat with the AI-powered chatbot for insights
   - View analytics and configure alerts

3. **Monitor social media**
   - Add keywords or accounts to monitor
   - Set up alerts for specific threats or mentions
   - View real-time sentiment analysis
   - Access historical data and trends

## Configuration

Update `config.py` with the following:

```python
# API Keys
TWITTER_API_KEY = "your_api_key"
TWITTER_API_SECRET = "your_api_secret"
TWITTER_BEARER_TOKEN = "your_bearer_token"

FACEBOOK_ACCESS_TOKEN = "your_access_token"
INSTAGRAM_ACCESS_TOKEN = "your_access_token"
REDDIT_CLIENT_ID = "your_client_id"
REDDIT_SECRET = "your_secret"
TELEGRAM_TOKEN = "your_bot_token"
NEWS_API_KEY = "your_news_api_key"

# Database
DATABASE_URL = "sqlite:///sociocyber.db"

# Flask
SECRET_KEY = "your_secret_key"
DEBUG = False
```

## Testing

Run the test suite:
```bash
python test.py
```

## Modules Overview

### Services
- **alerts.py**: Manages alert generation and notifications
- **analyzer.py**: Performs sentiment analysis and data processing
- **key_manager.py**: Securely manages API credentials
- **[platform]_client.py**: Platform-specific API integrations

### Models
- **db_models.py**: Defines database schemas for users, posts, alerts, and analytics

## Security Considerations

- Store API keys in environment variables or secure configuration
- Validate user input to prevent injection attacks
- Implement rate limiting on API endpoints
- Use HTTPS in production
- Regularly update dependencies

## Future Enhancements

- Machine learning models for threat prediction
- Advanced anomaly detection
- Multi-language support
- Custom alert rules and workflows
- Export reports in multiple formats
- Mobile application

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues, questions, or contributions, please open an issue on the GitHub repository.

## Authors

- Aakash Sharma - Initial development

## Acknowledgments

- Thank you to all API providers (Twitter, Facebook, Instagram, Reddit, Telegram, News APIs)
- Community contributions and feedback
