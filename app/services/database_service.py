import os
import re
import uuid
import mysql.connector
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime
import logging

load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Connect to MySQL database
def connect_db():
    try:
        conn = mysql.connector.connect(
            host=os.getenv("MYSQL_HOST"),
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            port=3306
        )
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {os.getenv('MYSQL_DATABASE_NAME')}")
        conn.database = os.getenv('MYSQL_DATABASE_NAME')
        
        # Create users table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                email VARCHAR(255) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                name VARCHAR(255) NOT NULL,
                created_at DATETIME NOT NULL,
                INDEX idx_email (email)
            )
        """)
        
        # Create file_ids_mapping table if it doesn't exist
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {os.getenv('MYSQL_TABLE_NAME')} (
                id INT AUTO_INCREMENT PRIMARY KEY,
                file_name VARCHAR(255) NOT NULL,
                file_id VARCHAR(255) NOT NULL,
                vector_id VARCHAR(255) NOT NULL,
                vector_store_name VARCHAR(255) NOT NULL,
                vector_store_file_id VARCHAR(255) NOT NULL,
                assistant_id VARCHAR(255),
                user_id INT,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        conn.commit()
        return conn
    except mysql.connector.Error as err:
        logger.error(f"Database connection error: {err}")
        raise

def create_user(email, password_hash, name):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        created_at = datetime.utcnow()
        
        cursor.execute(
            "INSERT INTO users (email, password_hash, name, created_at) VALUES (%s, %s, %s, %s)",
            (email, password_hash, name, created_at)
        )
        user_id = cursor.lastrowid
        conn.commit()
        return user_id
    except mysql.connector.Error as err:
        logger.error(f"Error creating user: {err}")
        raise
    finally:
        conn.close()

def get_user_by_id(user_id):
    try:
        conn = connect_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        return cursor.fetchone()
    finally:
        conn.close()

def get_user_by_email(email):
    try:
        conn = connect_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        return cursor.fetchone()
    finally:
        conn.close()

def is_file_uploaded(file_name, user_id):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT COUNT(*), assistant_id FROM {os.getenv('MYSQL_TABLE_NAME')} WHERE file_name = %s AND user_id = %s",
            (file_name, user_id)
        )
        result = cursor.fetchone()
        count = result[0]
        assistant_id = result[1] if result else None
        return count > 0, assistant_id
    finally:
        conn.close()

def save_to_db(file_name, file_id, vector_id, vector_store_name, vector_store_file_id, assistant_id=None, user_id=None):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute(
            f"""
            INSERT INTO {os.getenv('MYSQL_TABLE_NAME')} 
            (file_name, file_id, vector_id, vector_store_name, vector_store_file_id, assistant_id, user_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (file_name, file_id, vector_id, vector_store_name, vector_store_file_id, assistant_id, user_id)
        )
        conn.commit()
    finally:
        conn.close()

def connect_mongo():
    try:
        mongo_client = MongoClient(os.getenv("MONGO_URI"))
        db = mongo_client[os.getenv("MONGO_DATABASE_NAME")]
        return db
    except Exception as e:
        logger.error(f"MongoDB connection error: {e}")
        raise

def save_to_mongo_introduction(db, user_query, assistant_response, citations, file_name, collection_name, user_id):
    """Save user query, assistant response, and citations to a specified MongoDB collection."""
    try:
        collection = db[collection_name]
        entry = {
            "file_name": file_name,
            "user_query": user_query,
            "assistant_response": assistant_response,
            "citations": citations,
            "timestamp": datetime.utcnow(),
            "user_id": str(user_id)
        }
        collection.insert_one(entry)
        logger.info(f"Saved to MongoDB: {user_query[:50]}...")
    except Exception as e:
        logger.error(f"Error saving to MongoDB: {e}")
        raise

def save_to_mongo_outside_sections(db, user_query, assistant_response, citations, file_name, collection_name, user_id):
    """Save user query, assistant response, and citations to a specified MongoDB collection."""
    try:
        collection = db[collection_name]
        entry = {
            "file_name": file_name,
            "user_query": user_query,
            "assistant_response": assistant_response,
            "citations": citations,
            "timestamp": datetime.utcnow(),
            "user_id": str(user_id)
        }
        collection.insert_one(entry)
        logger.info(f"Saved to MongoDB: {user_query[:50]}...")
    except Exception as e:
        logger.error(f"Error saving to MongoDB: {e}")
        raise