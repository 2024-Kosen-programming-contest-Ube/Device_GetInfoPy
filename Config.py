import os

class Config:
    def __init__(self, filename):
        self.save_interval = 30
        self.send_interval = 30
        self.load_config(filename)

    def load_config(self, filename):
        if not os.path.exists(filename):
            raise FileNotFoundError(f"Config file {filename} not found")
        
        with open(filename, 'r') as file:
            for line in file:
                line = line.strip()
                if line and not line.startswith("#"):
                    key, value = map(str.strip, line.split('=', 1))
                    setattr(self, key, int(value))