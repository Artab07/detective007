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

try:
    # Try to fetch a record from the criminal_records table
    response = supabase.table('criminal_records').select("*").limit(1).execute()
    print("Connection successful!")
    print("Response:", response)
except Exception as e:
    print("Connection failed!")
    print("Error:", str(e)) 