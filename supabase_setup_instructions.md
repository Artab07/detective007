# Supabase Database Setup Instructions

This guide will help you set up the Supabase database for the Forensic Sketch Creation and Criminal Detection System.

## 1. Create a Supabase Project

1. Go to [https://supabase.com/](https://supabase.com/) and sign in or create an account.
2. Click on "New Project" to create a new project.
3. Enter a project name (e.g., "detective007").
4. Choose a database password (save it securely).
5. Select a region closest to your location.
6. Click "Create new project" and wait for the project to be created.

## 2. Get Your Supabase Credentials

1. In your project dashboard, go to "Project Settings" > "API".
2. Copy the "Project URL" and "anon/public" key.
3. Create a `.env` file in your project root with the following content:
   ```
   SUPABASE_URL=your_project_url
   SUPABASE_KEY=your_anon_public_key
   ```

## 3. Create the Database Schema

1. In your project dashboard, go to "SQL Editor".
2. Create a new query and paste the contents of `supabase_schema.sql`.
3. Click "Run" to execute the SQL commands.

## 4. Create a Storage Bucket

1. In your project dashboard, go to "Storage".
2. Click "Create a new bucket".
3. Enter "criminal-images" as the bucket name.
4. Check "Public bucket" to make the images publicly accessible.
5. Click "Create bucket".

## 5. Set Up Row Level Security (RLS)

The SQL script already includes RLS policies, but you may need to enable them manually:

1. In your project dashboard, go to "Authentication" > "Policies".
2. For each table (profiles, criminal_records, crimes, criminal_images, search_history), ensure RLS is enabled.
3. Add the policies as defined in the SQL script.

## 6. Create an Admin User

1. In your project dashboard, go to "Authentication" > "Users".
2. Click "Invite user" or "Create user".
3. Enter the email and password for your admin user.
4. After creating the user, go to "SQL Editor" and run the following SQL:
   ```sql
   INSERT INTO profiles (id, username, email, is_admin)
   VALUES ('user_id_from_auth', 'admin_username', 'admin_email', true);
   ```
   Replace `user_id_from_auth`, `admin_username`, and `admin_email` with your actual values.

## 7. Add Sample Data (Optional)

You can add sample data using the `setup_database.py` script or manually:

1. In your project dashboard, go to "Table Editor".
2. Select the "criminal_records" table and click "Insert row".
3. Add sample criminal records with the following fields:
   - name
   - dob
   - height
   - weight
   - eye_color
   - hair_color
   - last_known_location
   - last_known_date
   - status
   - notes

4. Repeat for the "crimes" and "criminal_images" tables.

## 8. Test the Connection

1. Run the following Python script to test the connection:
   ```python
   from supabase import create_client
   import os
   from dotenv import load_dotenv

   load_dotenv()
   supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))
   
   response = supabase.table('profiles').select('*').execute()
   print(response.data)
   ```

2. If you see your admin user data, the connection is working correctly.

## Troubleshooting

- If you encounter permission errors, check your RLS policies.
- If you can't connect to the database, verify your credentials in the `.env` file.
- If you can't upload images, check your storage bucket permissions. 