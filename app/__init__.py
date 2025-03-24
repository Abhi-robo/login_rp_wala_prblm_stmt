"""Flask application initialization."""
from flask import Flask
from flask_login import LoginManager

from.routes import app_routes
from.routes.auth import auth_bp

from.pages.introduction import introduction_bp # Import the new Blueprint

from.pages.conclusion import conclusion_bp

from.pages.discussion import discussion_bp

from.pages.methods import methods_bp

from.pages.results import results_bp

from.pages.features import features_bp

from.pages.manuscript import manuscript_bp

from.models.user import User

import os

from dotenv import load_dotenv

import secrets

def create_app():
    # Load environment variables from the .env file
    load_dotenv()

    # Create the Flask app instance
    app = Flask(__name__)

    # Load SECRET_KEY from the environment or generate a secure fallback for development
    app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))

    # Raise an error if no secret key is set in a production environment
    if not app.secret_key and os.environ.get('FLASK_ENV') == 'production':
        raise ValueError("No SECRET_KEY set for Flask application in production.")

    # Set session settings
    app.config['SESSION_TYPE'] = 'filesystem'  # Store sessions in the filesystem
    app.config['SESSION_PERMANENT'] = True

    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        return User.get_by_id(user_id)

    # Register the blueprints
    app.register_blueprint(app_routes)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(introduction_bp, url_prefix='/introduction')
    app.register_blueprint(methods_bp, url_prefix='/methods')
    app.register_blueprint(discussion_bp, url_prefix='/discussion')
    app.register_blueprint(conclusion_bp, url_prefix='/conclusion')
    app.register_blueprint(results_bp, url_prefix='/results')
    app.register_blueprint(features_bp, url_prefix='/features')
    app.register_blueprint(manuscript_bp, url_prefix='/manuscript')

    return app