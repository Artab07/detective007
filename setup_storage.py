import os
import logging
from dotenv import load_dotenv
from supabase import create_client
import base64
import numpy as np

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

def setup_storage():
    """Set up storage bucket for criminal images."""
    try:
        bucket_id = 'criminal-images'
        logger.info(f"Creating {bucket_id} storage bucket...")
        
        # Create new bucket
        supabase.storage.create_bucket(
            id=bucket_id,
            options={'public': True}  # Make bucket public
        )
        logger.info(f"Created {bucket_id} bucket")
            
        logger.info("Storage setup completed successfully!")
        
    except Exception as e:
        if 'already exists' in str(e).lower():
            logger.info(f"Bucket {bucket_id} already exists")
        else:
            logger.error("Error setting up storage: %s", str(e))
            raise

if __name__ == "__main__":
    setup_storage() 