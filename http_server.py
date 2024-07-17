from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
import time
import sensor

class RequestHandler(BaseHTTPRequestHandler):
    sensor=sensor.Sensor()
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
        else:
            self.send_response(405)
            self.end_headers()
            self.wfile.write(b"Method Not Allowed")

    def handle_getinfo_request(self):
        info = {
            "temperature": 42.0,
            "humidity": 70,
            "isPeople": self.sensor.getMotion(),
            "lux":self.sensor.getLux()
        }
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

        filename = time.strftime("./datalog/%Y-%m-%d_data_log.txt", requested_time)
        if not os.path.exists(filename):
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")
            return

        closest_data = None
        closest_time = None
        with open(filename, "r") as file:
            for line in file:
                log_time_str, log_data = line.split(" ", 1)
                log_time = time.strptime(log_time_str, "%Y-%m-%d-%H:%M:%S")
                log_timestamp = time.mktime(log_time)

                if closest_time is None or abs(log_timestamp - requested_timestamp) < abs(closest_time - requested_timestamp):
                    closest_time = log_timestamp
                    closest_data = log_data

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

def run_server():
    server_address = ('', 5000)
    httpd = HTTPServer(server_address, RequestHandler)
    print("Server running on port 5000")
    httpd.serve_forever()

# Example usage
if __name__ == "__main__":
    run_server()
