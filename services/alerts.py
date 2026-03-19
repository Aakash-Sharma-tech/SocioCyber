import requests
from typing import Dict
import time
from datetime import datetime

class AlertService:
    def __init__(self, key_manager):
        self.key_manager = key_manager
        self.alert_history = []
        
    def send_alert(self, message: str, severity: str = 'medium', alert_type: str = 'propaganda'):
        """Send alert via multiple channels"""
        try:
            # Send SMS via Twilio
            self._send_sms_alert(message, severity)
            
            # Log alert
            alert_data = {
                'message': message,
                'severity': severity,
                'type': alert_type,
                'timestamp': datetime.now().isoformat()
            }
            self.alert_history.append(alert_data)
            
            # Keep only last 100 alerts in memory
            if len(self.alert_history) > 100:
                self.alert_history = self.alert_history[-100:]
            
            print(f"ALERT [{severity.upper()}]: {message}")
            return True
            
        except Exception as e:
            print(f"Error sending alert: {str(e)}")
            return False
    
    def _send_sms_alert(self, message: str, severity: str):
        """Send SMS alert via Twilio"""
        try:
            # For demo purposes, we'll simulate SMS sending
            # In production, integrate with actual Twilio API
            
            twilio_sid = self.key_manager.api_keys.get('twilio', {}).get('sid')
            twilio_token = self.key_manager.api_keys.get('twilio', {}).get('token')
            twilio_phone = self.key_manager.api_keys.get('twilio', {}).get('phone')
            
            if not all([twilio_sid, twilio_token, twilio_phone]):
                print("SMS Alert (Simulated):", message)
                return
            
            # Actual Twilio implementation would go here
            # For now, just log the alert
            print(f"SMS Alert [{severity}]: {message}")
            
        except Exception as e:
            print(f"Error sending SMS: {str(e)}")
    
    def _send_telegram_alert(self, message: str):
        """Send alert via Telegram bot"""
        # Placeholder for Telegram integration
        print(f"Telegram Alert: {message}")
    
    def get_recent_alerts(self, limit: int = 10) -> list:
        """Get recent alerts"""
        return self.alert_history[-limit:] if self.alert_history else []
    
    def check_alert_conditions(self, analysis_data: Dict) -> bool:
        """Check if conditions warrant an alert"""
        try:
            # High propaganda score
            if analysis_data.get('propaganda_score', 0) > 0.8:
                self.send_alert(
                    f"High propaganda activity detected (Score: {analysis_data['propaganda_score']:.2f})",
                    severity='high',
                    alert_type='propaganda'
                )
                return True
            
            # High toxicity
            if analysis_data.get('toxicity_score', 0) > 0.9:
                self.send_alert(
                    f"High toxicity content detected (Score: {analysis_data['toxicity_score']:.2f})",
                    severity='high',
                    alert_type='toxicity'
                )
                return True
            
            # Coordinated negative sentiment
            if analysis_data.get('negative_sentiment_ratio', 0) > 0.8:
                self.send_alert(
                    f"Unusual negative sentiment spike detected ({analysis_data['negative_sentiment_ratio']:.1%})",
                    severity='medium',
                    alert_type='sentiment'
                )
                return True
            
            return False
            
        except Exception as e:
            print(f"Error checking alert conditions: {str(e)}")
            return False