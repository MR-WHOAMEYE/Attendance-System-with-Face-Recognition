# ===============================================
# File: lcd_i2c.py
# LCD I2C Driver for 16x2 Display
# ===============================================

from machine import I2C, Pin
import time

class LCD_I2C:
    def __init__(self, i2c, addr=0x27, rows=2, cols=16):
        self.i2c = i2c
        self.addr = addr
        self.rows = rows
        self.cols = cols
        
        # LCD Commands
        self.LCD_CLEARDISPLAY = 0x01
        self.LCD_RETURNHOME = 0x02
        self.LCD_ENTRYMODESET = 0x04
        self.LCD_DISPLAYCONTROL = 0x08
        self.LCD_CURSORSHIFT = 0x10
        self.LCD_FUNCTIONSET = 0x20
        self.LCD_SETCGRAMADDR = 0x40
        self.LCD_SETDDRAMADDR = 0x80
        
        # Flags for display entry mode
        self.LCD_ENTRYRIGHT = 0x00
        self.LCD_ENTRYLEFT = 0x02
        self.LCD_ENTRYSHIFTINCREMENT = 0x01
        self.LCD_ENTRYSHIFTDECREMENT = 0x00
        
        # Flags for display on/off control
        self.LCD_DISPLAYON = 0x04
        self.LCD_DISPLAYOFF = 0x00
        self.LCD_CURSORON = 0x02
        self.LCD_CURSOROFF = 0x00
        self.LCD_BLINKON = 0x01
        self.LCD_BLINKOFF = 0x00
        
        # Flags for function set
        self.LCD_8BITMODE = 0x10
        self.LCD_4BITMODE = 0x00
        self.LCD_2LINE = 0x08
        self.LCD_1LINE = 0x00
        self.LCD_5x10DOTS = 0x04
        self.LCD_5x8DOTS = 0x00
        
        # Flags for backlight control
        self.LCD_BACKLIGHT = 0x08
        self.LCD_NOBACKLIGHT = 0x00
        
        self.En = 0b00000100  # Enable bit
        self.Rw = 0b00000010  # Read/Write bit
        self.Rs = 0b00000001  # Register select bit
        
        self.init()
    
    def init(self):
        """Initialize the LCD"""
        time.sleep_ms(50)
        
        # Initialize in 4-bit mode
        self.write4bits(0x03 << 4)
        time.sleep_ms(5)
        self.write4bits(0x03 << 4)
        time.sleep_ms(5)
        self.write4bits(0x03 << 4)
        time.sleep_us(150)
        self.write4bits(0x02 << 4)
        
        # Function set: 4-bit mode, 2 lines, 5x8 dots
        self.command(self.LCD_FUNCTIONSET | self.LCD_4BITMODE | self.LCD_2LINE | self.LCD_5x8DOTS)
        
        # Display control: display on, cursor off, blink off
        self.command(self.LCD_DISPLAYCONTROL | self.LCD_DISPLAYON | self.LCD_CURSOROFF | self.LCD_BLINKOFF)
        
        # Clear display
        self.clear()
        
        # Entry mode: left to right
        self.command(self.LCD_ENTRYMODESET | self.LCD_ENTRYLEFT | self.LCD_ENTRYSHIFTDECREMENT)
        
        time.sleep_ms(2)
    
    def write4bits(self, data):
        """Write 4 bits to the LCD"""
        self.i2c.writeto(self.addr, bytearray([data | self.LCD_BACKLIGHT]))
        self.pulse_enable(data)
    
    def pulse_enable(self, data):
        """Pulse the enable pin"""
        self.i2c.writeto(self.addr, bytearray([data | self.En | self.LCD_BACKLIGHT]))
        time.sleep_us(1)
        self.i2c.writeto(self.addr, bytearray([data & ~self.En | self.LCD_BACKLIGHT]))
        time.sleep_us(50)
    
    def command(self, cmd):
        """Send command to LCD"""
        self.write4bits(cmd & 0xF0)
        self.write4bits((cmd << 4) & 0xF0)
    
    def write_data(self, data):
        """Write data to LCD"""
        self.write4bits(self.Rs | (data & 0xF0))
        self.write4bits(self.Rs | ((data << 4) & 0xF0))
    
    def clear(self):
        """Clear the LCD"""
        self.command(self.LCD_CLEARDISPLAY)
        time.sleep_ms(2)
    
    def home(self):
        """Return cursor to home"""
        self.command(self.LCD_RETURNHOME)
        time.sleep_ms(2)
    
    def set_cursor(self, col, row):
        """Set cursor position"""
        row_offsets = [0x00, 0x40]
        self.command(self.LCD_SETDDRAMADDR | (col + row_offsets[row]))
    
    def print(self, text):
        """Print text to LCD"""
        for char in str(text):
            self.write_data(ord(char))
    
    def print_line(self, text, line=0, center=False):
        """Print text on specific line"""
        # Ensure text is a string and log details for debugging
        if not isinstance(text, str):
            print(f"Warning: Non-string text passed to print_line: {text} (type: {type(text)})")
            text = str(text) if text is not None else ""
        
        self.set_cursor(0, line)
        try:
            if center:
                text = text.center(self.cols)
            else:
                # Try using ljust, with fallback if it fails
                try:
                    text = text.ljust(self.cols)
                except AttributeError as e:
                    print(f"Error: ljust failed on text: '{text}' (type: {type(text)})")
                    # Manual left-justification
                    text = text + " " * (self.cols - len(text))
        except Exception as e:
            print(f"Error in print_line formatting: {e}")
            text = text[:self.cols]  # Fallback to truncation
        self.print(text[:self.cols])
    
    def create_char(self, location, charmap):
        """Create custom character"""
        location &= 0x7
        self.command(self.LCD_SETCGRAMADDR | (location << 3))
        for i in range(8):
            self.write_data(charmap[i])
