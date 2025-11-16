import time
from machine import RTC

class DisplayManager:
    def __init__(self, lcd, animations):
        self.lcd = lcd
        self.animations = animations
        self.rtc = RTC()
        self.last_second = -1
        
        # Set initial time if not set (placeholder)
        # In real implementation, sync with PC time
        self.rtc.datetime((2025, 8, 13, 4, 8, 0, 0, 0))  # (year, month, day, weekday, hour, min, sec, subsec)
    
    def update_time_from_pc(self, time_string, date_string):
        """Update RTC with time from PC"""
        try:
            # Parse time string "14:35:42"
            time_parts = time_string.split(":")
            hour = int(time_parts[0])
            minute = int(time_parts[1])
            second = int(time_parts[2])
            
            # Parse date string "08/08/24"
            date_parts = date_string.split("/")
            day = int(date_parts[0])
            month = int(date_parts[1])
            year = 2000 + int(date_parts[2])
            
            # Update RTC
            current = self.rtc.datetime()
            self.rtc.datetime((year, month, day, current[3], hour, minute, second, 0))
            
        except Exception as e:
            print(f"Time update error: {e}")
    
    def format_time(self):
        """Format current time for display"""
        current = self.rtc.datetime()
        hour = current[4]
        minute = current[5]
        second = current[6]
        
        # Format as HH:MM:SS
        return f"{hour:02d}:{minute:02d}:{second:02d}"
    
    def format_date(self):
        """Format current date for display"""
        current = self.rtc.datetime()
        day = current[2]
        month = current[1]
        year = current[0] % 100  # Last 2 digits
        
        return f"{day:02d}/{month:02d}/{year:02d}"
    
    def show_clock(self):
        """Display current time and date"""
        current_time = self.format_time()
        current_date = self.format_date()
        
        # Only update if second changed (reduces flicker)
        current_second = self.rtc.datetime()[6]
        if current_second != self.last_second:
            self.lcd.print_line(f"Time: {current_time}", 0)
            self.lcd.print_line(f"Date: {current_date}", 1)
            self.last_second = current_second
    
    def show_recognition(self, name, time_str, status):
        """Display recognition information with animation"""
        # Stage 1: Recognition alert
        self.lcd.clear()
        self.lcd.print_line("RECOGNIZED!", 0, center=True)
        self.lcd.print_line("Please wait...", 1, center=True)
        time.sleep(1)
        
        # Stage 2: Show name and time
        self.lcd.clear()
        name_display = name[:16]  # Truncate if too long
        time_display = f"{status} {time_str}"
        
        self.lcd.print_line(name_display, 0, center=True)
        self.lcd.print_line(time_display, 1, center=True)
        time.sleep(3)
        
        # Stage 3: Confirmation
        self.lcd.clear()
        self.lcd.print_line("Attendance", 0, center=True)
        self.lcd.set_cursor(6, 1)
        self.lcd.print("Marked ")
        self.lcd.write_data(0)  # Checkmark character
        time.sleep(2)
    
    def show_error(self, error_msg):
        """Display error message"""
        self.lcd.clear()
        self.lcd.print_line("ERROR:", 0)
        self.lcd.print_line(error_msg[:16], 1)
        time.sleep(3)
    
    """def show_status(self, status_msg):
        Display status message
        self.lcd.clear()
        self.lcd.print_line("Status:", 0)
        self.lcd.print_line(status_msg[:16], 1)
        time.sleep(2)"""
    def show_status(self, status_msg):
        """Display  message"""
        self.lcd.clear()
        self.lcd.print_line("Made by", 0)
        self.lcd.print_line("  THARAN", 1)
        time.sleep(2)
