# ===============================
# 🌐 WEB MONITOR - FLASK APP
# ===============================
"""
Web application để hiển thị trạng thái máy chủ từ MongoDB
Deploy lên Render.com
"""

from flask import Flask, render_template, jsonify, request
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime, timedelta, timezone
import os
import requests
import json

app = Flask(__name__)

# MongoDB Configuration with timezone handling
# ⚠️ IMPORTANT: Set MONGO_URI as environment variable on Render
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority')
DB_NAME = os.environ.get('DB_NAME', 'HtechVolam')
COLLECTION_NAME = os.environ.get('COLLECTION_NAME', 'server_status')

# Discord Webhook Configuration
DISCORD_WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK_URL', '')

# Collection for excluded servers
EXCLUDED_SERVERS_COLLECTION = 'excluded_servers'

# Timezone Configuration
# Use UTC to avoid timezone confusion between local and server environments
# Can be overridden with TIMEZONE environment variable (e.g., 'Asia/Ho_Chi_Minh')
TIMEZONE_STR = os.environ.get('TIMEZONE', 'UTC')
try:
    import pytz
    APP_TIMEZONE = pytz.timezone(TIMEZONE_STR)
except ImportError:
    # Fallback to UTC if pytz not available
    APP_TIMEZONE = timezone.utc
    print(f"Warning: pytz not available, using UTC. Install with: pip install pytz")
except Exception as e:
    print(f"Warning: Invalid timezone '{TIMEZONE_STR}', falling back to UTC: {e}")
    APP_TIMEZONE = timezone.utc

# Timeout threshold (minutes)
OFFLINE_THRESHOLD_MINUTES = 70


def get_mongo_collection():
    """Kết nối MongoDB và trả về collection"""
    try:
        client = MongoClient(MONGO_URI, server_api=ServerApi('1'))
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
        return collection
    except Exception as e:
        print(f" Lỗi kết nối MongoDB: {e}")
        return None


def is_server_online(last_update):
    """
    Kiểm tra máy chủ có online không dựa vào thời gian cập nhật cuối
    
    Args:
        last_update: datetime object của lần cập nhật cuối
        
    Returns:
        bool: True nếu online (cập nhật trong vòng 70 phút)
    """
    if not last_update:
        return False
    
    # Use consistent timezone for comparison
    now = datetime.now(APP_TIMEZONE)
    time_diff = now - last_update
    
    # Online nếu cập nhật trong vòng 70 phút
    return time_diff.total_seconds() < (OFFLINE_THRESHOLD_MINUTES * 60)


def get_all_servers():
    """
    Lấy danh sách tất cả máy chủ và trạng thái
    """
    collection = get_mongo_collection()
    if collection is None:
        return []
    
    try:
        servers = list(collection.find().sort("cap_nhat_luc", -1))
        result = []
        for server in servers:
            last_update = server.get('cap_nhat_luc')
            # Make last_update timezone-aware if it's naive, using consistent timezone
            if last_update and last_update.tzinfo is None:
                last_update = last_update.replace(tzinfo=APP_TIMEZONE)
            online = is_server_online(last_update)
            
            # Tính thời gian từ lần cập nhật cuối using consistent timezone
            time_ago = ""
            if last_update:
                time_diff = datetime.now(APP_TIMEZONE) - last_update
                minutes = int(time_diff.total_seconds() / 60)
                hours = int(minutes / 60)
                
                if hours > 0:
                    time_ago = f"{hours} giờ {minutes % 60} phút trước"
                else:
                    time_ago = f"{minutes} phút trước"
            
            result.append({
                'ten_may': server.get('ten_may', 'Unknown'),
                'online': online,
                'so_acc_online': server.get('so_acc_online', 0),
                'so_acc_offline': server.get('so_acc_offline', 0),
                'tong_so_acc': server.get('tong_so_acc', 0),
                'cap_nhat_luc': last_update.strftime('%Y-%m-%d %H:%M:%S') if last_update else 'N/A',
                'time_ago': time_ago
            })
        
        return result
    except Exception as e:
        print(f" Lỗi lấy dữ liệu: {e}")
        return []


@app.route('/')
def index():
    """Trang chủ hiển thị danh sách máy chủ"""
    servers = get_all_servers()
    
    # Thống kê
    total_servers = len(servers)
    online_servers = sum(1 for s in servers if s['online'])
    offline_servers = total_servers - online_servers
    total_accounts = sum(s['tong_so_acc'] for s in servers)
    total_online_accounts = sum(s['so_acc_online'] for s in servers if s['online'])
    
    stats = {
        'total_servers': total_servers,
        'online_servers': online_servers,
        'offline_servers': offline_servers,
        'total_accounts': total_accounts,
        'total_online_accounts': total_online_accounts
    }
    
    return render_template('index.html', servers=servers, stats=stats)


@app.route('/api/servers')
def api_servers():
    """API endpoint trả về JSON của tất cả máy chủ"""
    servers = get_all_servers()
    return jsonify(servers)


@app.route('/api/profit/<ten_may>')
def api_profit(ten_may):
    """API endpoint trả về báo cáo lợi nhuận cho máy cụ thể từ money_monitor collection"""
    collection = get_mongo_collection()
    if collection is None:
        return jsonify({'error': 'Không thể kết nối MongoDB'}), 500
    
    try:
        # Query the money_monitor collection for the latest entry for this ten_may
        money_collection = collection.database['money_monitor']
        report = money_collection.find_one({"ten_may": ten_may}, sort=[("time", -1)])  # Find the latest entry
        
        if report:
            return jsonify({
                'ten_may': report.get('ten_may'),
                'loi_nhuan': report.get('loi_nhuan'),
                'report': report.get('report', []),
                'time': report.get('time').isoformat() if report.get('time') else None
            })
        else:
            return jsonify({'error': f'Không tìm thấy báo cáo cho máy {ten_may}'}), 404
    except Exception as e:
        print(f" Lỗi lấy báo cáo lợi nhuận: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/all-profits')
def api_all_profits():
    """API endpoint trả về báo cáo lợi nhuận cho tất cả máy từ money_monitor collection"""
    collection = get_mongo_collection()
    if collection is None:
        return jsonify({'error': 'Không thể kết nối MongoDB'}), 500
    
    try:
        # Query the money_monitor collection for all machines
        money_collection = collection.database['money_monitor']
        
        # Get all unique machine names
        all_machines = money_collection.distinct('ten_may')
        
        results = []
        for ten_may in all_machines:
            # Get the latest report for each machine
            report = money_collection.find_one({"ten_may": ten_may}, sort=[("time", -1)])
            
            if report:
                results.append({
                    'ten_may': report.get('ten_may'),
                    'loi_nhuan': report.get('loi_nhuan', 0),
                    'report': report.get('report', []),
                    'time': report.get('time').isoformat() if report.get('time') else None
                })
        
        return jsonify(results)
    except Exception as e:
        print(f" Lỗi lấy báo cáo lợi nhuận tất cả máy: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/excluded-servers', methods=['GET'])
def get_excluded_servers():
    """Lấy danh sách máy loại trừ khỏi thông báo"""
    collection = get_mongo_collection()
    if collection is None:
        return jsonify({'error': 'Không thể kết nối MongoDB'}), 500
    
    try:
        excluded_collection = collection.database[EXCLUDED_SERVERS_COLLECTION]
        doc = excluded_collection.find_one({'_id': 'excluded_list'})
        
        if doc and 'servers' in doc:
            return jsonify({'excluded_servers': doc['servers']})
        else:
            return jsonify({'excluded_servers': []})
    except Exception as e:
        print(f"❌ Lỗi lấy danh sách máy loại trừ: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/excluded-servers', methods=['POST'])
def update_excluded_servers():
    """Cập nhật danh sách máy loại trừ khỏi thông báo"""
    collection = get_mongo_collection()
    if collection is None:
        return jsonify({'error': 'Không thể kết nối MongoDB'}), 500
    
    try:
        data = request.get_json()
        excluded_servers = data.get('excluded_servers', [])
        
        excluded_collection = collection.database[EXCLUDED_SERVERS_COLLECTION]
        excluded_collection.update_one(
            {'_id': 'excluded_list'},
            {'$set': {'servers': excluded_servers}},
            upsert=True
        )
        
        return jsonify({'success': True, 'excluded_servers': excluded_servers})
    except Exception as e:
        print(f"❌ Lỗi cập nhật danh sách máy loại trừ: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/check-offline-servers', methods=['POST'])
def check_offline_servers():
    """Kiểm tra máy offline và gửi thông báo Discord"""
    if not DISCORD_WEBHOOK_URL:
        return jsonify({'error': 'Discord webhook chưa được cấu hình'}), 400
    
    collection = get_mongo_collection()
    if collection is None:
        return jsonify({'error': 'Không thể kết nối MongoDB'}), 500
    
    try:
        # Get excluded servers
        excluded_collection = collection.database[EXCLUDED_SERVERS_COLLECTION]
        excluded_doc = excluded_collection.find_one({'_id': 'excluded_list'})
        excluded_servers = excluded_doc.get('servers', []) if excluded_doc else []
        
        # Get all servers
        servers = get_all_servers()
        
        # Find offline servers (excluding the excluded ones)
        offline_servers = []
        for server in servers:
            if not server['online'] and server['ten_may'] not in excluded_servers:
                offline_servers.append(server)
        
        # Send Discord notification if there are offline servers
        if offline_servers:
            send_discord_notification(offline_servers)
            return jsonify({
                'success': True,
                'offline_count': len(offline_servers),
                'offline_servers': [s['ten_may'] for s in offline_servers]
            })
        else:
            return jsonify({
                'success': True,
                'offline_count': 0,
                'message': 'Tất cả máy đều online'
            })
    except Exception as e:
        print(f"❌ Lỗi kiểm tra máy offline: {e}")
        return jsonify({'error': str(e)}), 500


def send_discord_notification(offline_servers):
    """Gửi thông báo Discord về các máy offline"""
    if not DISCORD_WEBHOOK_URL:
        return
    
    try:
        # Build message
        server_list = '\n'.join([f"• **{s['ten_may']}** - Offline {s['time_ago']}" for s in offline_servers])
        
        embed = {
            "title": "⚠️ CẢNH BÁO: MÁY CHỦ OFFLINE",
            "description": f"Phát hiện **{len(offline_servers)}** máy chủ đang offline:",
            "color": 15158332,  # Red color
            "fields": [
                {
                    "name": "Danh sách máy offline",
                    "value": server_list,
                    "inline": False
                }
            ],
            "footer": {
                "text": "Server Monitor - Htech Volam"
            },
            "timestamp": datetime.now(APP_TIMEZONE).isoformat()
        }
        
        payload = {
            "embeds": [embed]
        }
        
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        
        if response.status_code == 204:
            print(f"✅ Đã gửi thông báo Discord về {len(offline_servers)} máy offline")
        else:
            print(f"❌ Lỗi gửi Discord webhook: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Lỗi gửi Discord notification: {e}")


@app.route('/health')
def health():
    """Health check endpoint cho Render"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now(APP_TIMEZONE).isoformat()})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
