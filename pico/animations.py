# ===============================================
# File: animations.py
# Boot Animations and Transitions
# ===============================================

import time

class Animations:
    def __init__(self, lcd):
        self.lcd = lcd
        self.setup_custom_chars()
    
    def setup_custom_chars(self):
        """Create custom characters for animations"""
        # Checkmark character (location 0)
        checkmark = [
            0b00000,
            0b00001,
            0b00011,
            0b10110,
            0b11100,
            0b01000,
            0b00000,
            0b00000
        ]
        
        # X mark character (location 1)
        x_mark = [
            0b00000,
            0b10001,
            0b01010,
            0b00100,
            0b01010,
            0b10001,
            0b00000,
            0b00000
        ]
        
        # Clock character (location 2)
        clock = [
            0b00000,
            0b01110,
            0b10101,
            0b10101,
            0b10001,
            0b01110,
            0b00000,
            0b00000
        ]
        
        # Heart character (location 3)
        heart = [
            0b00000,
            0b01010,
            0b11111,
            0b11111,
            0b01110,
            0b00100,
            0b00000,
            0b00000
        ]
        
        # Full block character (location 4)
        block = [
            0b11111,
            0b11111,
            0b11111,
            0b11111,
            0b11111,
            0b11111,
            0b11111,
            0b11111
        ]
        
        self.lcd.create_char(0, checkmark)
        self.lcd.create_char(1, x_mark)
        self.lcd.create_char(2, clock)
        self.lcd.create_char(3, heart)
        self.lcd.create_char(4, block)  # New block character
    
    def boot_sequence(self):
        """Complete boot animation sequence"""
        self.lcd.clear()
        
        # Step 1: Welcome message
        self.lcd.print_line("Face Recognition", 0, center=True)
        self.lcd.print_line("System", 1, center=True)
        time.sleep(2)
        
        # Step 2: Loading animation
        self.loading_animation()
        
        # Step 3: System ready
        self.lcd.clear()
        self.lcd.print_line("System Ready!", 0, center=True)
        self.lcd.set_cursor(7, 1)
        self.lcd.write_data(0)  # Show checkmark
        time.sleep(1)
        
        # Step 4: Transition to clock
        self.slide_transition("Starting Clock...")
    
    def loading_animation(self):
        """Animated loading bar"""
        self.lcd.clear()
        self.lcd.print_line("Loading...", 0, center=True)
        
        # Progress bar using custom block character (\x04)
        progress_chars = [
            "[        ]",
            "[\x04       ]",
            "[\x04\x04      ]",
            "[\x04\x04\x04     ]",
            "[\x04\x04\x04\x04    ]",
            "[\x04\x04\x04\x04\x04   ]",
            "[\x04\x04\x04\x04\x04\x04  ]",
            "[\x04\x04\x04\x04\x04\x04\x04 ]",
            "[\x04\x04\x04\x04\x04\x04\x04\x04]"
        ]
        
        for i, progress in enumerate(progress_chars):
            self.lcd.print_line(progress, 1, center=True)
            time.sleep(0.3)
    
    def slide_transition(self, message):
        """Slide text across screen"""
        # Ensure message is a string
        if not isinstance(message, str):
            print(f"Warning: Non-string message in slide_transition: {message} (type: {type(message)})")
            message = str(message) if message is not None else ""
        
        # Clear and show message sliding in from right
        spaces = " " * 16
        full_text = spaces + message + spaces
        
        for i in range(len(full_text) - 15):
            self.lcd.clear()
            self.lcd.print_line(full_text[i:i+16], 0)
            time.sleep(0.1)
        
        time.sleep(0.5)
    
    def fade_effect(self, old_text, new_text, line=0):
        """Simple fade effect by alternating text"""
        for _ in range(3):
            self.lcd.print_line(" " * 16, line)
            time.sleep(0.1)
            self.lcd.print_line(old_text, line)
            time.sleep(0.1)
        
        for _ in range(3):
            self.lcd.print_line(" " * 16, line)
            time.sleep(0.1)
            self.lcd.print_line(new_text, line)
            time.sleep(0.1)
