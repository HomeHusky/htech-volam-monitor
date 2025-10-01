# 🌐 Htech Volam Server Monitor

Website giám sát trạng thái máy chủ Htech Volam từ MongoDB - Real-time monitoring dashboard.

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

## 🖼️ Preview

Dashboard hiển thị:
- 📊 Thống kê tổng quan (tổng máy, online/offline, accounts)
- 🖥️ Chi tiết từng máy chủ với biểu đồ trực quan
- 🔄 Auto refresh mỗi 30 phút + nút refresh thủ công
- 📱 Responsive design (mobile, tablet, desktop)

## 📋 Tính năng

### ✅ Hiển thị trạng thái máy chủ
- **Online**: Máy cập nhật dữ liệu trong vòng 70 phút
- **Offline**: Máy không cập nhật quá 70 phút

### 📊 Thống kê tổng quan
- Tổng số máy chủ
- Số máy đang hoạt động
- Số máy offline
- Tổng số accounts online
- Tổng số accounts

### 💡 Thông tin chi tiết mỗi máy
- Tên máy chủ
- Trạng thái (Online/Offline)
- Số account online/offline
- Biểu đồ phần trăm accounts
### 🔄 Tự động làm mới
- Tự động reload trang mỗi 30 phút
- Countdown timer hiển thị thời gian còn lại
- Nút "Làm mới" để refresh thủ công bất kỳ lúc nào
- Luôn hiển thị dữ liệu mới nhất

### 💰 Pricing

### Free Tier
- ✅ Đủ cho monitoring cơ bản
- ⚠️ Sleep sau 15 phút không hoạt động
- ⚠️ Khởi động lại mất ~30 giây
- ⚠️ Giới hạn 750 giờ/tháng

### 🔄 Giải pháp Keep Alive (Không để sleep)
   - **Start Command**: `gunicorn app:app`

### Bước 3: Environment Variables (Tùy chọn)
Nếu muốn thay đổi MongoDB URI:
- Key: `MONGO_URI`
- Value: `mongodb+srv://...` (connection string của bạn)

### Bước 4: Deploy
- Click **Create Web Service**
- Đợi vài phút để Render build và deploy
- Truy cập URL được cung cấp (ví dụ: `https://htech-volam-monitor.onrender.com`)

## 🖥️ Chạy Local

### Cài đặt dependencies
```bash
cd web_monitor
pip install -r requirements.txt
```

### Chạy ứng dụng
```bash
python app.py
```

Truy cập: `http://localhost:5000`

## 📡 API Endpoints

### GET `/`
Trang chủ hiển thị dashboard

### GET `/api/servers`
Trả về JSON danh sách tất cả máy chủ
```json
[
  {
    "ten_may": "Máy chủ 1",
    "online": true,
    "so_acc_online": 15,
    "so_acc_offline": 5,
    "tong_so_acc": 20,
    "cap_nhat_luc": "2025-10-02 01:30:00",
    "time_ago": "5 phút trước"
  }
]
```

### GET `/api/stats`
Trả về JSON thống kê tổng quan
```json
{
  "total_servers": 10,
  "online_servers": 8,
  "offline_servers": 2,
  "total_accounts": 200,
  "total_online_accounts": 150,
  "last_update": "2025-10-02 01:30:00"
}
```

### GET `/health`
Health check endpoint
```json
{
  "status": "healthy",
  "timestamp": "2025-10-02T01:30:00.123456"
}
```

## 🎨 Giao diện

### Màu sắc
- **Online**: Xanh lá (#10b981)
- **Offline**: Đỏ (#ef4444)
- **Primary**: Tím gradient (#667eea → #764ba2)

### Responsive
- Desktop: Grid 3-4 cột
- Tablet: Grid 2 cột
- Mobile: 1 cột

### Animation
- Fade in khi load trang
- Hover effects trên cards
- Pulse animation cho refresh indicator

## ⚙️ Cấu hình

### Thời gian offline (app.py)
```python
OFFLINE_THRESHOLD_MINUTES = 70  # Đổi thành số phút bạn muốn
```

### Thời gian auto refresh (index.html)
```javascript
const AUTO_REFRESH_TIME = 1800000; // 1800000ms = 30 phút
// Đổi thành số milliseconds bạn muốn
// Ví dụ: 60000 = 1 phút, 300000 = 5 phút, 1800000 = 30 phút
```

## 📁 Cấu trúc thư mục
```
web_monitor/
├── app.py                 # Flask application
├── requirements.txt       # Python dependencies
├── render.yaml           # Render deployment config
├── .gitignore           # Git ignore file
├── README.md            # Documentation
└── templates/
    └── index.html       # HTML template
```

## 🔒 Bảo mật

⚠️ **Lưu ý**: MongoDB URI hiện đang hardcode trong code. Để bảo mật hơn:

1. Sử dụng Environment Variables trên Render
2. Không commit sensitive data lên Git
3. Tạo MongoDB user với quyền read-only cho web app

## 🐛 Troubleshooting

### Lỗi kết nối MongoDB
- Kiểm tra MongoDB URI
- Kiểm tra IP whitelist trên MongoDB Atlas (thêm `0.0.0.0/0` cho Render)

### Website không load
- Kiểm tra logs trên Render Dashboard
- Verify build command và start command

### Dữ liệu không hiển thị
- Kiểm tra collection name: `server_status`
- Kiểm tra database name: `HtechVolam`
- Verify có dữ liệu trong MongoDB

## 📝 License

MIT License - Free to use and modify
