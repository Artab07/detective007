-- Create profiles table for user authentication
CREATE TABLE profiles (
    id UUID REFERENCES auth.users ON DELETE CASCADE,
    username TEXT UNIQUE,
    email TEXT UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    PRIMARY KEY (id)
);

-- Create criminal_records table
CREATE TABLE criminal_records (
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

-- Create crimes table
CREATE TABLE crimes (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    criminal_id UUID REFERENCES criminal_records(id) ON DELETE CASCADE,
    crime_type TEXT NOT NULL,
    date_committed DATE,
    location TEXT,
    description TEXT,
    severity TEXT,
    status TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Create images table for storing multiple images per criminal
CREATE TABLE criminal_images (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    criminal_id UUID REFERENCES criminal_records(id) ON DELETE CASCADE,
    image_url TEXT NOT NULL,
    image_type TEXT NOT NULL, -- 'sketch', 'photo', 'mugshot', etc.
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Create search_history table
CREATE TABLE search_history (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    search_type TEXT NOT NULL, -- 'sketch', 'upload', 'camera'
    search_date TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    result_count INTEGER,
    search_image_url TEXT
);

-- Create RLS policies
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE criminal_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE crimes ENABLE ROW LEVEL SECURITY;
ALTER TABLE criminal_images ENABLE ROW LEVEL SECURITY;
ALTER TABLE search_history ENABLE ROW LEVEL SECURITY;

-- Profiles policies
CREATE POLICY "Users can view their own profile"
    ON profiles FOR SELECT
    USING (auth.uid() = id);

CREATE POLICY "Users can update their own profile"
    ON profiles FOR UPDATE
    USING (auth.uid() = id);

-- Criminal records policies
CREATE POLICY "Anyone can view criminal records"
    ON criminal_records FOR SELECT
    TO authenticated
    USING (true);

CREATE POLICY "Only admins can insert criminal records"
    ON criminal_records FOR INSERT
    TO authenticated
    USING (auth.uid() IN (SELECT id FROM profiles WHERE is_admin = true));

CREATE POLICY "Only admins can update criminal records"
    ON criminal_records FOR UPDATE
    TO authenticated
    USING (auth.uid() IN (SELECT id FROM profiles WHERE is_admin = true));

-- Crimes policies
CREATE POLICY "Anyone can view crimes"
    ON crimes FOR SELECT
    TO authenticated
    USING (true);

CREATE POLICY "Only admins can insert crimes"
    ON crimes FOR INSERT
    TO authenticated
    USING (auth.uid() IN (SELECT id FROM profiles WHERE is_admin = true));

-- Criminal images policies
CREATE POLICY "Anyone can view criminal images"
    ON criminal_images FOR SELECT
    TO authenticated
    USING (true);

CREATE POLICY "Only admins can insert criminal images"
    ON criminal_images FOR INSERT
    TO authenticated
    USING (auth.uid() IN (SELECT id FROM profiles WHERE is_admin = true));

-- Search history policies
CREATE POLICY "Users can view their own search history"
    ON search_history FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own search history"
    ON search_history FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Create functions
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = TIMEZONE('utc'::text, NOW());
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers
CREATE TRIGGER update_profiles_updated_at
    BEFORE UPDATE ON profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_criminal_records_updated_at
    BEFORE UPDATE ON criminal_records
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_crimes_updated_at
    BEFORE UPDATE ON crimes
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();