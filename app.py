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
import threading
import time

app = Flask(__name__)

# MongoDB Configuration with timezone handling
# ⚠️ IMPORTANT: Set MONGO_URI as environment variable on Render
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority')
DB_NAME = os.environ.get('DB_NAME', 'HtechVolam')
COLLECTION_NAME = os.environ.get('COLLECTION_NAME', 'server_status')

# Discord Webhook Configuration
DISCORD_WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK_URL', '')

# Profit reports collection
PROFIT_REPORTS_COLLECTION = 'profit_reports'

# Collection for excluded servers
EXCLUDED_SERVERS_COLLECTION = 'excluded_servers'

# Collection for monitoring settings
MONITORING_SETTINGS_COLLECTION = 'monitoring_settings'

# Default check interval (minutes)
DEFAULT_CHECK_INTERVAL_MINUTES = 30

# Background monitoring thread
monitoring_thread = None
monitoring_stop_event = threading.Event()

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


def send_comprehensive_discord_notification(offline_servers, unchanged_accounts, decreased_accounts):
    """Gửi thông báo Discord tổng hợp về máy offline và tài khoản có vấn đề"""
    if not DISCORD_WEBHOOK_URL:
        return

    try:
        embed = {
            "title": "📊 BÁO CÁO HỆ THỐNG",
            "color": 3447003,  # Blue color
            "fields": [],
            "footer": {
                "text": "Server Monitor - Htech Volam"
            },
            "timestamp": datetime.now(APP_TIMEZONE).isoformat()
        }

        # Offline servers section
        if offline_servers:
            server_list = '\n'.join([f"• **{s['ten_may']}** - Offline {s['time_ago']}" for s in offline_servers])
            embed["fields"].append({
                "name": f"⚠️ Máy Offline ({len(offline_servers)})",
                "value": server_list,
                "inline": False
            })

        # Unchanged accounts section
        if unchanged_accounts:
            account_list = '\n'.join([
                f"• **{acc['machine']}** - {acc['account']} (Không đổi)"
                for acc in unchanged_accounts[:10]  # Limit to 10 for Discord message size
            ])
            if len(unchanged_accounts) > 10:
                account_list += f"\n• ... và {len(unchanged_accounts) - 10} tài khoản khác"

            embed["fields"].append({
                "name": f"📊 Tài Khoản Không Đổi ({len(unchanged_accounts)})",
                "value": account_list,
                "inline": False
            })

        # Decreased accounts section
        if decreased_accounts:
            account_list = '\n'.join([
                f"• **{acc['machine']}** - {acc['account']} (Giảm)"
                for acc in decreased_accounts[:10]  # Limit to 10 for Discord message size
            ])
            if len(decreased_accounts) > 10:
                account_list += f"\n• ... và {len(decreased_accounts) - 10} tài khoản khác"

            embed["fields"].append({
                "name": f"📉 Tài Khoản Giảm ({len(decreased_accounts)})",
                "value": account_list,
                "inline": False
            })

        # Set description based on content
        total_issues = len(offline_servers) + len(unchanged_accounts) + len(decreased_accounts)
        if total_issues == 0:
            embed["description"] = "✅ Tất cả máy đều online và không có tài khoản có vấn đề"
        else:
            embed["description"] = f"📋 Phát hiện **{total_issues}** vấn đề cần chú ý"

        payload = {
            "embeds": [embed]
        }

        response = requests.post(DISCORD_WEBHOOK_URL, json=payload)

        if response.status_code == 204:
            print(f"✅ Đã gửi báo cáo Discord tổng hợp: {len(offline_servers)} máy offline, {len(unchanged_accounts)} tài khoản không đổi, {len(decreased_accounts)} tài khoản giảm")
        else:
            print(f"❌ Lỗi gửi Discord webhook: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Lỗi gửi Discord notification tổng hợp: {e}")


@app.route('/api/monitoring-settings', methods=['GET'])
def get_monitoring_settings():
    """Lấy cài đặt monitoring"""
    collection = get_mongo_collection()
    if collection is None:
        return jsonify({'error': 'Không thể kết nối MongoDB'}), 500
    
    try:
        settings_collection = collection.database[MONITORING_SETTINGS_COLLECTION]
        settings = settings_collection.find_one({'_id': 'monitoring_config'})
        
        if settings and 'check_interval_minutes' in settings:
            return jsonify({'check_interval_minutes': settings['check_interval_minutes']})
        else:
            return jsonify({'check_interval_minutes': DEFAULT_CHECK_INTERVAL_MINUTES})
    except Exception as e:
        print(f"❌ Lỗi lấy cài đặt monitoring: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/monitoring-settings', methods=['POST'])
def update_monitoring_settings():
    """Cập nhật cài đặt monitoring"""
    collection = get_mongo_collection()
    if collection is None:
        return jsonify({'error': 'Không thể kết nối MongoDB'}), 500
    
    try:
        data = request.get_json()
        check_interval = data.get('check_interval_minutes', DEFAULT_CHECK_INTERVAL_MINUTES)
        
        # Validate
        if not isinstance(check_interval, (int, float)) or check_interval < 1 or check_interval > 1440:
            return jsonify({'error': 'Thời gian phải từ 1 đến 1440 phút'}), 400
        
        settings_collection = collection.database[MONITORING_SETTINGS_COLLECTION]
        settings_collection.update_one(
            {'_id': 'monitoring_config'},
            {'$set': {'check_interval_minutes': check_interval, 'updated_at': datetime.now(APP_TIMEZONE)}},
            upsert=True
        )
        
        # Restart monitoring thread with new interval
        restart_monitoring_thread()
        
        return jsonify({'success': True, 'check_interval_minutes': check_interval})
    except Exception as e:
        print(f"❌ Lỗi cập nhật cài đặt monitoring: {e}")
        return jsonify({'error': str(e)}), 500


def get_check_interval():
    """Lấy thời gian check interval từ database"""
    try:
        collection = get_mongo_collection()
        if collection is None:
            return DEFAULT_CHECK_INTERVAL_MINUTES
        
        settings_collection = collection.database[MONITORING_SETTINGS_COLLECTION]
        settings = settings_collection.find_one({'_id': 'monitoring_config'})
        
        if settings and 'check_interval_minutes' in settings:
            return settings['check_interval_minutes']
    except Exception as e:
        print(f"❌ Lỗi lấy check interval: {e}")
    
    return DEFAULT_CHECK_INTERVAL_MINUTES


def monitoring_loop():
    """Background thread để kiểm tra máy offline định kỳ"""
    print("🔄 Monitoring thread started")
    
    while not monitoring_stop_event.is_set():
        try:
            # Get current check interval
            check_interval_minutes = get_check_interval()
            check_interval_seconds = check_interval_minutes * 60
            
            print(f"⏱️ Next check in {check_interval_minutes} minutes")
            
            # Wait for the interval or until stop event is set
            if monitoring_stop_event.wait(timeout=check_interval_seconds):
                break  # Stop event was set
            
            # Perform the check
            print(f"🔍 Checking offline servers...")
            check_and_notify_offline_servers()
            
        except Exception as e:
            print(f"❌ Error in monitoring loop: {e}")
            # Wait a bit before retrying
            monitoring_stop_event.wait(timeout=60)
    
    print("🛑 Monitoring thread stopped")


def get_unchanged_accounts():
    """Lấy danh sách các account có trạng thái 'Không đổi' ở máy online"""
    collection = get_mongo_collection()
    if collection is None:
        return []

    try:
        # Get online servers
        servers = get_all_servers()
        online_machines = [s['ten_may'] for s in servers if s['online']]

        if not online_machines:
            print("⚠️ No online machines found for unchanged accounts check")
            return []

        # Get profit reports for online machines
        profit_collection = collection.database[PROFIT_REPORTS_COLLECTION]
        unchanged_accounts = []

        print(f"🔍 Checking {len(online_machines)} online machines for unchanged accounts (based on status text)")

        for machine in online_machines:
            report = profit_collection.find_one({'ten_may': machine})
            if report and 'report' in report:
                print(f"📋 Machine {machine}: Found {len(report['report'])} accounts")
                for acc in report['report']:
                    status = (acc.get('status', '') or '').lower().strip()
                    account_name = acc.get('account', 'N/A')

                    print(f"  Account {account_name}: status='{status}'")

                    # Normalize status for comparison (same logic as profit table)
                    normalized_status = status.lower().strip()

                    # Check for "Không đổi" (neutral/gray in table)
                    is_unchanged = (
                        'không đổi' in normalized_status or
                        normalized_status == 'không đổi' or
                        normalized_status == 'khôngđổi' or
                        normalized_status == 'k đổi' or
                        (not normalized_status) or  # Empty status
                        (not any(keyword in normalized_status for keyword in ['tăng', 'giảm', 'chưa đạt', 'đạt kpi', 'đạt 50% kpi']))
                    )

                    if is_unchanged:
                        print(f"    ✅ Found unchanged account: {account_name} (status: '{status}')")
                        unchanged_accounts.append({
                            'machine': machine,
                            'account': account_name,
                            'profit': acc.get('profit', 0),
                            'old': acc.get('old', 0),
                            'new': acc.get('new', 0),
                            'status': status
                        })

        print(f"📊 Total unchanged accounts found: {len(unchanged_accounts)}")
        return unchanged_accounts
    except Exception as e:
        print(f"❌ Error getting unchanged accounts: {e}")
        import traceback
        traceback.print_exc()
        return []


def get_decreased_accounts():
    """Lấy danh sách các account có trạng thái 'Giảm' ở máy online"""
    collection = get_mongo_collection()
    if collection is None:
        return []

    try:
        # Get online servers
        servers = get_all_servers()
        online_machines = [s['ten_may'] for s in servers if s['online']]

        if not online_machines:
            print("⚠️ No online machines found for decreased accounts check")
            return []

        # Get profit reports for online machines
        profit_collection = collection.database[PROFIT_REPORTS_COLLECTION]
        decreased_accounts = []

        print(f"🔍 Checking {len(online_machines)} online machines for decreased accounts (based on status text)")

        for machine in online_machines:
            report = profit_collection.find_one({'ten_may': machine})
            if report and 'report' in report:
                print(f"📋 Machine {machine}: Found {len(report['report'])} accounts")
                for acc in report['report']:
                    status = (acc.get('status', '') or '').lower().strip()
                    account_name = acc.get('account', 'N/A')

                    print(f"  Account {account_name}: status='{status}'")

                    # Normalize status for comparison (same logic as profit table)
                    normalized_status = status.lower().strip()

                    # Check for negative statuses: "Chưa đạt KPI", "Chưa đạt", "Giảm"
                    # IMPORTANT: Check negative statuses FIRST (because "chưa đạt kpi" contains "đạt kpi")
                    is_decreased = (
                        'chưa đạt kpi' in normalized_status or
                        'chưa đạt' in normalized_status or
                        'giảm' in normalized_status or
                        normalized_status == 'giảm' or
                        normalized_status == 'giam'
                    )

                    if is_decreased:
                        print(f"    ✅ Found decreased account: {account_name} (status: '{status}')")
                        decreased_accounts.append({
                            'machine': machine,
                            'account': account_name,
                            'profit': acc.get('profit', 0),
                            'old': acc.get('old', 0),
                            'new': acc.get('new', 0),
                            'status': status
                        })

        print(f"📉 Total decreased accounts found: {len(decreased_accounts)}")
        return decreased_accounts
    except Exception as e:
        print(f"❌ Error getting decreased accounts: {e}")
        import traceback
        traceback.print_exc()
        return []


def check_and_notify_offline_servers():
    """Kiểm tra máy offline và gửi thông báo Discord cho cả máy offline và tài khoản không đổi/giảm"""
    collection = get_mongo_collection()
    if collection is None:
        print("❌ Cannot connect to MongoDB")
        return

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

        # Get accounts with issues from online machines
        unchanged_accounts = get_unchanged_accounts()
        decreased_accounts = get_decreased_accounts()

        print(f"🔍 Debug: Found {len(offline_servers)} offline servers, {len(unchanged_accounts)} unchanged accounts, {len(decreased_accounts)} decreased accounts")

        # Send Discord notification if there are issues
        if (offline_servers or unchanged_accounts or decreased_accounts) and DISCORD_WEBHOOK_URL:
            send_comprehensive_discord_notification(offline_servers, unchanged_accounts, decreased_accounts)
            print(f"✅ Sent comprehensive Discord notification")
        else:
            print(f"⚠️ No issues found or Discord webhook not configured")

        # Log results
        if offline_servers:
            print(f"⚠️ Found {len(offline_servers)} offline servers")
        if unchanged_accounts:
            print(f"📊 Found {len(unchanged_accounts)} unchanged accounts")
        if decreased_accounts:
            print(f"📉 Found {len(decreased_accounts)} decreased accounts")

        if not offline_servers and not unchanged_accounts and not decreased_accounts:
            print("✅ All servers are online and no problematic accounts")

    except Exception as e:
        print(f"❌ Error checking offline servers: {e}")
        import traceback
        traceback.print_exc()


def start_monitoring_thread():
    """Khởi động background monitoring thread"""
    global monitoring_thread
    
    if monitoring_thread is not None and monitoring_thread.is_alive():
        print("⚠️ Monitoring thread already running")
        return
    
    monitoring_stop_event.clear()
    monitoring_thread = threading.Thread(target=monitoring_loop, daemon=True)
    monitoring_thread.start()
    print("✅ Monitoring thread started")


def restart_monitoring_thread():
    """Restart monitoring thread với cài đặt mới"""
    global monitoring_thread
    
    print("🔄 Restarting monitoring thread...")
    
    # Stop current thread
    if monitoring_thread is not None and monitoring_thread.is_alive():
        monitoring_stop_event.set()
        monitoring_thread.join(timeout=5)
    
    # Start new thread
    start_monitoring_thread()


@app.route('/health')
def health():
    """Health check endpoint cho Render"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now(APP_TIMEZONE).isoformat(),
        'monitoring_active': monitoring_thread is not None and monitoring_thread.is_alive()
    })


if __name__ == '__main__':
    # Start background monitoring thread
    start_monitoring_thread()
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
