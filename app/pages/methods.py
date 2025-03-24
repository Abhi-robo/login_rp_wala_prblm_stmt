import logging
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.services.assistent_chat_service import AssistantSession
from app.services.database_service import *
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

methods_bp = Blueprint('methods_bp', __name__)

@methods_bp.route('/get_methods', methods=['GET'])
@login_required
def get_introductions():
    """Flask endpoint to fetch all introductions from the 'introductions' collection for the current user."""
    try:
        db = connect_mongo()
        # Fetch user-specific data
        introductions_cursor = db['methods'].find(
            {'user_id': str(current_user.id)},
            {'_id': 0, 'user_query': 1, 'assistant_response': 1}
        )
        
        # Convert the cursor to a list of dictionaries
        introductions_list = list(introductions_cursor)
        
        # Return the fetched data as JSON response
        return jsonify(introductions_list), 200
    
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        return jsonify({"error": "An error occurred while fetching introductions"}), 500

@methods_bp.route('/save_outside_methods_chat_response', methods=['POST'])
@login_required
def save_outside_methods_chat_response():
    """Flask endpoint to save user query, assistant response, and citations."""
    try:
        # Get the data from the request
        data = request.get_json()
        
        # Ensure required fields are in the request
        file_name = data.get("file_name")
        user_query = data.get('user_query')
        assistant_response = data.get('assistant_response')
        citations = data.get('citations')
        
        if not user_query or not assistant_response:
            return jsonify({"error": "Missing required fields"}), 400
        
        db = connect_mongo()
        
        # Save to MongoDB with user_id
        save_to_mongo_outside_sections(
            db=db,
            user_query=user_query,
            assistant_response=assistant_response,
            citations=citations,
            file_name=file_name,
            collection_name="methods",
            user_id=current_user.id
        )
        
        return jsonify({"message": "Saved successfully"}), 200
    
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        return jsonify({"error": "An error occurred while saving data"}), 500