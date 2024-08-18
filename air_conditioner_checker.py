import time
import json
import os
import bisect

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
    
    # 最新のデータを取得
    latest_data = json.loads(data[-1])  # 最後のデータが最新
    latest_temp = latest_data["temperature"]

    # 30分前のタイムスタンプを計算
    time_30_min_ago = requested_timestamp - 1800  # 1800秒 = 30分
    pos_30_min_ago = bisect.bisect_left(timestamps, time_30_min_ago)
    
    if pos_30_min_ago < len(timestamps):
        closest_30_min_ago_time = timestamps[pos_30_min_ago]
        closest_30_min_ago_data = json.loads(data[pos_30_min_ago])
        temp_30_min_ago = closest_30_min_ago_data["temperature"]
    else:
        self.send_response(404)
        self.end_headers()
        self.wfile.write(b"Data 30 minutes ago not found")
        return

    # 温度差を計算
    temp_difference = latest_temp - temp_30_min_ago

    # 結果をレスポンスとして送信
    response = {
        "latest_time": time.strftime("%Y-%m-%d-%H:%M:%S", time.localtime(timestamps[-1])),
        "latest_temperature": latest_temp,
        "time_30_min_ago": time.strftime("%Y-%m-%d-%H:%M:%S", time.localtime(closest_30_min_ago_time)),
        "temperature_30_min_ago": temp_30_min_ago,
        "temperature_difference": temp_difference
    }
    self.send_response(200)
    self.send_header("Content-type", "application/json")
    self.end_headers()
    self.wfile.write(json.dumps(response).encode())
