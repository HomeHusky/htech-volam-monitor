"""
Script giữ cho Render web service không sleep
Ping website mỗi 10 phút
Chạy script này trên máy local hoặc server 24/7
"""

import requests
import time
from datetime import datetime

# URL của website trên Render
WEBSITE_URL = "https://your-app.onrender.com/health"  # Thay bằng URL thực của bạn

# Ping interval (seconds) - 10 phút
PING_INTERVAL = 600  # 10 minutes = 600 seconds

def ping_website():
    """Ping website để giữ nó không sleep"""
    try:
        response = requests.get(WEBSITE_URL, timeout=30)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if response.status_code == 200:
            print(f"✅ [{timestamp}] Ping thành công - Status: {response.status_code}")
            return True
        else:
            print(f"⚠️ [{timestamp}] Ping thất bại - Status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"❌ [{timestamp}] Lỗi kết nối: {e}")
        return False

def main():
    """Main loop"""
    print("=" * 60)
    print("🚀 RENDER KEEP ALIVE SERVICE")
    print("=" * 60)
    print(f"📡 Target URL: {WEBSITE_URL}")
    print(f"⏰ Ping interval: {PING_INTERVAL} seconds ({PING_INTERVAL/60} minutes)")
    print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print("\nPress Ctrl+C to stop\n")
    
    while True:
        try:
            ping_website()
            time.sleep(PING_INTERVAL)
        except KeyboardInterrupt:
            print("\n\n⛔ Stopped by user")
            break
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            time.sleep(60)  # Wait 1 minute before retry

if __name__ == "__main__":
    main()
