from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
import time
import subprocess
import bisect
from urllib.parse import parse_qs, urlparse
from sensor import Sensor, setLEDColor

class RequestHandler(BaseHTTPRequestHandler):
    sensor = Sensor()

    def do_GET(self):
        if self.path == "/data/getinfo":
            self.handle_getinfo_request()
        elif self.path.startswith("/data/"):
            time_str = self.path.split("time=", 1)[1] if "time=" in self.path else None
            if time_str:
                self.handle_time_request(time_str)
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Bad Request")
        elif self.path == "/wifi/getinfo":
            self.handle_getwifiinfo_request()
        elif self.path.startswith("/wifi/connect"):
            self.handle_wifi_connect_request()
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")

    def handle_getinfo_request(self):
        temperature, humidity = self.sensor.getEnviroment()
        airconditioner, ontime = self.sensor.getAirConditioner()
        info = {
            "temperature": temperature,
            "humidity": humidity,
            "isPeople": self.sensor.getMotion(),
            "lux": self.sensor.getLux(),
            "useairconditioner": airconditioner,
            "airconditioner_time": ontime
        }
        self.sensor.setBlinkLED(setLEDColor.PURPLE, 3)
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(info).encode())

    def handle_time_request(self, time_str):
        try:
            requested_time = time.strptime(time_str, "%Y-%m-%d-%H:%M:%S")
            requested_timestamp = time.mktime(requested_time)
        except ValueError:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Bad Request")
            return
        current_path = os.getcwd()
        filename = time.strftime(f"{current_path}/datalog/%Y-%m-%d_data_log.txt", requested_time)
        if not os.path.exists(filename):
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")
            return

        with open(filename, "r") as file:
            lines = file.readlines()
        
        timestamps = []
        data = []
        for line in lines:
            log_time_str, log_data = line.split(" ", 1)
            log_time = time.strptime(log_time_str, "%Y-%m-%d-%H:%M:%S")
            log_timestamp = time.mktime(log_time)
            timestamps.append(log_timestamp)
            data.append(log_data)

        pos = bisect.bisect_left(timestamps, requested_timestamp)
        
        closest_time = None
        closest_data = None
        
        if pos == 0:
            closest_time = timestamps[0]
            closest_data = data[0]
        elif pos == len(timestamps):
            closest_time = timestamps[-1]
            closest_data = data[-1]
        else:
            before = timestamps[pos - 1]
            after = timestamps[pos]
            if abs(before - requested_timestamp) <= abs(after - requested_timestamp):
                closest_time = before
                closest_data = data[pos - 1]
            else:
                closest_time = after
                closest_data = data[pos]

        if closest_data:
            response = {
                "closest_time": time.strftime("%Y-%m-%d-%H:%M:%S", time.localtime(closest_time)),
                "data": json.loads(closest_data)
            }
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")

    def handle_getwifiinfo_request(self):
        try:
            result = subprocess.run(['nmcli', '-t', '-f', 'SSID,SIGNAL', 'device', 'wifi'], capture_output=True, text=True)
            if result.returncode == 0:
                wifi_networks = result.stdout.strip().split("\n")
                networks = []
                for network in wifi_networks:
                    ssid, signal = network.split(":")
                    networks.append({"ssid": ssid, "signal_strength": signal})
                
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(networks).encode())
            else:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(b"Failed to scan WiFi networks")
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f"Error: {str(e)}".encode())

    def handle_wifi_connect_request(self):
        parsed_url = urlparse(self.path)
        params = parse_qs(parsed_url.query)
        ssid = params.get("ssid", [None])[0]
        password = params.get("password", [None])[0]

        if ssid and password:
            self.handle_connect_request(ssid, password)
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Bad Request: SSID and password required")

    def handle_connect_request(self, ssid, password):
        try:
            result = subprocess.run(['nmcli', 'device', 'wifi', 'connect', ssid, 'password', password], capture_output=True, text=True)
            if result.returncode == 0:
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "connected", "ssid": ssid}).encode())
            else:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(f"Failed to connect to {ssid}: {result.stderr}".encode())
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f"Error: {str(e)}".encode())

def run_server():
    server_address = ('', 5000)
    httpd = HTTPServer(server_address, RequestHandler)
    print("Server running on port 5000")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()
