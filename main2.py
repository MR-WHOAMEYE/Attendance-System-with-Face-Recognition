import cv2
import face_recognition
import numpy as np
import pandas as pd
import os
from datetime import datetime
import pickle
import time
import serial

class ConsoleAttendanceSystem:
    def __init__(self):
        self.known_face_encodings = []
        self.known_face_names = []
        self.attendance_log = []
        self.uploads_dir = "uploads"
        self.attendance_file = os.path.join(self.uploads_dir, "attendance_log.csv")
        self.encodings_file = os.path.join(self.uploads_dir, "face_encodings.pkl")
        
        # Track recent recognitions to avoid duplicate marking
        self.recent_recognitions = {}
        self.recognition_cooldown = 30  # seconds
        
        # Create necessary files and folders
        self.setup_files()
        
        # Load existing data
        self.load_encodings()
        self.load_attendance_log()
        
        # Initialize serial connection to Pico COM5 at 115200 baud
        try:
            self.serial_port = serial.Serial('COM5', 115200, timeout=1)
            time.sleep(2)  # Allow Pico reset and ready
            print("Serial port COM5 opened for communication with Pico.")
        except Exception as e:
            print(f"Error opening serial port COM5: {e}")
            self.serial_port = None
    
    def setup_files(self):
        """Create necessary files and directories"""
        try:
            # Create upload folder
            os.makedirs(self.uploads_dir, exist_ok=True)
            print(f"Created/verified uploads directory: {self.uploads_dir}")
            
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
    
    def load_encodings(self):
        """Load face encodings from file"""
        try:
            if os.path.exists(self.encodings_file):
                with open(self.encodings_file, 'rb') as f:
                    data = pickle.load(f)
                    self.known_face_encodings = data.get('encodings', [])
                    self.known_face_names = data.get('names', [])
                print(f"Loaded {len(self.known_face_names)} known faces: {self.known_face_names}")
            else:
                print("No existing encodings file found")
        except Exception as e:
            print(f"Error loading encodings: {str(e)}")
            self.known_face_encodings = []
            self.known_face_names = []
    
    def load_attendance_log(self):
        """Load existing attendance log"""
        try:
            if os.path.exists(self.attendance_file):
                df = pd.read_csv(self.attendance_file)
                self.attendance_log = df.to_dict('records')
                print(f"Loaded {len(self.attendance_log)} attendance records")
            else:
                self.attendance_log = []
                print("No existing attendance log found")
        except Exception as e:
            print(f"Error loading attendance log: {str(e)}")
            self.attendance_log = []
    
    def can_mark_attendance(self, name):
        """Check if enough time has passed since last recognition"""
        current_time = time.time()
        if name in self.recent_recognitions:
            time_diff = current_time - self.recent_recognitions[name]
            return time_diff > self.recognition_cooldown
        return True
    
    def mark_attendance_automatic(self, name):
        """Automatically mark attendance for a person"""
        if not self.can_mark_attendance(name):
            return False, f"Attendance recently marked for {name}"
        
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M:%S")
        
        # Check if already marked today
        today_attendance = [entry for entry in self.attendance_log 
                            if entry['Name'] == name and entry['Date'] == date_str]
        
        if not today_attendance:
            attendance_entry = {
                'Name': name,
                'Date': date_str,
                'Time': time_str,
                'Status': 'Present'
            }
            
            self.attendance_log.append(attendance_entry)
            
            # Save to CSV
            try:
                df = pd.DataFrame([attendance_entry])
                if os.path.exists(self.attendance_file) and os.path.getsize(self.attendance_file) > 0:
                    df.to_csv(self.attendance_file, mode='a', header=False, index=False)
                else:
                    df.to_csv(self.attendance_file, mode='w', header=True, index=False)
            except Exception as e:
                print(f"Error saving attendance: {str(e)}")
            
            # Update recent recognition time
            self.recent_recognitions[name] = time.time()
            
            return True, f"Attendance marked for {name} at {time_str}"
        else:
            # Update recognition time even if already marked today to reset cooldown
            self.recent_recognitions[name] = time.time()
            return False, f"Attendance already marked for {name} today"
    
    def start_face_recognition(self):
        """Start face recognition using webcam"""
        print("\n--- Starting Face Recognition ---")
        print("Press 'q' to quit, 's' to save current frame")
        
        if not self.known_face_names:
            print("No known faces in the system! Please add some persons first using the web interface.")
            return
        
        camera = cv2.VideoCapture(0)
        
        if not camera.isOpened():
            print("Error: Could not open camera")
            return
        
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        camera.set(cv2.CAP_PROP_FPS, 20)
        
        print("Camera started. Face recognition active...")
        
        process_this_frame = True
        
        try:
            while True:
                ret, frame = camera.read()
                if not ret:
                    print("Error reading from camera")
                    break
                
                if process_this_frame:
                    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
                    
                    face_locations = face_recognition.face_locations(rgb_small_frame, model="hog")
                    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
                    
                    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                        matches = face_recognition.compare_faces(
                            self.known_face_encodings, 
                            face_encoding, 
                            tolerance=0.6
                        )
                        name = "Unknown"
                        confidence = 0
                        
                        if len(matches) > 0 and True in matches:
                            face_distances = face_recognition.face_distance(
                                self.known_face_encodings, 
                                face_encoding
                            )
                            best_match_index = np.argmin(face_distances)
                            
                            if matches[best_match_index]:
                                name = self.known_face_names[best_match_index]
                                confidence = 1 - face_distances[best_match_index]
                                
                                if confidence > 0.4:
                                    success, message = self.mark_attendance_automatic(name)
                                    if success:
                                        print(f"✓ {message}")
                                        
                                        # Send recognition message to Pico
                                        now = datetime.now()
                                        time_str = now.strftime("%H:%M:%S")
                                        pico_message = f"RECOGNIZE|{name}|{time_str}|IN\n"
                                        if self.serial_port and self.serial_port.is_open:
                                            try:
                                                self.serial_port.write(pico_message.encode('utf-8'))
                                            except Exception as e:
                                                print(f"Error sending to Pico: {e}")
                                    
                        # Scale back face locations for drawing on original frame
                        top *= 4
                        right *= 4
                        bottom *= 4
                        left *= 4
                        
                        color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
                        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
                        
                        display_text = f"{name}"
                        if name != "Unknown":
                            display_text += f" ({confidence:.2f})"
                        
                        cv2.putText(frame, display_text, (left + 6, bottom - 6), 
                                    cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)
                
                process_this_frame = not process_this_frame
                
                cv2.imshow('Face Recognition Attendance', frame)
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('s'):
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = os.path.join(self.uploads_dir, f"capture_{timestamp}.jpg")
                    cv2.imwrite(filename, frame)
                    print(f"Frame saved as {filename}")
        
        except KeyboardInterrupt:
            print("\nStopping face recognition...")
        
        finally:
            camera.release()
            cv2.destroyAllWindows()
            print("Camera released and windows closed")
            self.close_serial()
    
    def close_serial(self):
        """Close the serial connection safely"""
        if hasattr(self, 'serial_port') and self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
            print("Serial port closed.")

if __name__ == "__main__":
    print("Face Recognition Attendance System")
    print("===================================")
    
    attendance_system = ConsoleAttendanceSystem()
    print(f"Files location: {os.path.abspath(attendance_system.uploads_dir)}")
    
    attendance_system.start_face_recognition()
