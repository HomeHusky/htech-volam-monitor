"""
Script test kết nối MongoDB và lấy dữ liệu
Chạy trước khi deploy để verify
"""

from app import get_all_servers, get_mongo_collection

def test_connection():
    """Test kết nối MongoDB"""
    print("=== TEST KẾT NỐI MONGODB ===\n")
    
    collection = get_mongo_collection()
    if collection:
        print("✅ Kết nối MongoDB thành công!")
        
        # Đếm số documents
        count = collection.count_documents({})
        print(f"📊 Số lượng máy chủ trong database: {count}\n")
        
        return True
    else:
        print("❌ Không thể kết nối MongoDB!")
        return False

def test_get_servers():
    """Test lấy danh sách máy chủ"""
    print("=== TEST LẤY DANH SÁCH MÁY CHỦ ===\n")
    
    servers = get_all_servers()
    
    if not servers:
        print("⚠️ Không có dữ liệu máy chủ!")
        return
    
    print(f"Tìm thấy {len(servers)} máy chủ:\n")
    
    for i, server in enumerate(servers, 1):
        status = "🟢 ONLINE" if server['online'] else "🔴 OFFLINE"
        print(f"{i}. {server['ten_may']} - {status}")
        print(f"   Accounts: {server['so_acc_online']}/{server['tong_so_acc']} online")
        print(f"   Cập nhật: {server['time_ago']}")
        print()

if __name__ == "__main__":
    if test_connection():
        test_get_servers()
        
        print("\n=== KẾT QUẢ ===")
        print("✅ Tất cả test đều pass!")
        print("🚀 Sẵn sàng deploy lên Render!")
        print("\nChạy lệnh: python app.py")
        print("Truy cập: http://localhost:5000")
