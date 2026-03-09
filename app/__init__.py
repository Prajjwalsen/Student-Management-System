# app/__init__.py
from flask import Flask
from flask_cors import CORS
from .database import init_database
from .routes import register_routes
import os

def create_app():
    app = Flask(__name__, 
                template_folder=os.path.join(os.path.dirname(__file__), '..', 'templates'),
                static_folder=os.path.join(os.path.dirname(__file__), '..', 'static'))
    app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

    # Enable CORS
    CORS(app)

    # Initialize database
    init_database()

    # Register routes
    register_routes(app)

    return app