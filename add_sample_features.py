import os
import sys
import logging
import shutil
from PIL import Image, ImageDraw

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_directory_if_not_exists(directory):
    """Create a directory if it doesn't exist."""
    if not os.path.exists(directory):
        os.makedirs(directory)
        logger.info(f"Created directory: {directory}")

def create_sample_face_shape():
    """Create a sample face shape image."""
    img = Image.new('RGBA', (200, 250), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw an oval for the face shape
    draw.ellipse((20, 20, 180, 230), outline=(0, 0, 0, 255), width=2)
    
    return img

def create_sample_eyes():
    """Create sample eye images."""
    eyes = []
    
    # Regular eyes
    img = Image.new('RGBA', (100, 40), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse((10, 10, 40, 30), outline=(0, 0, 0, 255), width=2)
    draw.ellipse((60, 10, 90, 30), outline=(0, 0, 0, 255), width=2)
    eyes.append(("regular", img))
    
    # Narrow eyes
    img = Image.new('RGBA', (100, 40), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse((10, 15, 40, 25), outline=(0, 0, 0, 255), width=2)
    draw.ellipse((60, 15, 90, 25), outline=(0, 0, 0, 255), width=2)
    eyes.append(("narrow", img))
    
    # Wide eyes
    img = Image.new('RGBA', (100, 40), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse((5, 5, 45, 35), outline=(0, 0, 0, 255), width=2)
    draw.ellipse((55, 5, 95, 35), outline=(0, 0, 0, 255), width=2)
    eyes.append(("wide", img))
    
    return eyes

def create_sample_noses():
    """Create sample nose images."""
    noses = []
    
    # Regular nose
    img = Image.new('RGBA', (60, 80), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    draw.line((30, 10, 30, 70), fill=(0, 0, 0, 255), width=2)
    noses.append(("regular", img))
    
    # Wide nose
    img = Image.new('RGBA', (60, 80), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    draw.line((20, 10, 40, 70), fill=(0, 0, 0, 255), width=2)
    noses.append(("wide", img))
    
    # Narrow nose
    img = Image.new('RGBA', (60, 80), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    draw.line((25, 10, 35, 70), fill=(0, 0, 0, 255), width=2)
    noses.append(("narrow", img))
    
    return noses

def create_sample_mouths():
    """Create sample mouth images."""
    mouths = []
    
    # Regular mouth
    img = Image.new('RGBA', (100, 40), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    draw.arc((10, 10, 90, 30), 0, 180, fill=(0, 0, 0, 255), width=2)
    mouths.append(("regular", img))
    
    # Smiling mouth
    img = Image.new('RGBA', (100, 40), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    draw.arc((10, 5, 90, 35), 0, 180, fill=(0, 0, 0, 255), width=2)
    mouths.append(("smiling", img))
    
    # Serious mouth
    img = Image.new('RGBA', (100, 40), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    draw.line((20, 20, 80, 20), fill=(0, 0, 0, 255), width=2)
    mouths.append(("serious", img))
    
    return mouths

def create_sample_hairs():
    """Create sample hair images."""
    hairs = []
    
    # Short hair
    img = Image.new('RGBA', (200, 100), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    draw.arc((20, 20, 180, 100), 0, 180, fill=(0, 0, 0, 255), width=2)
    hairs.append(("short", img))
    
    # Long hair
    img = Image.new('RGBA', (200, 200), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    draw.arc((20, 20, 180, 100), 0, 180, fill=(0, 0, 0, 255), width=2)
    draw.rectangle((20, 100, 180, 200), outline=(0, 0, 0, 255), width=2)
    hairs.append(("long", img))
    
    # Bald
    img = Image.new('RGBA', (200, 50), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    draw.arc((20, 0, 180, 50), 0, 180, fill=(0, 0, 0, 255), width=2)
    hairs.append(("bald", img))
    
    return hairs

def save_feature(img, feature_type, feature_name, output_dir):
    """Save a feature image to the output directory."""
    feature_dir = os.path.join(output_dir, feature_type)
    create_directory_if_not_exists(feature_dir)
    
    output_path = os.path.join(feature_dir, f"{feature_name}.png")
    img.save(output_path)
    logger.info(f"Saved {feature_type} feature: {feature_name}")

def main():
    """Main function to add sample facial features."""
    try:
        logger.info("Starting to add sample facial features...")
        
        # Create face_features directory
        face_features_dir = 'face_features'
        create_directory_if_not_exists(face_features_dir)
        
        # Create face shape
        face_shape = create_sample_face_shape()
        save_feature(face_shape, "face_shape", "oval", face_features_dir)
        
        # Create eyes
        eyes = create_sample_eyes()
        for eye_name, eye_img in eyes:
            save_feature(eye_img, "eyes", eye_name, face_features_dir)
        
        # Create noses
        noses = create_sample_noses()
        for nose_name, nose_img in noses:
            save_feature(nose_img, "noses", nose_name, face_features_dir)
        
        # Create mouths
        mouths = create_sample_mouths()
        for mouth_name, mouth_img in mouths:
            save_feature(mouth_img, "mouths", mouth_name, face_features_dir)
        
        # Create hairs
        hairs = create_sample_hairs()
        for hair_name, hair_img in hairs:
            save_feature(hair_img, "hairs", hair_name, face_features_dir)
        
        logger.info("Sample facial features added successfully!")
        
    except Exception as e:
        logger.error(f"Error adding sample facial features: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 