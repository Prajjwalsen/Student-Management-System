# config.py
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    DATABASE = 'database.db'
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    PORT = int(os.environ.get('PORT', 5000))

    # Flask reloader settings to reduce unnecessary reloads
    TEMPLATES_AUTO_RELOAD = True
    # Disable file watching for certain directories to reduce reload triggers
    # This can be configured in the run command