import sys
import select
import time

class SerialHandler:
    def __init__(self):
        self.buffer = ""
        self.last_heartbeat = time.time()
        self.heartbeat_timeout = 60  # seconds
    
    def check_for_data(self):
        """Check for incoming serial data"""
        try:
            # Check if data is available
            if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                line = sys.stdin.readline().strip()
                if line:
                    self.last_heartbeat = time.time()
                    return self.parse_message(line)
        except:
            pass
        
        return None
    
    def parse_message(self, message):
        """Parse incoming message"""
        try:
            parts = message.split('|')
            if len(parts) < 2:
                return None
            
            msg_type = parts[0]
            
            if msg_type == "TIME" and len(parts) >= 3:
                return {
                    'type': 'TIME',
                    'time': parts[1],
                    'date': parts[2]
                }
            
            elif msg_type == "RECOGNIZE" and len(parts) >= 4:
                return {
                    'type': 'RECOGNIZE',
                    'name': parts[1],
                    'time': parts[2],
                    'status': parts[3]
                }
            
            elif msg_type == "COMMAND" and len(parts) >= 2:
                return {
                    'type': 'COMMAND',
                    'command': parts[1]
                }
        
        except Exception as e:
            print(f"Parse error: {e}")
        
        return None
    
    def is_connected(self):
        """Check if PC connection is active"""
        return (time.time() - self.last_heartbeat) < self.heartbeat_timeout
    
    def send_status(self, status):
        """Send status back to PC"""
        try:
            print(f"STATUS|{status}")
        except:
            pass

