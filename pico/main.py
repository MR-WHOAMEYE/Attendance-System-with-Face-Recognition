from machine import I2C, Pin
import time
import sys

# Import our modules
from lcd_i2c import LCD_I2C
from animations import Animations
from display_manager import DisplayManager
from serial_handler import SerialHandler

class AttendanceDisplay:
    def __init__(self):
        # Hardware setup
        self.i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
        
        # Find LCD address
        self.lcd_addr = self.find_lcd_address()
        if self.lcd_addr is None:
            print("LCD not found!")
            return
        
        # Initialize components
        self.lcd = LCD_I2C(self.i2c, self.lcd_addr)
        self.animations = Animations(self.lcd)
        self.display = DisplayManager(self.lcd, self.animations)
        self.serial = SerialHandler()
        
        # State management
        self.state = 'BOOT'
        self.last_recognition_time = 0
        self.recognition_display_duration = 6  # seconds
        self.recognition_data = None
        
        # Timing
        self.last_clock_update = 0
        self.clock_update_interval = 1  # seconds
        
        print("Attendance Display System Initialized")
        print(f"LCD found at address: 0x{self.lcd_addr:02X}")
    
    def find_lcd_address(self):
        """Scan I2C bus for LCD"""
        devices = self.i2c.scan()
        print(f"I2C devices found: {[hex(device) for device in devices]}")
        
        # Common LCD addresses
        common_addresses = [0x27, 0x3F, 0x26, 0x20]
        
        for addr in common_addresses:
            if addr in devices:
                return addr
        
        # Return first found device if no common address found
        return devices[0] if devices else None
    
    def run(self):
        """Main state machine loop"""
        print("Starting main loop...")
        
        while True:
            try:
                current_time = time.time()
                
                # Check for serial messages
                message = self.serial.check_for_data()
                if message:
                    self.handle_message(message)
                
                # State machine
                if self.state == 'BOOT':
                    self.handle_boot_state()
                    
                elif self.state == 'CLOCK':
                    self.handle_clock_state(current_time)
                    
                elif self.state == 'RECOGNITION':
                    self.handle_recognition_state(current_time)
                    
                elif self.state == 'TRANSITION':
                    self.handle_transition_state()
                
                # Small delay to prevent overwhelming the system
                time.sleep(0.1)
                
            except KeyboardInterrupt:
                print("\nShutting down...")
                self.lcd.clear()
                self.lcd.print_line("System Shutdown", 0, center=True)
                break
                
            except Exception as e:
                print(f"Error in main loop: {e}")
                self.display.show_error("System Error")
                time.sleep(2)
                self.state = 'CLOCK'  # Recovery
    
    def handle_message(self, message):
        """Handle incoming serial messages"""
        if message['type'] == 'TIME':
            self.display.update_time_from_pc(message['time'], message['date'])
            
        elif message['type'] == 'RECOGNIZE':
            self.recognition_data = message
            self.last_recognition_time = time.time()
            self.state = 'RECOGNITION'
            self.serial.send_status("RECEIVED")
            
        elif message['type'] == 'COMMAND':
            self.handle_command(message['command'])
    
    def handle_command(self, command):
        """Handle system commands"""
        if command == 'REBOOT':
            self.state = 'BOOT'
        elif command == 'TEST':
            self.display.show_status("Test Mode")
        elif command == 'CLEAR':
            self.lcd.clear()
    
    def handle_boot_state(self):
        """Handle boot animation state"""
        print("Running boot sequence...")
        self.animations.boot_sequence()
        self.state = 'CLOCK'
        print("Boot complete, switching to clock")
    
    def handle_clock_state(self, current_time):
        """Handle clock display state"""
        # Update clock display
        if current_time - self.last_clock_update >= self.clock_update_interval:
            self.display.show_clock()
            self.last_clock_update = current_time
        
        # Check connection status
        if not self.serial.is_connected():
            # Show disconnected status periodically
            if int(current_time) % 30 == 0:  # Every 30 seconds
                self.display.show_status("THARAN")
                time.sleep(1)
    
    def handle_recognition_state(self, current_time):
        """Handle recognition display state"""
        if self.recognition_data:
            self.display.show_recognition(
                self.recognition_data['name'],
                self.recognition_data['time'],
                self.recognition_data['status']
            )
            self.recognition_data = None
        
        # Check if display time is over
        if current_time - self.last_recognition_time >= self.recognition_display_duration:
            self.state = 'TRANSITION'
    
    def handle_transition_state(self):
        """Handle transition back to clock"""
        self.animations.fade_effect("", "")
        self.lcd.clear()
        self.state = 'CLOCK'
        self.last_clock_update = 0  # Force immediate clock update

# ===============================================
# Program Entry Point
# ===============================================

def main():
    print("=" * 40)
    print("Face Recognition Attendance Display")
    print("Raspberry Pi Pico + LCD I2C")
    print("=" * 40)
    
    try:
        # Create and run the attendance display system
        system = AttendanceDisplay()
        if system.lcd_addr is not None:
            system.run()
        else:
            print("Failed to initialize - LCD not found")
    
    except Exception as e:
        print(f"Failed to start system: {e}")

if __name__ == "__main__":
    main()
