# ===============================
# 🌐 WEB MONITOR - FLASK APP
# ===============================
"""
Web application để hiển thị trạng thái máy chủ từ MongoDB
Deploy lên Render.com
"""

from flask import Flask, render_template, jsonify
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime, timedelta
import os

app = Flask(__name__)

# MongoDB Configuration
# ⚠️ IMPORTANT: Set MONGO_URI as environment variable on Render
# Never commit real credentials to Git!
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority')
DB_NAME = os.environ.get('DB_NAME', 'HtechVolam')
COLLECTION_NAME = os.environ.get('COLLECTION_NAME', 'server_status')

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
        print(f"❌ Lỗi kết nối MongoDB: {e}")
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
    
    now = datetime.now()
    time_diff = now - last_update
    
    # Online nếu cập nhật trong vòng 70 phút
    return time_diff.total_seconds() < (OFFLINE_THRESHOLD_MINUTES * 60)


def get_all_servers():
    """
    Lấy danh sách tất cả máy chủ và trạng thái
    
    Returns:
        list: Danh sách các máy chủ với thông tin trạng thái
    """
    collection = get_mongo_collection()
    if collection is None:
        return []
    
    try:
        servers = list(collection.find().sort("cap_nhat_luc", -1))
        
        result = []
        for server in servers:
            last_update = server.get('cap_nhat_luc')
            online = is_server_online(last_update)
            
            # Tính thời gian từ lần cập nhật cuối
            time_ago = ""
            if last_update:
                time_diff = datetime.now() - last_update
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
        print(f"❌ Lỗi lấy dữ liệu: {e}")
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
        report = money_collection.find_one({"ten_may": ten_may}, sort=[("time", -1)])
        
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
        print(f"❌ Lỗi lấy báo cáo lợi nhuận: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/health')
def health():
    """Health check endpoint cho Render"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
