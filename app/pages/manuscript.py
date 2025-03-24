import os
import uuid
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.services.database_service import (
    connect_db,
    connect_mongo,
    is_file_uploaded,
    save_to_db,
    save_to_mongo_outside_sections
)

manuscript_bp = Blueprint('manuscript_bp', __name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@manuscript_bp.route('/upload', methods=['POST'])
@login_required
def upload_manuscript():
    """Upload a new manuscript file."""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
        
        if not allowed_file(file.filename):
            return jsonify({"error": "File type not allowed"}), 400
        
        filename = secure_filename(file.filename)
        file_id = str(uuid.uuid4())
        vector_id = str(uuid.uuid4())
        
        # Check if file already exists for this user
        exists, _ = is_file_uploaded(filename, current_user.id)
        if exists:
            return jsonify({"error": "File already exists"}), 400
        
        # Save file
        file_path = os.path.join(UPLOAD_FOLDER, file_id + '_' + filename)
        file.save(file_path)
        
        # Save to MySQL
        save_to_db(
            file_name=filename,
            file_id=file_id,
            vector_id=vector_id,
            vector_store_name="manuscript_store",
            vector_store_file_id=file_id,
            user_id=current_user.id
        )
        
        return jsonify({
            "message": "File uploaded successfully",
            "file_id": file_id
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@manuscript_bp.route('/manuscripts', methods=['GET'])
@login_required
def get_manuscripts():
    """Get all manuscripts for the current user."""
    try:
        conn = connect_db()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute(
            f"SELECT file_name, file_id, created_at FROM {os.getenv('MYSQL_TABLE_NAME')} WHERE user_id = %s",
            (current_user.id,)
        )
        
        manuscripts = cursor.fetchall()
        return jsonify(manuscripts), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@manuscript_bp.route('/save-notes', methods=['POST'])
@login_required
def save_manuscript_notes():
    """Save notes or comments about a manuscript."""
    try:
        data = request.get_json()
        file_name = data.get('file_name')
        notes = data.get('notes')
        
        if not file_name or not notes:
            return jsonify({"error": "Missing required fields"}), 400
        
        db = connect_mongo()
        
        save_to_mongo_outside_sections(
            db=db,
            user_query="Save manuscript notes",
            assistant_response=notes,
            citations=[],
            file_name=file_name,
            collection_name="manuscript_notes",
            user_id=current_user.id
        )
        
        return jsonify({"message": "Notes saved successfully"}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@manuscript_bp.route('/notes/<file_name>', methods=['GET'])
@login_required
def get_manuscript_notes(file_name):
    """Get all notes for a specific manuscript."""
    try:
        db = connect_mongo()
        notes = list(db['manuscript_notes'].find(
            {
                'file_name': file_name,
                'user_id': str(current_user.id)
            },
            {
                '_id': 0,
                'assistant_response': 1,
                'timestamp': 1
            }
        ))
        
        return jsonify(notes), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500 