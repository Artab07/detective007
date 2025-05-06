from supabase import create_client
import os
from dotenv import load_dotenv
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

def test_database():
    try:
        # Test if we can access the table
        logger.info("Testing criminal_records table access...")
        response = supabase.table('criminal_records').select("*").limit(1).execute()
        logger.info("Table access successful!")
        
        # Test if we can insert a minimal record
        logger.info("Testing record insertion...")
        test_data = {
            'name': 'Test Criminal',
            'face_encoding': 'test_encoding'
        }
        response = supabase.table('criminal_records').insert(test_data).execute()
        logger.info("Record insertion successful!")
        
        # Clean up test data
        logger.info("Cleaning up test data...")
        if response.data:
            criminal_id = response.data[0]['id']
            supabase.table('criminal_records').delete().eq('id', criminal_id).execute()
            logger.info("Test data cleaned up successfully!")
            
    except Exception as e:
        logger.error("Database test failed: %s", str(e), exc_info=True)

if __name__ == "__main__":
    test_database() 