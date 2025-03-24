"""Base routes for the application."""
from flask import Blueprint, jsonify, redirect, url_for
from flask_login import login_required, current_user

# Create the blueprint
app_routes = Blueprint('app_routes', __name__)

@app_routes.route('/')
def index():
    """Home page route."""
    if current_user.is_authenticated:
        return jsonify({
            "message": "Welcome to Manuscript Manager",
            "user": {
                "id": current_user.id,
                "name": current_user.name,
                "email": current_user.email
            }
        })
    return redirect(url_for('auth.login'))

@app_routes.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "message": "Service is running"
    }), 200

@app_routes.route('/profile')
@login_required
def profile():
    """User profile endpoint."""
    return jsonify({
        "user": {
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email
        }
    }) 