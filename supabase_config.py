from supabase import create_client
import os
from dotenv import load_dotenv
import numpy as np
import base64
import io
from PIL import Image
import logging
import face_recognition
from collections import defaultdict
import binascii

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
        logger.info(f"Supabase sign_up response: {response}")
        # Check for error in response
        if hasattr(response, 'error') and response.error:
            logger.error(f"Supabase sign_up error: {response.error}")
            raise Exception(response.error)
        if hasattr(response, 'user') and response.user:
            supabase.table('profiles').insert({
                'id': response.user.id,
                'username': username,
                'email': email
            }).execute()
            return response
        else:
            logger.error(f"Sign up failed, response: {response}")
            raise Exception("Sign up failed. Please check your email and password.")
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
        required_fields = ['name']
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

def search_criminal_records(face_encoding, threshold=0.6):
    """Search for criminal records matching the given face encoding using all encodings in face_encodings table."""
    try:
        # Ensure input encoding is a numpy array of shape (128,) and dtype float64
        if isinstance(face_encoding, bytes):
            face_encoding = np.frombuffer(face_encoding, dtype=np.float64)
        elif isinstance(face_encoding, str):
            face_encoding = np.frombuffer(base64.b64decode(face_encoding), dtype=np.float64)
        elif isinstance(face_encoding, np.ndarray):
            face_encoding = face_encoding.astype(np.float64)
        else:
            raise ValueError("face_encoding must be bytes, str, or numpy array")
        if face_encoding.shape != (128,):
            raise ValueError(f"Input face encoding has invalid shape: {face_encoding.shape}")
        # Fetch all face encodings and join with criminal_records
        encodings_response = supabase.table('face_encodings').select('criminal_id, encoding').execute()
        records_response = supabase.table('criminal_records').select('*').execute()
        if not encodings_response.data or not records_response.data:
            return []
        # Group encodings by criminal_id
        encodings_by_criminal = defaultdict(list)
        for row in encodings_response.data:
            try:
                raw = row['encoding']
                if isinstance(raw, str):
                    encoding_bytes = base64.b64decode(raw)
                else:
                    encoding_bytes = raw
                encoding = np.frombuffer(encoding_bytes, dtype=np.float64)
                if encoding.shape == (128,):
                    encodings_by_criminal[row['criminal_id']].append(encoding)
                else:
                    # Skip invalid encodings
                    continue
            except Exception as e:
                logger.warning(f"Skipping encoding for {row.get('criminal_id', 'unknown')}: {e}")
                continue
        # Find best match
        best_match = None
        best_distance = float('inf')
        for record in records_response.data:
            cid = record['id']
            if cid not in encodings_by_criminal:
                continue
            stored_encodings = encodings_by_criminal[cid]
            if not stored_encodings:
                continue
            # Compute distances
            distances = face_recognition.face_distance(stored_encodings, face_encoding)
            logger.info(f"Distances for {record.get('name', 'Unknown')}: {distances}")
            min_distance = float(np.min(distances)) if len(distances) > 0 else float('inf')
            logger.info(f"Best distance for {record.get('name', 'Unknown')}: {min_distance}")
            if min_distance < best_distance:
                best_distance = min_distance
                best_match = {**record, 'distance': min_distance}
        logger.info(f"Best match: {best_match} with distance {best_distance}")
        if best_match and best_distance < threshold:
            return [best_match]
        else:
            return []
    except Exception as e:
        logger.error(f"Error searching criminal records: {str(e)}")
        raise

def calculate_similarity(encoding1, encoding2):
    """Calculate similarity between two face encodings."""
    try:
        # Convert base64 to numpy arrays if needed
        if isinstance(encoding1, str):
            encoding1 = np.frombuffer(base64.b64decode(encoding1), dtype=np.float64)
        if isinstance(encoding2, str):
            encoding2 = np.frombuffer(base64.b64decode(encoding2), dtype=np.float64)
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

def get_current_user():
    """Return the current authenticated user (or None if not logged in)."""
    try:
        session = supabase.auth.get_session()
        if session and session['user']:
            return session['user']
        return None
    except Exception as e:
        logger.error(f"Error getting current user: {str(e)}")
        return None

def get_user_role(user_id):
    """Fetch the user's role from the profiles table."""
    try:
        response = supabase.table('profiles').select('role').eq('id', user_id).single().execute()
        if response.data and 'role' in response.data:
            return response.data['role']
        return None
    except Exception as e:
        logger.error(f"Error getting user role: {str(e)}")
        return None