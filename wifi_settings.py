import subprocess

def scan_wifi():
    # nmcliを使ってWiFiネットワークをスキャン
    result = subprocess.run(['sudo', 'nmcli', 'device', 'wifi', 'list'], capture_output=True, text=True)
    return result.stdout

def connect_to_wifi(ssid, password):
    # nmcliを使ってWiFiに接続
    try:
        # WiFi接続コマンド
        connect_cmd = ['sudo', 'nmcli', 'device', 'wifi', 'connect', ssid, 'password', password]
        result = subprocess.run(connect_cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Connected to {ssid} successfully!")
        else:
            print(f"Failed to connect to {ssid}. Error: {result.stderr}")
    except Exception as e:
        print(f"Error occurred: {str(e)}")

def main():
    # スキャンしてWiFiネットワーク一覧を表示
    print("Scanning for available WiFi networks...")
    networks = scan_wifi()
    print(networks)
    
    # ユーザーに接続したいSSIDを入力させる
    ssid = input("Enter the SSID of the WiFi network you want to connect to: ")
    password = input(f"Enter the password for {ssid}: ")
    
    # WiFiに接続
    connect_to_wifi(ssid, password)

if __name__ == "__main__":
    main()
