# 🔄 Hướng dẫn giữ Render không Sleep

Render Free Tier sẽ sleep sau 15 phút không hoạt động. Dưới đây là các cách để giữ website luôn active.

## 🎯 Các giải pháp

### ✅ Giải pháp 1: UptimeRobot (Khuyên dùng - 100% Free)

**UptimeRobot** là dịch vụ monitoring miễn phí, ping website định kỳ.

#### Bước 1: Đăng ký UptimeRobot
1. Truy cập [UptimeRobot.com](https://uptimerobot.com/)
2. Đăng ký tài khoản miễn phí
3. Xác nhận email

#### Bước 2: Tạo Monitor
1. Click **Add New Monitor**
2. Cấu hình:
   - **Monitor Type**: HTTP(s)
   - **Friendly Name**: `Htech Volam Monitor`
   - **URL**: `https://your-app.onrender.com/health`
   - **Monitoring Interval**: `5 minutes` (free tier)
   - **Monitor Timeout**: `30 seconds`
3. Click **Create Monitor**

#### Bước 3: Xong!
- UptimeRobot sẽ ping website mỗi 5 phút
- Website sẽ không bao giờ sleep
- Nhận email alert nếu website down

**Ưu điểm:**
- ✅ 100% miễn phí
- ✅ Không cần chạy script
- ✅ Có email alert
- ✅ Dashboard theo dõi uptime
- ✅ Hỗ trợ 50 monitors miễn phí

---

### ✅ Giải pháp 2: Chạy script Python (Local/Server)

Chạy script `keep_alive.py` trên máy tính hoặc server 24/7.

#### Cài đặt
```bash
pip install requests
```

#### Cấu hình
Sửa file `keep_alive.py`:
```python
WEBSITE_URL = "https://your-app.onrender.com/health"  # URL thực của bạn
PING_INTERVAL = 600  # 10 phút
```

#### Chạy
```bash
python keep_alive.py
```

Output:
```
============================================================
🚀 RENDER KEEP ALIVE SERVICE
============================================================
📡 Target URL: https://your-app.onrender.com/health
⏰ Ping interval: 600 seconds (10.0 minutes)
🕐 Started at: 2025-10-02 01:35:00
============================================================

Press Ctrl+C to stop

✅ [2025-10-02 01:35:00] Ping thành công - Status: 200
✅ [2025-10-02 01:45:00] Ping thành công - Status: 200
```

**Ưu điểm:**
- ✅ Hoàn toàn kiểm soát
- ✅ Có thể tùy chỉnh interval
- ✅ Chạy local không cần service bên ngoài

**Nhược điểm:**
- ❌ Cần máy tính/server chạy 24/7
- ❌ Tốn điện nếu chạy local

---

### ✅ Giải pháp 3: Cron-job.org (Free)

Dịch vụ cron job miễn phí online.

#### Bước 1: Đăng ký
1. Truy cập [Cron-job.org](https://cron-job.org/)
2. Đăng ký tài khoản miễn phí

#### Bước 2: Tạo Cron Job
1. Click **Create cronjob**
2. Cấu hình:
   - **Title**: `Keep Render Alive`
   - **URL**: `https://your-app.onrender.com/health`
   - **Schedule**: Every 10 minutes
3. Save

**Ưu điểm:**
- ✅ Miễn phí
- ✅ Không cần chạy script
- ✅ Web interface đơn giản

**Nhược điểm:**
- ❌ Ít tính năng hơn UptimeRobot
- ❌ Không có alert

---

### ✅ Giải pháp 4: GitHub Actions (Free)

Sử dụng GitHub Actions để ping định kỳ.

#### Tạo file `.github/workflows/keep-alive.yml`
```yaml
name: Keep Render Alive

on:
  schedule:
    # Chạy mỗi 10 phút
    - cron: '*/10 * * * *'
  workflow_dispatch:

jobs:
  ping:
    runs-on: ubuntu-latest
    steps:
      - name: Ping website
        run: |
          curl -f https://your-app.onrender.com/health || exit 1
          echo "✅ Ping successful at $(date)"
```

**Ưu điểm:**
- ✅ Miễn phí
- ✅ Tích hợp với GitHub
- ✅ Không cần service bên ngoài

**Nhược điểm:**
- ❌ Cần có GitHub repository
- ❌ Interval tối thiểu 5 phút

---

### ✅ Giải pháp 5: Chạy từ máy khác trong hệ thống

Nếu bạn có máy chủ khác chạy 24/7, thêm cron job:

#### Linux/Mac
```bash
# Mở crontab
crontab -e

# Thêm dòng này (ping mỗi 10 phút)
*/10 * * * * curl -s https://your-app.onrender.com/health > /dev/null
```

#### Windows Task Scheduler
1. Mở Task Scheduler
2. Create Basic Task
3. Trigger: Daily, repeat every 10 minutes
4. Action: Start a program
   - Program: `curl`
   - Arguments: `https://your-app.onrender.com/health`

---

## 📊 So sánh các giải pháp

| Giải pháp | Miễn phí | Dễ setup | Độ tin cậy | Alert | Khuyên dùng |
|-----------|----------|----------|------------|-------|-------------|
| **UptimeRobot** | ✅ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ✅ | ⭐⭐⭐⭐⭐ |
| Script Python | ✅ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ❌ | ⭐⭐⭐ |
| Cron-job.org | ✅ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ❌ | ⭐⭐⭐⭐ |
| GitHub Actions | ✅ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ❌ | ⭐⭐⭐ |
| Server Cron | ✅ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ❌ | ⭐⭐⭐⭐ |

## 🎯 Khuyến nghị

### Cho người dùng thông thường:
**→ Dùng UptimeRobot** (Giải pháp 1)
- Dễ nhất, không cần code
- Có email alert
- 100% miễn phí

### Cho developer:
**→ Dùng GitHub Actions** (Giải pháp 4)
- Tích hợp với workflow
- Version control
- Miễn phí

### Nếu có server 24/7:
**→ Dùng Cron Job** (Giải pháp 5)
- Tin cậy nhất
- Không phụ thuộc service bên ngoài

## 🔧 Verify hoạt động

Sau khi setup, kiểm tra:

1. **Xem logs trên Render**
   - Vào Render Dashboard → Service → Logs
   - Sẽ thấy request đến `/health` mỗi 5-10 phút

2. **Check uptime**
   - Để website idle > 15 phút
   - Truy cập website → Nếu load ngay = thành công
   - Nếu load chậm = vẫn đang sleep

3. **Monitor UptimeRobot**
   - Vào dashboard
   - Xem uptime % (nên là 99-100%)

## 💡 Tips

1. **Ping endpoint `/health` thay vì `/`**
   - Nhẹ hơn, không load toàn bộ trang
   - Không ảnh hưởng analytics

2. **Interval khuyên dùng: 10 phút**
   - Render sleep sau 15 phút
   - 10 phút = an toàn, không quá spam

3. **Multiple monitors**
   - Setup 2-3 services khác nhau
   - Backup nếu 1 service down

4. **Không ping quá thường xuyên**
   - Mỗi 5-10 phút là đủ
   - Quá nhiều request = lãng phí bandwidth

## ⚠️ Lưu ý

- Render Free Tier có giới hạn 750 giờ/tháng
- Keep alive sẽ dùng hết quota này
- Nếu cần uptime 100%, nên nâng cấp lên Starter plan ($7/month)

## 🎉 Kết luận

**Setup nhanh nhất (5 phút):**
1. Vào [UptimeRobot.com](https://uptimerobot.com/)
2. Đăng ký → Add Monitor
3. URL: `https://your-app.onrender.com/health`
4. Interval: 5 minutes
5. Done! ✅

Website sẽ không bao giờ sleep nữa! 🚀
