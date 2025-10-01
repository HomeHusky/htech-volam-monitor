# 🚀 Hướng dẫn Deploy lên Render.com

## 📋 Checklist trước khi deploy

- [ ] Đã có tài khoản GitHub
- [ ] Đã có tài khoản Render.com
- [ ] Đã push code lên GitHub repository
- [ ] MongoDB đã có dữ liệu trong collection `server_status`

## 🎯 Các bước Deploy

### Bước 1: Chuẩn bị Repository

1. **Push code lên GitHub**
```bash
cd web_monitor
git init
git add .
git commit -m "Initial commit - Server Monitor"
git remote add origin <your-github-repo-url>
git push -u origin main
```

### Bước 2: Tạo Web Service trên Render

1. Truy cập [Render Dashboard](https://dashboard.render.com/)
2. Click **New +** → **Web Service**
3. Chọn **Connect a repository**
4. Authorize Render truy cập GitHub
5. Chọn repository của bạn

### Bước 3: Cấu hình Service

**Basic Settings:**
- **Name**: `htech-volam-monitor` (hoặc tên bạn muốn)
- **Region**: Singapore (gần Việt Nam nhất)
- **Branch**: `main`
- **Root Directory**: `web_monitor` (nếu code trong subfolder)

**Build & Deploy:**
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app:app`

**Instance Type:**
- **Free** (đủ cho monitoring cơ bản)

### Bước 4: Environment Variables (Tùy chọn)

Nếu muốn bảo mật MongoDB URI:

1. Scroll xuống **Environment Variables**
2. Click **Add Environment Variable**
3. Thêm:
   - **Key**: `MONGO_URI`
   - **Value**: `mongodb+srv://htechvolam:Htech317@htechvolam.oefc26z.mongodb.net/?retryWrites=true&w=majority&appName=HtechVolam`

### Bước 5: Deploy

1. Click **Create Web Service**
2. Đợi Render build (khoảng 2-5 phút)
3. Khi status chuyển sang **Live**, click vào URL

**URL mẫu**: `https://htech-volam-monitor.onrender.com`

## ⚙️ Cấu hình MongoDB Atlas

### Whitelist IP cho Render

1. Vào [MongoDB Atlas](https://cloud.mongodb.com/)
2. Chọn cluster → **Network Access**
3. Click **Add IP Address**
4. Chọn **Allow Access from Anywhere** (`0.0.0.0/0`)
5. Click **Confirm**

⚠️ **Lưu ý**: Đây là cách đơn giản nhất. Để bảo mật hơn, tạo user read-only riêng cho web app.

## 🧪 Test sau khi Deploy

### 1. Health Check
```
https://your-app.onrender.com/health
```
Kết quả mong đợi:
```json
{
  "status": "healthy",
  "timestamp": "2025-10-02T01:30:00.123456"
}
```

### 2. API Test
```
https://your-app.onrender.com/api/stats
```

### 3. Web Interface
```
https://your-app.onrender.com/
```

## 🔧 Troubleshooting

### ❌ Build Failed

**Lỗi**: `Could not find requirements.txt`
- **Fix**: Kiểm tra Root Directory setting
- Nếu code trong `web_monitor/`, set Root Directory = `web_monitor`

**Lỗi**: `No module named 'flask'`
- **Fix**: Kiểm tra file `requirements.txt` có đúng dependencies

### ❌ Application Error

**Lỗi**: `ModuleNotFoundError: No module named 'app'`
- **Fix**: Kiểm tra Start Command: `gunicorn app:app`

**Lỗi**: MongoDB connection timeout
- **Fix**: 
  1. Kiểm tra MongoDB Atlas Network Access
  2. Thêm `0.0.0.0/0` vào IP Whitelist

### ❌ Website hiển thị trống

**Lỗi**: Không có dữ liệu máy chủ
- **Fix**: 
  1. Kiểm tra MongoDB có dữ liệu trong collection `server_status`
  2. Verify database name = `HtechVolam`
  3. Chạy login ít nhất 1 lần để tạo dữ liệu

## 📊 Monitoring

### Xem Logs trên Render

1. Vào service dashboard
2. Click tab **Logs**
3. Xem real-time logs

### Metrics

- **Deploy History**: Xem lịch sử deploy
- **Metrics**: CPU, Memory usage
- **Events**: Các sự kiện của service

## 🔄 Update Code

### Auto Deploy (Recommended)

Render tự động deploy khi push code mới:
```bash
git add .
git commit -m "Update feature"
git push origin main
```

### Manual Deploy

1. Vào Render Dashboard
2. Chọn service
3. Click **Manual Deploy** → **Deploy latest commit**

## 💰 Pricing

### Free Tier
- ✅ Đủ cho monitoring cơ bản
- ⚠️ Sleep sau 15 phút không hoạt động
- ⚠️ Khởi động lại mất ~30 giây

### Giải pháp cho Free Tier

**Cron Job để keep alive:**
```bash
# Ping mỗi 10 phút
*/10 * * * * curl https://your-app.onrender.com/health
```

Hoặc dùng service như [UptimeRobot](https://uptimerobot.com/) (free) để ping định kỳ.

### Starter Plan ($7/month)
- ✅ Không sleep
- ✅ Faster performance
- ✅ Custom domain

## 🎨 Customization

### Thay đổi thời gian offline

File `app.py`:
```python
OFFLINE_THRESHOLD_MINUTES = 70  # Đổi thành số phút bạn muốn
```

### Thay đổi auto refresh

File `templates/index.html`:
```javascript
setTimeout(function() {
    location.reload();
}, 30000);  // 30000ms = 30 giây
```

### Custom Domain

1. Mua domain (ví dụ: `monitor.htechvolam.com`)
2. Vào Render service settings
3. Add custom domain
4. Cấu hình DNS theo hướng dẫn

## 📱 Mobile Responsive

Website đã responsive cho:
- 📱 Mobile (< 768px)
- 📱 Tablet (768px - 1024px)
- 🖥️ Desktop (> 1024px)

## 🔐 Security Best Practices

1. **Tạo MongoDB user read-only cho web app**
```javascript
// MongoDB Shell
use HtechVolam
db.createUser({
  user: "web_readonly",
  pwd: "strong_password",
  roles: [{ role: "read", db: "HtechVolam" }]
})
```

2. **Sử dụng Environment Variables**
- Không hardcode credentials trong code
- Dùng Render Environment Variables

3. **Enable HTTPS**
- Render tự động cung cấp SSL certificate
- Luôn dùng HTTPS

## 📞 Support

Nếu gặp vấn đề:
1. Check Render logs
2. Check MongoDB Atlas logs
3. Test local trước: `python test_local.py`

## ✅ Checklist Deploy thành công

- [ ] Website accessible qua URL
- [ ] Health check endpoint hoạt động
- [ ] API endpoints trả về dữ liệu
- [ ] Dashboard hiển thị đúng số liệu
- [ ] Auto refresh hoạt động
- [ ] Responsive trên mobile
- [ ] MongoDB connection stable

🎉 **Chúc mừng! Website đã sẵn sàng!**
