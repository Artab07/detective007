import face_recognition
import numpy as np
import cv2
from PIL import Image
import io
import base64
from supabase_config import search_criminal_records
from skimage import transform
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FaceMatcher:
    def __init__(self):
        # Load OpenCV's Haar cascade for face detection
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.face_detector = face_recognition.api.face_detector
        self.face_encoder = face_recognition.api.face_encoder

    def process_image(self, image_path=None, image_data=None):
        """Load and decode image from file path or base64-encoded data."""
        try:
            if image_path:
                image = face_recognition.load_image_file(image_path)
            elif image_data:
                image_bytes = base64.b64decode(image_data)
                image = face_recognition.load_image_file(io.BytesIO(image_bytes))
            else:
                raise ValueError("Either image_path or image_data must be provided")
            
            # Convert to RGB if needed
            if len(image.shape) == 2:
                image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
            elif image.shape[2] == 4:
                image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
                
            return image
        except Exception as e:
            logger.error(f"Error processing image: {str(e)}")
            raise

    def detect_faces(self, image):
        """Detect faces using dlib-cnn for real photos, Haar Cascade for sketches."""
        try:
            # Defensive checks
            if image is None or not isinstance(image, np.ndarray):
                logger.error("Input image is None or not a numpy array")
                return []
            if image.dtype != np.uint8:
                logger.error(f"Image dtype is {image.dtype}, expected uint8")
                return []
            if len(image.shape) == 2:
                pass  # grayscale is fine
            elif len(image.shape) == 3 and image.shape[2] == 3:
                pass  # RGB is fine
            else:
                logger.error(f"Image shape is {image.shape}, expected (H,W) or (H,W,3)")
                return []

            # Ensure image is C-contiguous
            if not image.flags['C_CONTIGUOUS']:
                image = np.ascontiguousarray(image)

            # Detect if image is a sketch (binary or nearly binary)
            unique_vals = np.unique(image)
            if len(unique_vals) < 20:  # Heuristic: very few unique values = sketch
                logger.info("Image appears to be a sketch or thresholded. Using Haar Cascade only.")
                if len(image.shape) == 3:
                    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
                else:
                    gray = image
                faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
                face_locations = [(y, x + w, y + h, x) for (x, y, w, h) in faces]
                if face_locations:
                    logger.info(f"Found {len(face_locations)} face(s) with Haar Cascade.")
                else:
                    logger.warning("No faces detected with Haar Cascade.")
                return face_locations

            # Otherwise, use dlib-cnn for real photos
            face_locations = face_recognition.face_locations(image, model='cnn')
            if face_locations:
                logger.info(f"Found {len(face_locations)} face(s) with CNN model.")
                return face_locations

            logger.warning("No faces detected with CNN model.")
            return []
        except Exception as e:
            logger.error(f"Error detecting faces: {str(e)}")
            return []

    def get_face_encodings(self, image, known_face_locations=None):
        """Return face encodings for all detected faces with enhanced error handling. Use CNN model for consistency."""
        try:
            # Ensure image is uint8 and RGB or grayscale
            if not isinstance(image, np.ndarray):
                raise ValueError(f"Image must be a numpy array, got {type(image)}")
            if image.dtype != np.uint8:
                image = image.astype(np.uint8)
            if len(image.shape) == 2:
                # grayscale, convert to RGB
                image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
            elif len(image.shape) == 3:
                if image.shape[2] == 4:
                    # RGBA, convert to RGB
                    image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
                elif image.shape[2] == 3:
                    # Already RGB, do nothing
                    pass
                else:
                    raise ValueError(f"Unsupported image shape for face encoding: {image.shape}")
            else:
                raise ValueError(f"Unsupported image shape for face encoding: {image.shape}")

            # Always use CNN model for detection and encoding
            if known_face_locations is None:
                known_face_locations = face_recognition.face_locations(image, model='cnn')
            if not known_face_locations:
                logger.warning("No faces detected in the image")
                return []
            encodings = face_recognition.face_encodings(image, known_face_locations, model='cnn')
            if encodings:
                print("Actual encoding array for matching:", encodings[0].tolist())
            return encodings
        except Exception as e:
            logger.error(f"Error getting face encodings: {str(e)}")
            return []

    def match_face(self, face_encoding, tolerance=0.5):
        """Match a face encoding with entries in the criminal database."""
        try:
            matches = search_criminal_records(face_encoding, tolerance)
            return matches
        except Exception as e:
            logger.error(f"Error matching face: {str(e)}")
            return []

    def process_sketch(self, sketch_path=None, sketch_data=None):
        """Process a sketch image with special handling for sketch characteristics."""
        try:
            # Load the sketch
            if sketch_path:
                sketch = cv2.imread(sketch_path)
                if sketch is None:
                    logger.error(f"Failed to load image from {sketch_path}")
                    return []
                logger.info(f"Loaded sketch from {sketch_path} with shape {sketch.shape} and dtype {sketch.dtype}")
            elif sketch_data:
                nparr = np.frombuffer(base64.b64decode(sketch_data), np.uint8)
                sketch = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                if sketch is None:
                    logger.error("Failed to decode sketch from provided data")
                    return []
                logger.info(f"Decoded sketch from data with shape {sketch.shape} and dtype {sketch.dtype}")
            else:
                raise ValueError("Either sketch_path or sketch_data must be provided")

            # Convert to RGB
            sketch = cv2.cvtColor(sketch, cv2.COLOR_BGR2RGB)
            logger.info(f"Sketch converted to RGB with shape {sketch.shape} and dtype {sketch.dtype}")

            # Enhance sketch for better face detection
            enhanced = self.enhance_sketch(sketch)
            logger.info(f"Enhanced sketch shape: {enhanced.shape}, dtype: {enhanced.dtype}")

            # Get face encodings
            face_locations = self.detect_faces(enhanced)
            if not face_locations:
                logger.warning("No faces detected in the sketch")
                return []

            encodings = self.get_face_encodings(enhanced, face_locations)
            return encodings
        except Exception as e:
            logger.error(f"Error processing sketch: {str(e)}")
            return []

    def enhance_sketch(self, image):
        """Enhance sketch image for better face detection."""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            # Apply adaptive thresholding
            thresh = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            # Denoise
            denoised = cv2.fastNlMeansDenoising(thresh)
            # Convert back to RGB
            enhanced = cv2.cvtColor(denoised, cv2.COLOR_GRAY2RGB)
            # Ensure type is uint8
            if enhanced.dtype != np.uint8:
                enhanced = enhanced.astype(np.uint8)
            return enhanced
        except Exception as e:
            logger.error(f"Error enhancing sketch: {str(e)}")
            return image

    def compare_faces(self, known_image_path, unknown_image_path, tolerance=0.6):
        """Compare two face images and return similarity score."""
        try:
            # Load and process both images
            known_image = self.process_image(known_image_path)
            unknown_image = self.process_image(unknown_image_path)
            
            # Get face encodings
            known_encoding = self.get_face_encodings(known_image)
            unknown_encoding = self.get_face_encodings(unknown_image)
            
            if not known_encoding or not unknown_encoding:
                return 0.0
            
            # Compare faces
            face_distance = face_recognition.face_distance(
                [known_encoding[0]], unknown_encoding[0]
            )[0]
            
            # Convert distance to similarity score (0-1)
            similarity = 1 - face_distance
            
            return float(similarity)
        except Exception as e:
            logger.error(f"Error comparing faces: {str(e)}")
            return 0.0
