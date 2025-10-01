# ⚡ Quick Start - Giữ Render không Sleep

## 🎯 Giải pháp nhanh nhất (5 phút)

### Dùng UptimeRobot (Khuyên dùng)

1. **Đăng ký**: [UptimeRobot.com](https://uptimerobot.com/) (Free)

2. **Add Monitor**:
   - Monitor Type: `HTTP(s)`
   - URL: `https://your-app.onrender.com/health`
   - Interval: `5 minutes`

3. **Done!** ✅ Website sẽ không sleep nữa

---

## 📋 Các file đã tạo

### 1. `keep_alive.py`
Script Python để ping website (chạy local/server)

**Sử dụng:**
```bash
# Sửa URL trong file
WEBSITE_URL = "https://your-app.onrender.com/health"

# Chạy
pip install requests
python keep_alive.py
```

### 2. `.github/workflows/keep-alive.yml`
GitHub Actions workflow (tự động ping)

**Sử dụng:**
```bash
# 1. Sửa URL trong file
# 2. Push lên GitHub
# 3. Enable Actions trong repo settings
# 4. Done! Tự động ping mỗi 10 phút
```

### 3. `KEEP_ALIVE_GUIDE.md`
Hướng dẫn chi tiết tất cả các giải pháp

---

## 🚀 So sánh nhanh

| Giải pháp | Setup | Khuyên dùng |
|-----------|-------|-------------|
| **UptimeRobot** | 5 phút | ⭐⭐⭐⭐⭐ |
| GitHub Actions | 10 phút | ⭐⭐⭐⭐ |
| Script Python | 5 phút | ⭐⭐⭐ |
| Cron-job.org | 5 phút | ⭐⭐⭐⭐ |

---

## ✅ Verify thành công

Sau khi setup, đợi 20 phút rồi:
1. Truy cập website
2. Nếu load ngay → Thành công ✅
3. Nếu load chậm → Vẫn đang sleep ❌

---

## 💡 Tips

- Ping endpoint `/health` (nhẹ hơn `/`)
- Interval: 5-10 phút là đủ
- Setup 2 services để backup

---

**Khuyến nghị:** Dùng UptimeRobot - Dễ nhất, có alert, 100% free! 🎉
