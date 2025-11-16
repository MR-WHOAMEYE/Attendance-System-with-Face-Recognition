# Attendance System with Face Recognition

A real-time attendance tracking system that uses facial recognition technology to automatically mark attendance. The system consists of three main components: a Flask web application for face enrollment and management, a PC-based face recognition module for automatic attendance marking, and a Raspberry Pi Pico with LCD display for visual feedback.

## Features

### Web Application (Flask)
- **User-Friendly Interface**: Easy-to-use web interface for system management
- **Face Enrollment**: Add new people to the system using uploaded images or camera capture
- **Person Management**: View, add, and remove registered persons
- **Attendance Dashboard**: Real-time view of attendance records
- **Image Upload Support**: Supports PNG, JPG, and JPEG formats
- **Base64 Camera Integration**: Capture faces directly from browser camera
- **RESTful API**: JSON endpoints for system integration
- **Records Management**: Option to remove person with or without their attendance history

### Face Recognition System (PC)
- **Real-time Face Detection and Recognition**: Uses OpenCV and face_recognition library for accurate facial identification
- **Automatic Attendance Marking**: Automatically logs attendance when a known face is detected
- **Duplicate Prevention**: Implements a 30-second cooldown to prevent duplicate entries
- **Persistent Storage**: Saves face encodings and attendance logs in CSV format
- **Serial Communication**: Sends recognition data to Raspberry Pi Pico display via COM port
- **Webcam Integration**: Live video feed with visual face detection boxes
- **Confidence Scoring**: Shows recognition confidence level for each detection

### Display System (Raspberry Pi Pico)
- **LCD Display**: 16x2 I2C LCD for real-time information display
- **Boot Animation**: Professional startup sequence
- **Clock Display**: Shows current time and date when idle
- **Recognition Alerts**: Visual confirmation when attendance is marked
- **Serial Communication**: Receives data from PC via USB serial connection
- **State Machine**: Efficient state management for smooth transitions

## System Requirements

### PC Requirements
- Python 3.7 or higher
- Webcam (built-in or USB)
- Windows/Linux/macOS
- Serial port (USB) for Pico communication

### Python Dependencies
```
flask
opencv-python
face-recognition
numpy
pandas
pyserial
Pillow
```

### Hardware Requirements
- Raspberry Pi Pico
- 16x2 LCD Display with I2C module
- USB cable for Pico connection
- Jumper wires for LCD connection

### LCD I2C Wiring (Pico)
- SDA → GPIO 0 (Pin 1)
- SCL → GPIO 1 (Pin 2)
- VCC → VBUS (5V) or 3.3V
- GND → GND

## Installation

### 1. PC Setup

#### Install Python Dependencies
```bash
pip install flask
pip install opencv-python
pip install face-recognition
pip install numpy
pip install pandas
pip install pyserial
pip install Pillow
```

**Note**: The `face-recognition` library requires dlib, which may need additional setup:
- **Windows**: May require Visual Studio C++ build tools
- **Linux**: Install with `sudo apt-get install cmake`
- **macOS**: Install with `brew install cmake`

#### Clone the Repository
```bash
git clone https://github.com/MR-WHOAMEYE/Attendance-System-with-Face-Recognition.git
cd Attendance-System-with-Face-Recognition
```

### 2. Raspberry Pi Pico Setup

#### Install MicroPython
1. Download MicroPython firmware for Raspberry Pi Pico from [micropython.org](https://micropython.org/download/rp2-pico/)
2. Hold the BOOTSEL button while connecting Pico to PC
3. Copy the .uf2 file to the RPI-RP2 drive

#### Upload Pico Files
Upload all files from the `pico/` directory to your Raspberry Pi Pico:
- `main.py` - Main program entry point
- `lcd_i2c.py` - LCD driver
- `animations.py` - Display animations
- `display_manager.py` - Display state management
- `serial_handler.py` - Serial communication handler
- `blink.py` - LED blink utility

You can use tools like Thonny, ampy, or VS Code with Pico extension to upload files.

## Usage

### First-Time Setup

1. **Enroll Faces Using Web Interface**: Start by running the web application to add known faces to the system.

2. **Connect Hardware**: 
   - Connect the Raspberry Pi Pico to your PC via USB (COM5 by default)
   - Ensure the LCD is properly wired to the Pico

3. **Check Serial Port**: Verify the COM port in `main.py` (line 33):
   ```python
   self.serial_port = serial.Serial('COM5', 115200, timeout=1)
   ```
   Adjust the port name if necessary (e.g., '/dev/ttyUSB0' on Linux, '/dev/cu.usbmodem*' on macOS).

### Running the System

The system can be run in two modes:

#### Mode 1: Web Application (For Face Enrollment and Management)

Start the Flask web server:
```bash
python app.py
```

The web interface will be available at `http://localhost:5000`

**Web Application Features:**
- **Add Person**: Upload an image or use camera to capture and enroll a new face
- **View Registered Persons**: See all people registered in the system
- **Remove Person**: Delete a person from the system (with or without attendance records)
- **Attendance Dashboard**: View all attendance records in real-time
- **Recent Attendance**: Monitor today's attendance markings

#### Mode 2: Automatic Face Recognition (For Attendance Marking)

First, start the Pico Display:
1. Power on or reset the Raspberry Pi Pico
2. The LCD will show a boot animation followed by a clock display
3. Wait for "THARAN" status message (indicates ready state)

Then, run the face recognition system:
```bash
python main.py
```

The system will:
- Load existing face encodings
- Open the webcam
- Start detecting and recognizing faces
- Display live video feed with detection boxes
- Automatically mark attendance when known faces are detected
- Send recognition data to the Pico display

### Keyboard Controls (Face Recognition Mode)
- Press `q` to quit the application
- Press `s` to save the current frame as an image

### Data Storage

The system creates an `uploads/` directory with the following files:
- `face_encodings.pkl` - Stored face encodings and names
- `attendance_log.csv` - Attendance records with Name, Date, Time, and Status
- `capture_*.jpg` - Saved camera frames (when pressing 's')

### Recommended Workflow

1. **Initial Setup**: Run `python app.py` and use the web interface to enroll all faces
2. **Daily Operation**: Run `python main.py` for automatic attendance marking
3. **Management**: Keep the web interface open to monitor attendance in real-time
4. **Review**: Use the web interface to view and export attendance records

## Project Structure

```
Attendance-System-with-Face-Recognition/
│
├── app.py                      # Flask web application for face enrollment
├── main.py                     # PC-based face recognition system
│
├── templates/                  # HTML templates for web interface
│   └── index.html              # Main web interface
│
├── pico/                       # Raspberry Pi Pico files
│   ├── main.py                 # Pico main program
│   ├── lcd_i2c.py              # LCD I2C driver
│   ├── animations.py           # Display animations
│   ├── display_manager.py      # Display state management
│   ├── serial_handler.py       # Serial communication
│   └── blink.py                # LED utilities
│
└── uploads/                    # Generated data directory
    ├── face_encodings.pkl      # Face data
    ├── attendance_log.csv      # Attendance records
    └── capture_*.jpg           # Saved frames
```

## Configuration

### Face Recognition Parameters

In `main.py`, you can adjust:
- `tolerance` (line 184): Recognition sensitivity (default: 0.6, lower = stricter)
- `confidence` threshold (line 200): Minimum confidence for attendance (default: 0.4)
- `recognition_cooldown` (line 22): Seconds between duplicate recognitions (default: 30)

### Serial Communication

- Baud rate: 115200
- Message format: `RECOGNIZE|Name|Time|Status\n`
- Default port: COM5 (Windows)

### Display Settings

In `pico/main.py`:
- `recognition_display_duration` (line 32): How long to show recognition (default: 6 seconds)
- `clock_update_interval` (line 36): Clock refresh rate (default: 1 second)

## Troubleshooting

### Common Issues

#### "Error opening serial port COM5"
- Check if Pico is connected to the correct port
- Verify no other application is using the serial port
- Update the port name in main.py line 33

#### "No known faces in the system"
- Run `python app.py` and use the web interface to add people first
- The system requires `face_encodings.pkl` file with at least one face
- Upload clear, well-lit face images for best results

#### "LCD not found!"
- Check I2C wiring (SDA, SCL, VCC, GND)
- Verify LCD I2C address (common: 0x27, 0x3F)
- Test with I2C scanner code

#### "Could not open camera"
- Check if webcam is connected
- Verify no other application is using the camera
- Try a different camera index: `cv2.VideoCapture(1)` instead of `VideoCapture(0)`

#### Face recognition is slow
- The system processes every other frame for performance
- Reduce video resolution in main.py (lines 158-160)
- Ensure adequate lighting for better detection

#### Web application won't start
- Check if port 5000 is already in use
- Ensure Flask is installed: `pip install flask`
- Check for any error messages in the console

#### "No face found in the image" when adding person
- Ensure the image contains a clear, visible face
- Use well-lit images with the face clearly visible
- Try a different image or use the camera capture feature

## Adding New People

### Using the Web Application (Recommended)
1. Start the web application: `python app.py`
2. Open your browser to `http://localhost:5000`
3. Use the "Add Person" interface:
   - Enter the person's name
   - Either upload an image file (PNG, JPG, JPEG) or capture from camera
   - Click "Add Person"
4. The system will automatically:
   - Detect faces in the image
   - Generate face encodings
   - Save to `face_encodings.pkl`
   - Make the person available for recognition

### Manual Method (Advanced)
If you prefer to add people programmatically:
1. Capture face images of the person
2. Generate face encodings using face_recognition library
3. Add the encodings to `face_encodings.pkl` with the person's name
4. The system will automatically load the updated encodings

## Web API Endpoints

The Flask application provides the following RESTful API endpoints:

### POST `/add_person`
Add a new person to the system
- **Parameters**: 
  - `name` (string): Person's name
  - `file` (file): Image file, or
  - `image_data` (base64 string): Base64-encoded image
- **Response**: JSON with success status and message

### POST `/remove_person`
Remove a person from the system
- **Parameters**: 
  - `name` (string): Person's name
  - `remove_records` (boolean): Whether to delete attendance records
- **Response**: JSON with success status and message

### GET `/get_attendance`
Retrieve all attendance records
- **Response**: JSON array of attendance records

### GET `/get_known_persons`
Get list of all registered persons
- **Response**: JSON array of person names

### GET `/get_recent_attendance`
Get today's attendance records
- **Response**: JSON array of today's attendance records

## Serial Protocol

Messages sent from PC to Pico:
- `TIME|HH:MM:SS|DD/MM/YY` - Update display time
- `RECOGNIZE|Name|HH:MM:SS|IN` - Face recognized
- `COMMAND|REBOOT` - Reboot display system
- `COMMAND|CLEAR` - Clear display

## Performance Notes

- Face detection uses HOG (Histogram of Oriented Gradients) model for speed
- Frames are downscaled to 1/4 size (0.25) for faster processing
- Only every other frame is processed for face recognition
- Camera captures at 640x480 @ 20fps

## Credits

**Made by THARAN**

This project combines computer vision, embedded systems, and serial communication to create a practical attendance tracking solution.

## License

This project is open source and available for educational and personal use.

## Future Enhancements

Potential improvements:
- ~~Web interface for face enrollment~~ ✅ (Implemented)
- User authentication and role-based access
- Database integration (MySQL/PostgreSQL)
- Multiple camera support
- Advanced reporting and analytics
- Email notifications
- Export attendance to Excel/PDF
- Cloud storage for attendance records
- Mobile app integration
- Temperature sensing (for health monitoring)
- Access control integration
- Bulk face enrollment
- Face verification with confidence threshold settings

## Support

For issues, questions, or contributions, please open an issue on the GitHub repository.
