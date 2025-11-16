from flask import Flask, render_template, request, jsonify
import face_recognition
import numpy as np
import pandas as pd
import os
from datetime import datetime
import pickle
import base64
from io import BytesIO
from PIL import Image

app = Flask(__name__)

class SmartAttendanceSystem:
    def __init__(self):
        self.known_face_encodings = []
        self.known_face_names = []
        self.attendance_log = []
        self.upload_folder = "uploads"
        self.attendance_file = os.path.join(self.upload_folder, "attendance_log.csv")
        self.encodings_file = os.path.join(self.upload_folder, "face_encodings.pkl")
        
        # Create necessary files and folders
        self.setup_files()
        
        # Load existing data
        self.load_encodings()
        self.load_attendance_log()
    
    def setup_files(self):
        """Create necessary files and directories"""
        try:
            # Create upload folder
            os.makedirs(self.upload_folder, exist_ok=True)
            print(f"Created/verified uploads directory: {self.upload_folder}")
            
            # Create face encodings file if it doesn't exist
            if not os.path.exists(self.encodings_file):
                empty_data = {'encodings': [], 'names': []}
                with open(self.encodings_file, 'wb') as f:
                    pickle.dump(empty_data, f)
                print(f"Created {self.encodings_file}")
            
            # Create attendance log file if it doesn't exist
            if not os.path.exists(self.attendance_file):
                df = pd.DataFrame(columns=['Name', 'Date', 'Time', 'Status'])
                df.to_csv(self.attendance_file, index=False)
                print(f"Created {self.attendance_file}")
                
        except Exception as e:
            print(f"Error setting up files: {str(e)}")
    
    def add_person_from_image(self, name, image_data):
        """Add person from image data (base64 or file)"""
        try:
            if isinstance(image_data, str) and image_data.startswith('data:image'):
                # Handle base64 image data
                image_data = image_data.split(',')[1]
                image_bytes = base64.b64decode(image_data)
                image = Image.open(BytesIO(image_bytes))
                image_np = np.array(image)
            else:
                # Handle file upload
                image_np = face_recognition.load_image_file(image_data)
            
            # Get face encoding
            face_encodings = face_recognition.face_encodings(image_np)
            
            if len(face_encodings) > 0:
                face_encoding = face_encodings[0]
                
                # Check if person already exists
                if name in self.known_face_names:
                    return False, f"Person '{name}' already exists in the system"
                
                # Add to known faces
                self.known_face_encodings.append(face_encoding)
                self.known_face_names.append(name)
                
                # Save encodings
                self.save_encodings()
                return True, f"Successfully added {name} to the system"
            else:
                return False, "No face found in the image"
                
        except Exception as e:
            return False, f"Error processing image: {str(e)}"
    
    def remove_person(self, name):
        """Remove person from the system"""
        try:
            if name not in self.known_face_names:
                return False, f"Person '{name}' not found in the system"
            
            # Find the index of the person
            index = self.known_face_names.index(name)
            
            # Remove from both lists
            self.known_face_names.pop(index)
            self.known_face_encodings.pop(index)
            
            # Save updated encodings
            self.save_encodings()
            
            # Optionally, you might want to keep attendance records for historical purposes
            # or remove them as well. Here we'll keep them for historical data.
            
            return True, f"Successfully removed {name} from the system"
            
        except Exception as e:
            return False, f"Error removing person: {str(e)}"
    
    def remove_person_and_records(self, name):
        """Remove person and all their attendance records"""
        try:
            if name not in self.known_face_names:
                return False, f"Person '{name}' not found in the system"
            
            # Find the index of the person
            index = self.known_face_names.index(name)
            
            # Remove from both lists
            self.known_face_names.pop(index)
            self.known_face_encodings.pop(index)
            
            # Remove attendance records
            self.attendance_log = [record for record in self.attendance_log if record['Name'] != name]
            
            # Save updated data
            self.save_encodings()
            self.save_attendance_log()
            
            return True, f"Successfully removed {name} and all attendance records from the system"
            
        except Exception as e:
            return False, f"Error removing person and records: {str(e)}"
    
    def save_encodings(self):
        """Save face encodings to file"""
        try:
            data = {
                'encodings': self.known_face_encodings,
                'names': self.known_face_names
            }
            with open(self.encodings_file, 'wb') as f:
                pickle.dump(data, f)
            return True
        except Exception as e:
            print(f"Error saving encodings: {str(e)}")
            return False
    
    def load_encodings(self):
        """Load face encodings from file"""
        try:
            if os.path.exists(self.encodings_file):
                with open(self.encodings_file, 'rb') as f:
                    data = pickle.load(f)
                    self.known_face_encodings = data.get('encodings', [])
                    self.known_face_names = data.get('names', [])
                print(f"Loaded {len(self.known_face_names)} known faces")
        except Exception as e:
            print(f"Error loading encodings: {str(e)}")
            # Reset to empty if there's an error
            self.known_face_encodings = []
            self.known_face_names = []
    
    def load_attendance_log(self):
        """Load existing attendance log"""
        try:
            if os.path.exists(self.attendance_file):
                df = pd.read_csv(self.attendance_file)
                self.attendance_log = df.to_dict('records')
            else:
                self.attendance_log = []
        except Exception as e:
            print(f"Error loading attendance log: {str(e)}")
            self.attendance_log = []
    
    def save_attendance_log(self):
        """Save attendance log to file"""
        try:
            df = pd.DataFrame(self.attendance_log)
            df.to_csv(self.attendance_file, index=False)
            return True
        except Exception as e:
            print(f"Error saving attendance log: {str(e)}")
            return False
    
    def get_attendance_data(self):
        """Get attendance data for display"""
        return self.attendance_log

# Initialize the attendance system
attendance_system = SmartAttendanceSystem()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_person', methods=['POST'])
def add_person():
    try:
        name = request.form.get('name', '').strip()
        if not name:
            return jsonify({'success': False, 'message': 'Name is required'})
        
        # Check for uploaded file
        if 'file' in request.files and request.files['file'].filename:
            file = request.files['file']
            if file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                success, message = attendance_system.add_person_from_image(name, file)
                return jsonify({'success': success, 'message': message})
        
        # Check for base64 image data (from camera)
        elif 'image_data' in request.form:
            image_data = request.form['image_data']
            success, message = attendance_system.add_person_from_image(name, image_data)
            return jsonify({'success': success, 'message': message})
        
        return jsonify({'success': False, 'message': 'No image provided'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/remove_person', methods=['POST'])
def remove_person():
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        remove_records = data.get('remove_records', False)
        
        if not name:
            return jsonify({'success': False, 'message': 'Name is required'})
        
        if remove_records:
            success, message = attendance_system.remove_person_and_records(name)
        else:
            success, message = attendance_system.remove_person(name)
            
        return jsonify({'success': success, 'message': message})
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/get_attendance')
def get_attendance():
    attendance_data = attendance_system.get_attendance_data()
    return jsonify(attendance_data)

@app.route('/get_known_persons')
def get_known_persons():
    return jsonify(attendance_system.known_face_names)

@app.route('/get_recent_attendance')
def get_recent_attendance():
    """Get recent attendance markings for real-time updates"""
    today = datetime.now().strftime("%Y-%m-%d")
    recent_attendance = [entry for entry in attendance_system.attendance_log 
                        if entry['Date'] == today]
    return jsonify(recent_attendance)

if __name__ == '__main__':
    # Ensure all files are created on startup
    print("Starting Smart Attendance System...")
    print(f"Files will be saved in: {os.path.abspath(attendance_system.upload_folder)}")
    print(f"Known persons loaded: {len(attendance_system.known_face_names)}")
    print(f"Attendance records loaded: {len(attendance_system.attendance_log)}")
    app.run(debug=True, threaded=True)