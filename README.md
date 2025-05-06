# Forensic Sketch Creation and Criminal Detection System

This system allows users to create forensic sketches, upload images, and match them against a database of criminal records using face recognition technology.

## Features

- User authentication (sign up, sign in, sign out)
- Forensic sketch creation with draggable facial features
- Image upload and camera capture for face matching
- Criminal database with face recognition matching
- Detailed criminal record viewing
- Search history tracking

## Prerequisites

- Python 3.12 or higher
- Supabase account and project
- Webcam (for camera capture feature)

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd detective007
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/Mac
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root with your Supabase credentials:
   ```
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key
   ```

## Database Setup

1. Set up the Supabase storage bucket:
   ```
   python setup_storage.py
   ```

2. Set up the database schema and add sample data:
   ```
   python setup_database.py
   ```
   - Follow the prompts to create an admin user
   - The script will add sample criminal records

## Usage

1. Run the application:
   ```
   python main.py
   ```

2. Sign in with your credentials or create a new account

3. Create a forensic sketch:
   - Select facial features from the provided options
   - Drag, resize, and rotate features to create a sketch
   - Submit the sketch for matching

4. Upload an image or use the camera to capture an image for matching

5. View matching criminal records and details

## Project Structure

- `main.py`: Entry point for the application
- `frontend.py`: GUI implementation using customtkinter
- `face_matcher.py`: Face recognition and matching functionality
- `supabase_config.py`: Database connection and operations
- `supabase_schema.sql`: Database schema definition
- `setup_database.py`: Script to set up the database
- `setup_storage.py`: Script to set up storage buckets
- `images/`: Directory for storing images
- `face_features/`: Directory for facial feature images
- `models/`: Directory for face recognition models

## Troubleshooting

- If you encounter issues with face recognition, ensure that dlib is properly installed
- For database connection issues, verify your Supabase credentials in the `.env` file
- If the application crashes, check the logs for error messages

## License

This project is licensed under the MIT License - see the LICENSE file for details. 