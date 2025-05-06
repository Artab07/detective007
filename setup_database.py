import os
import sys
import logging
from dotenv import load_dotenv
from supabase import create_client
import numpy as np
import face_recognition
import base64
import io
from PIL import Image
import uuid
from datetime import datetime, timedelta

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get Supabase credentials
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')

if not supabase_url or not supabase_key:
    logger.error("Supabase credentials not found in .env file")
    logger.info("Please create a .env file with the following content:")
    logger.info("SUPABASE_URL=your_supabase_url")
    logger.info("SUPABASE_KEY=your_supabase_key")
    sys.exit(1)

# Initialize Supabase client
supabase = create_client(supabase_url, supabase_key)

def create_tables():
    """Create all necessary tables in the database."""
    try:
        logger.info("Creating database tables...")
        
        # Create criminal_records table
        sql = """
        CREATE TABLE IF NOT EXISTS criminal_records (
            id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
            name TEXT NOT NULL,
            dob DATE,
            height NUMERIC,
            weight NUMERIC,
            eye_color TEXT,
            hair_color TEXT,
            last_known_location TEXT,
            last_known_date DATE,
            status TEXT,
            notes TEXT,
            face_encoding BYTEA,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
        );
        """
        supabase.rpc('exec_sql', {'sql': sql}).execute()
        logger.info("Created criminal_records table")
        
        # Create criminal_images table
        sql = """
        CREATE TABLE IF NOT EXISTS criminal_images (
            id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
            criminal_id UUID REFERENCES criminal_records(id) ON DELETE CASCADE,
            image_url TEXT NOT NULL,
            image_type TEXT NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
        );
        """
        supabase.rpc('exec_sql', {'sql': sql}).execute()
        logger.info("Created criminal_images table")
        
        # Create update timestamp function
        sql = """
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = TIMEZONE('utc'::text, NOW());
            RETURN NEW;
        END;
        $$ language 'plpgsql';
        """
        supabase.rpc('exec_sql', {'sql': sql}).execute()
        logger.info("Created update_updated_at_column function")
        
        # Create trigger for criminal_records
        sql = """
        CREATE TRIGGER update_criminal_records_updated_at
            BEFORE UPDATE ON criminal_records
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
        """
        supabase.rpc('exec_sql', {'sql': sql}).execute()
        logger.info("Created trigger for criminal_records")
        
        logger.info("Database setup completed successfully!")
        
    except Exception as e:
        logger.error(f"Error setting up database: {str(e)}")
        raise

def create_admin_user(email, password, username):
    """Create an admin user."""
    try:
        # Sign up the user
        response = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": {
                    "username": username,
                    "is_admin": True
                }
            }
        })
        
        if response.user:
            # Add user profile to profiles table
            supabase.table('profiles').insert({
                'id': response.user.id,
                'username': username,
                'email': email,
                'is_admin': True
            }).execute()
            
            logger.info(f"Admin user created: {username}")
            return response.user.id
        else:
            logger.error("Failed to create admin user")
            return None
    except Exception as e:
        logger.error(f"Error creating admin user: {str(e)}")
        raise

def add_sample_criminal_record(name, dob, face_image_path=None):
    """Add a sample criminal record with face encoding."""
    try:
        # Generate a random UUID for the criminal record
        criminal_id = str(uuid.uuid4())
        
        # Create face encoding if image is provided
        face_encoding = None
        if face_image_path and os.path.exists(face_image_path):
            # Load the image
            image = face_recognition.load_image_file(face_image_path)
            
            # Detect faces
            face_locations = face_recognition.face_locations(image)
            
            if face_locations:
                # Get face encodings
                encodings = face_recognition.face_encodings(image, face_locations)
                
                if encodings:
                    face_encoding = encodings[0]
                    logger.info(f"Face encoding created for {name}")
                else:
                    logger.warning(f"No face encodings found for {name}")
            else:
                logger.warning(f"No faces detected in image for {name}")
        
        # Create criminal record
        criminal_data = {
            'id': criminal_id,
            'name': name,
            'dob': dob,
            'height': 175,  # cm
            'weight': 70,   # kg
            'eye_color': 'Brown',
            'hair_color': 'Black',
            'last_known_location': 'New York City',
            'last_known_date': (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
            'status': 'At Large',
            'notes': 'Sample criminal record for testing',
            'face_encoding': face_encoding.tobytes() if face_encoding is not None else None
        }
        
        # Insert criminal record
        supabase.table('criminal_records').insert(criminal_data).execute()
        logger.info(f"Criminal record added: {name}")
        
        # Add sample crime
        crime_data = {
            'criminal_id': criminal_id,
            'crime_type': 'Robbery',
            'date_committed': (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%d'),
            'location': 'Manhattan',
            'description': 'Armed robbery of a convenience store',
            'severity': 'High',
            'status': 'Unsolved'
        }
        
        supabase.table('crimes').insert(crime_data).execute()
        logger.info(f"Crime record added for: {name}")
        
        # Add sample image if provided
        if face_image_path and os.path.exists(face_image_path):
            # Upload image to Supabase Storage
            with open(face_image_path, 'rb') as f:
                image_data = f.read()
            
            # Generate a unique filename
            filename = f"{criminal_id}_{os.path.basename(face_image_path)}"
            
            # Upload to Supabase Storage
            storage_response = supabase.storage.from_('criminal-images').upload(
                filename, 
                image_data,
                {'content-type': 'image/jpeg'}
            )
            
            # Get the public URL
            image_url = supabase.storage.from_('criminal-images').get_public_url(filename)
            
            # Add image record
            image_data = {
                'criminal_id': criminal_id,
                'image_url': image_url,
                'image_type': 'mugshot'
            }
            
            supabase.table('criminal_images').insert(image_data).execute()
            logger.info(f"Image added for: {name}")
        
        return criminal_id
    except Exception as e:
        logger.error(f"Error adding sample criminal record: {str(e)}")
        raise

def main():
    """Main function to set up the database."""
    try:
        logger.info("Starting database setup...")
        create_tables()
        
        # Create admin user
        logger.info("Creating admin user...")
        admin_email = input("Enter admin email: ")
        admin_password = input("Enter admin password: ")
        admin_username = input("Enter admin username: ")
        
        admin_id = create_admin_user(admin_email, admin_password, admin_username)
        
        if not admin_id:
            logger.error("Failed to create admin user. Exiting.")
            sys.exit(1)
        
        # Add sample criminal records
        logger.info("Adding sample criminal records...")
        
        # Check if we have sample images
        sample_images_dir = 'images/sample'
        if os.path.exists(sample_images_dir):
            sample_images = [f for f in os.listdir(sample_images_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]
            
            if sample_images:
                for i, image_file in enumerate(sample_images):
                    image_path = os.path.join(sample_images_dir, image_file)
                    name = f"Sample Criminal {i+1}"
                    dob = (datetime.now() - timedelta(days=365*30)).strftime('%Y-%m-%d')  # 30 years old
                    
                    add_sample_criminal_record(name, dob, image_path)
            else:
                logger.warning("No sample images found. Adding criminal records without images.")
                for i in range(3):
                    name = f"Sample Criminal {i+1}"
                    dob = (datetime.now() - timedelta(days=365*30)).strftime('%Y-%m-%d')  # 30 years old
                    
                    add_sample_criminal_record(name, dob)
        else:
            logger.warning("Sample images directory not found. Adding criminal records without images.")
            for i in range(3):
                name = f"Sample Criminal {i+1}"
                dob = (datetime.now() - timedelta(days=365*30)).strftime('%Y-%m-%d')  # 30 years old
                
                add_sample_criminal_record(name, dob)
        
        logger.info("Database setup completed successfully!")
        logger.info(f"Admin user created: {admin_username}")
        logger.info("You can now log in to the application using these credentials.")
        
    except Exception as e:
        logger.error(f"Error during database setup: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 