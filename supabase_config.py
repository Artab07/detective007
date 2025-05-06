from supabase import create_client
import os
from dotenv import load_dotenv
import numpy as np
import base64
import io
from PIL import Image
import logging

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

def sign_up(email, password, username):
    """Register a new user."""
    try:
        # Create auth user
        response = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": {
                    "username": username
                }
            }
        })
        
        # Add user profile to profiles table
        if response.user:
            supabase.table('profiles').insert({
                'id': response.user.id,
                'username': username,
                'email': email
            }).execute()
            
        return response
    except Exception as e:
        logger.error(f"Error during signup: {str(e)}")
        raise

def sign_in(email, password):
    """Sign in an existing user."""
    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        return response
    except Exception as e:
        logger.error(f"Error during signin: {str(e)}")
        raise

def sign_out():
    """Sign out the current user."""
    try:
        supabase.auth.sign_out()
    except Exception as e:
        logger.error(f"Error during signout: {str(e)}")
        raise

def add_criminal_record(data):
    """Add a new criminal record to the database."""
    try:
        logger.info("Adding criminal record with data: %s", data)
        
        # Validate required fields
        required_fields = ['name', 'face_encoding']
        for field in required_fields:
            if field not in data or not data[field]:
                raise ValueError(f"Missing required field: {field}")
        
        # Insert criminal record
        response = supabase.table('criminal_records').insert(data).execute()
        
        if not response.data:
            logger.error("No data returned from insert operation")
            raise Exception("Failed to add criminal record: No data returned")
            
        logger.info("Criminal record added successfully: %s", response.data)
        return response
        
    except Exception as e:
        logger.error("Error adding criminal record: %s", str(e), exc_info=True)
        raise

def search_criminal_records(face_encoding, tolerance=0.5):
    """Search for criminal records matching the given face encoding."""
    try:
        if isinstance(face_encoding, np.ndarray):
            face_encoding = face_encoding.tobytes()
        response = supabase.table('criminal_records').select('*').execute()
        matches = []
        for record in response.data:
            if record['face_encoding']:
                logger.info(f"face_encoding for {record.get('name', 'Unknown')}: {record['face_encoding']}")
                try:
                    encoding_bytes = base64.b64decode(record['face_encoding'])
                    stored_encoding = np.frombuffer(encoding_bytes, dtype=np.float64)
                except Exception as e:
                    logger.warning(f"Skipping record with invalid face_encoding: {e}")
                    continue
                similarity = calculate_similarity(face_encoding, stored_encoding)
                logger.info(f"Similarity score for {record.get('name', 'Unknown')}: {similarity}")
                if similarity >= tolerance:
                    matches.append({
                        **record,
                        'confidence': float(similarity)
                    })
        matches.sort(key=lambda x: x['confidence'], reverse=True)
        return matches
    except Exception as e:
        logger.error(f"Error searching criminal records: {str(e)}")
        raise

def calculate_similarity(encoding1, encoding2):
    """Calculate similarity between two face encodings."""
    try:
        # Convert bytes to numpy arrays if needed
        if isinstance(encoding1, bytes):
            encoding1 = np.frombuffer(encoding1, dtype=np.float64)
        if isinstance(encoding2, bytes):
            encoding2 = np.frombuffer(encoding2, dtype=np.float64)
        
        # Calculate Euclidean distance
        distance = np.linalg.norm(encoding1 - encoding2)
        
        # Convert distance to similarity score (0-1)
        similarity = 1 / (1 + distance)
        
        return similarity
    except Exception as e:
        logger.error(f"Error calculating similarity: {str(e)}")
        return 0.0

def add_search_history(user_id, search_type, result_count, search_image_url=None):
    """Add a search history record."""
    try:
        supabase.table('search_history').insert({
            'user_id': user_id,
            'search_type': search_type,
            'result_count': result_count,
            'search_image_url': search_image_url
        }).execute()
    except Exception as e:
        logger.error(f"Error adding search history: {str(e)}")
        raise

def get_user_search_history(user_id):
    """Get search history for a user."""
    try:
        response = supabase.table('search_history').select('*').eq('user_id', user_id).order('search_date', desc=True).execute()
        return response.data
    except Exception as e:
        logger.error(f"Error getting search history: {str(e)}")
        raise