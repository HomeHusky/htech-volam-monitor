# 📤 Hướng dẫn Push lên GitHub Repository riêng

## 🎯 Mục đích
Push thư mục `web_monitor` lên một GitHub repository riêng để deploy lên Render.

---

## ⚡ Cách 1: Dùng Script tự động (Khuyên dùng)

### Windows:
```bash
cd web_monitor
setup_git.bat
```

### Linux/Mac:
```bash
cd web_monitor
chmod +x setup_git.sh
./setup_git.sh
```

Script sẽ tự động:
1. ✅ Khởi tạo Git repository
2. ✅ Tạo .gitignore
3. ✅ Add và commit files
4. ✅ Hỏi GitHub repository URL
5. ✅ Push lên GitHub

---

## 🔧 Cách 2: Thủ công (Step by step)

### Bước 1: Tạo GitHub Repository

1. Vào [GitHub](https://github.com/new)
2. **Repository name**: `htech-volam-monitor` (hoặc tên bạn muốn)
3. **Description**: `Server monitoring dashboard for Htech Volam`
4. Chọn **Public** hoặc **Private**
5. **KHÔNG** chọn "Initialize this repository with a README"
6. Click **Create repository**
7. Copy URL (ví dụ: `https://github.com/username/htech-volam-monitor.git`)

### Bước 2: Setup Git Local

Mở terminal/cmd trong thư mục `web_monitor`:

```bash
# Di chuyển vào thư mục web_monitor
cd web_monitor

# Khởi tạo git (nếu chưa có)
git init

# Add tất cả files
git add .

# Commit
git commit -m "Initial commit - Htech Volam Server Monitor"

# Add remote (thay YOUR_GITHUB_URL)
git remote add origin https://github.com/username/htech-volam-monitor.git

# Đổi branch thành main
git branch -M main

# Push lên GitHub
git push -u origin main
```

### Bước 3: Verify

Vào GitHub repository, kiểm tra files đã được push:
- ✅ app.py
- ✅ templates/index.html
- ✅ requirements.txt
- ✅ Procfile
- ✅ README.md
- ✅ Các file khác

---

## 🚀 Deploy lên Render

Sau khi push lên GitHub:

### Bước 1: Connect Repository
1. Vào [Render Dashboard](https://dashboard.render.com/)
2. Click **New +** → **Web Service**
3. Click **Connect a repository**
4. Authorize Render truy cập GitHub
5. Chọn repository `htech-volam-monitor`

### Bước 2: Configure Service
- **Name**: `htech-volam-monitor`
- **Region**: `Singapore`
- **Branch**: `main`
- **Root Directory**: (để trống)
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app:app`

### Bước 3: Environment Variables (Tùy chọn)
Nếu muốn thay đổi MongoDB URI:
- Key: `MONGO_URI`
- Value: `mongodb+srv://...`

### Bước 4: Deploy
1. Click **Create Web Service**
2. Đợi 2-5 phút để build
3. Khi status = **Live**, click URL
4. Done! ✅

---

## 🔄 Update Code sau này

Khi có thay đổi:

```bash
cd web_monitor

# Add changes
git add .

# Commit
git commit -m "Update: mô tả thay đổi"

# Push
git push origin main
```

Render sẽ tự động deploy lại!

---

## ⚠️ Troubleshooting

### Lỗi: "remote origin already exists"
```bash
git remote remove origin
git remote add origin YOUR_GITHUB_URL
```

### Lỗi: "failed to push"
```bash
# Pull trước
git pull origin main --allow-unrelated-histories

# Rồi push lại
git push origin main
```

### Lỗi: "Permission denied"
Cần setup GitHub authentication:

**Option 1: HTTPS (Dễ hơn)**
```bash
# GitHub sẽ hỏi username/password khi push
# Dùng Personal Access Token thay vì password
```

**Option 2: SSH**
```bash
# Tạo SSH key
ssh-keygen -t ed25519 -C "your_email@example.com"

# Add vào GitHub
# Settings → SSH and GPG keys → New SSH key
```

---

## 📁 Cấu trúc Repository

Sau khi push, repository sẽ có:

```
htech-volam-monitor/
├── app.py                    # Flask app
├── templates/
│   └── index.html           # Frontend
├── requirements.txt         # Dependencies
├── Procfile                 # Render config
├── runtime.txt             # Python version
├── render.yaml             # Alternative config
├── .gitignore              # Git ignore
├── README.md               # Documentation
├── DEPLOY_GUIDE.md         # Deploy guide
├── KEEP_ALIVE_GUIDE.md     # Keep alive guide
├── QUICK_START.md          # Quick start
├── keep_alive.py           # Keep alive script
├── test_local.py           # Local test
└── .github/
    └── workflows/
        └── keep-alive.yml  # GitHub Actions
```

---

## ✅ Checklist

- [ ] Tạo GitHub repository
- [ ] Push code lên GitHub
- [ ] Verify files trên GitHub
- [ ] Connect repository với Render
- [ ] Configure service settings
- [ ] Deploy thành công
- [ ] Test website hoạt động
- [ ] Setup keep-alive (UptimeRobot)

---

## 💡 Tips

1. **Repository name**: Nên đặt tên ngắn gọn, dễ nhớ
2. **Branch**: Dùng `main` thay vì `master`
3. **Commit messages**: Viết rõ ràng để dễ track changes
4. **Auto deploy**: Render tự động deploy khi push code mới
5. **Private repo**: Vẫn deploy được, Render hỗ trợ cả public và private

---

## 🎉 Kết luận

Sau khi push lên GitHub:
1. ✅ Code được version control
2. ✅ Dễ dàng deploy lên Render
3. ✅ Tự động deploy khi có update
4. ✅ Có thể collaborate với team

**URL mẫu sau khi deploy:**
`https://htech-volam-monitor.onrender.com`

Good luck! 🚀
