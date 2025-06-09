# Detective007 

[![Python 3.8+](https://img.shields.io/badge/Python-3.12+-3776ab?style=flat&logo=python&logoColor=white)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CustomTkinter](https://img.shields.io/badge/GUI-CustomTkinter-FF6B35?style=flat)](https://github.com/TomSchimansky/CustomTkinter)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.x-5C3EE8?style=flat&logo=opencv&logoColor=white)](https://opencv.org/)
[![Face Recognition](https://img.shields.io/badge/Face_Recognition-AI-FF4B4B?style=flat)](https://github.com/ageitgey/face_recognition)
[![Supabase](https://img.shields.io/badge/Supabase-3ECF8E?style=flat&logo=supabase&logoColor=white)](https://supabase.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=flat&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![dlib](https://img.shields.io/badge/dlib-ML-8B5A2B?style=flat)](http://dlib.net/)
[![Pillow](https://img.shields.io/badge/Pillow-Image_Processing-4B8BBE?style=flat)](https://pillow.readthedocs.io/)
[![NumPy](https://img.shields.io/badge/NumPy-013243?style=flat&logo=numpy&logoColor=white)](https://numpy.org/)


**A sophisticated forensic sketch creation and face recognition system for criminal investigation.**

Detective007 is a comprehensive digital forensics tool that combines forensic sketch creation with advanced face recognition technology. This system enables law enforcement professionals and investigators to create detailed sketches and match them against criminal databases with high accuracy.

## Features

### Forensic Sketch Creation
- **Interactive Sketch Builder**: Drag-and-drop facial features with precision control
- **Comprehensive Feature Library**: Extensive collection of eyes, noses, mouths, and other facial features
- **Real-time Editing**: Resize, rotate, and position features with intuitive controls
- **Professional Output**: Generate high-quality sketches suitable for investigations

### Face Recognition & Matching
- **Advanced AI Matching**: State-of-the-art face recognition algorithms
- **Multi-input Support**: Upload images or capture directly from webcam
- **Database Integration**: Seamless matching against criminal record databases
- **Accuracy Scoring**: Confidence levels for each match result

### User Management
- **Secure Authentication**: Complete sign-up, sign-in, and sign-out system
- **User Profiles**: Personalized workspace for each investigator
- **Access Control**: Role-based permissions for sensitive operations

### Investigation Tools
- **Criminal Database**: Comprehensive database of criminal records with photos
- **Search History**: Track and review previous investigations
- **Detailed Records**: Access complete criminal profiles and case information
- **Export Capabilities**: Generate reports and export results

## Quick Start

### Prerequisites

Ensure you have the following installed on your system:

- **Python 3.8 or higher**
- **Supabase account** (for database and storage)
- **Webcam** (for camera capture functionality)
- **Git** (for cloning the repository)

### Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/Artab07/detective007.git
   cd detective007
   ```

2. **Create Virtual Environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # On Windows:
   venv\Scripts\activate
   
   # On Linux/Mac:
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

  ```bash
   if you face any error in any files installation manually install it
   ```
4. **Environment Configuration**
   
   Create a `.env` file in the project root directory:
   ```env
   SUPABASE_URL=your_supabase_project_url
   SUPABASE_KEY=your_supabase_anon_key
   ```

5. **Database Setup**
   
   Set up your Supabase storage bucket:
   ```bash
   python setup_storage.py
   ```
   
   Initialize the database schema and add sample data:
   ```bash
   python setup_database.py
   ```
   
   Follow the prompts to:
   - Create an admin user account
   - Populate the database with sample criminal records

6. **Launch the Application**
   ```bash
   python frontend.py
   ```

## Usage Guide

### 1. **Authentication**
   # Launch the application
    python frontend.py
   ![Screenshot 2024-12-18 144548](https://github.com/user-attachments/assets/9373468f-40c8-4e94-8c10-a48a1d76b8c0)

   # Sign up
   ![Screenshot 2024-12-18 144729](https://github.com/user-attachments/assets/4e2755de-e0cc-40b4-9937-26b7809dc996)

   # Sign in with your credentials or create a new account
   ![Screenshot 2025-06-09 115421](https://github.com/user-attachments/assets/c2cf06dc-c0e8-4bb4-9941-b72a7594592c)

   # Access your personalized dashboard
   ![Screenshot 2025-06-09 115615](https://github.com/user-attachments/assets/5fabfa28-2488-4833-a28f-38aa7c4d51cf)


2. **Creating Forensic Sketches**
   - Navigate to the sketch creation interface
   - Browse and select facial features from the library
   - Drag features onto the canvas
   ![Screenshot 2025-06-09 115918](https://github.com/user-attachments/assets/5b1ef722-66f1-4cd0-9194-f5c3cd7485af)

   - Use resize and rotation controls for precise positioning
   - Submit completed sketch for database matching

3. **Image-Based Matching**
   - Upload an existing image file
   - OR use the integrated camera to capture a photo
   - The system will automatically process and match against the database
   - Review match results with confidence scores

4. **Investigating Results**
   - Browse through matched criminal records
   - Access detailed profiles and case information
   - Export results for reporting purposes
   - Save investigations to your search history


##  Project Structure

```
detective007/                  
├── frontend.py               # Application entry point, GUI implementation (CustomTkinter)
├── face_matcher.py           # Face recognition and matching engine
├── supabase_config.py        # Database connection and operations
├── supabase_schema.sql       # Database schema definition
├── setup_database.py         # Database initialization script
├── setup_storage.py          # Storage bucket setup script
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables (create this)
├── images/                   # Image storage directory
├── face_features/            # Facial feature library
│   ├── eyes/                # Eye feature variations
│   ├── noses/               # Nose feature variations
│   ├── mouths/              # Mouth feature variations
│   └── ...                  # Additional features
├── models/                   # Face recognition models
└── docs/                     # Documentation files
```

##  Technology Stack

- **Frontend**: CustomTkinter (Modern GUI framework)
- **Backend**: Python 3.8+
- **Face Recognition**: OpenCV, dlib, face_recognition
- **Database**: Supabase (PostgreSQL)
- **Storage**: Supabase Storage
- **Authentication**: Supabase Auth
- **Image Processing**: PIL (Pillow), NumPy

##  Dependencies

Key Python packages used in this project:

```txt
customtkinter              # Modern GUI framework
face-recognition          # Face recognition library
opencv-python            # Computer vision library
pillow                   # Image processing
supabase                 # Database and storage client
python-dotenv            # Environment variable management
numpy                    # Numerical computing
dlib                     # Machine learning library
```

## Troubleshooting

### Common Issues

**Face Recognition Installation Issues**
- Ensure `dlib` is properly installed
- On Windows, you may need Visual Studio Build Tools
- Try using conda instead of pip for problematic packages

**Database Connection Problems**
- Verify your Supabase credentials in the `.env` file
- Check your internet connection
- Ensure your Supabase project is active

**Application Crashes**
- Check the console for error messages
- Verify all dependencies are installed correctly
- Ensure Python version compatibility (3.12+)

**Webcam Not Working**
- Check camera permissions
- Verify camera is not being used by another application
- Test with a different USB port (for external cameras)

### Performance Optimization

- **Large Image Files**: Compress images before processing for faster results
- **Database Queries**: Use filters to limit search scope
- **Memory Usage**: Close unused sketches and clear cache regularly

##  Security Considerations

- **Data Privacy**: All facial data is processed locally before database storage
- **Secure Authentication**: Passwords are hashed and stored securely
- **Access Control**: Role-based permissions prevent unauthorized access
- **Data Encryption**: Sensitive data is encrypted in transit and at rest

##  Contributing

We welcome contributions from the community! Here's how you can help:

### Development Setup

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Make your changes and test thoroughly
4. Commit your changes: `git commit -m 'Add new feature'`
5. Push to the branch: `git push origin feature/new-feature`
6. Submit a pull request

### Contribution Guidelines

- Follow PEP 8 style guidelines
- Include docstrings for all functions and classes
- Add unit tests for new features
- Update documentation as needed
- Test with multiple Python versions


## 👥 Author

- **Artab07** - *Project Creator & Lead Developer* - [@Artab07](https://github.com/Artab07)

## Acknowledgments

- **Face Recognition Community**: For providing excellent open-source libraries
- **Law Enforcement Professionals**: For feedback and requirements guidance
- **Beta Testers**: For helping improve the system's accuracy and usability
- **Open Source Contributors**: For continuous improvements and bug fixes

## Support & Contact

Need help or have questions?

-  **Bug Reports**: [GitHub Issues](https://github.com/Artab07/detective007/issues)
-  **Discussions**: [GitHub Discussions](https://github.com/Artab07/detective007/discussions)
-  **Email**: [Contact the maintainer](mailto:artab.maji1993@gmail.com)

## Roadmap

### Planned Features

- [ ] **Mobile Application**: Native mobile app for field investigations
- [ ] **API Integration**: RESTful API for third-party integrations
- [ ] **Advanced AI Models**: Implementation of newer face recognition algorithms
- [ ] **Multi-language Support**: Internationalization for global use
- [ ] **Cloud Deployment**: Hosted version for smaller departments
- [ ] **Reporting Dashboard**: Advanced analytics and reporting tools

### Recent Updates

- ✅ **v1.0.0**: Initial release with core functionality
- ✅ **Database Integration**: Supabase integration complete
- ✅ **Face Matching**: Advanced matching algorithms implemented
- ✅ **User Authentication**: Secure login system

---

**Detective007** - *Bridging the gap between traditional forensic sketching and modern face recognition technology.*

*Made with ❤️ for the law enforcement community*
