# app/utils/session_manager.py
from datetime import datetime, timedelta

class SessionManager:
    def __init__(self):
        self.sessions = {}

    def get_user_step(self, user_id):
        session = self.sessions.get(user_id)
        if session:
            step, last_message_time = session
            # Check if the last message was sent more than 3 minutes ago
            if datetime.now() - last_message_time > timedelta(minutes=3):
                return 'start'  # Reset to start if idle time exceeded
            return step
        return 'start'  # Default to 'start' if no session exists

    def set_user_step(self, user_id, step):
        # Store both step and current timestamp
        self.sessions[user_id] = (step, datetime.now())
        
    def reset_user_step(self, user_id):
        self.sessions[user_id] = ('start', datetime.now())

def get_user_id(data):
    # Extract user ID from webhook data (e.g., from phone number or unique ID)
    return data.get('from')  # Adjust based on actual WhatsApp webhook data
