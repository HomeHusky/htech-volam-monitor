# 🚨 BẢO MẬT - MongoDB URI đã bị public!

## ⚠️ Vấn đề

MongoDB URI với username/password đã bị commit lên GitHub repository public!

**URI bị lộ:**
```
mongodb+srv://htechvolam:Htech317@htechvolam.oefc26z.mongodb.net/...
```

## 🔥 CẦN LÀM NGAY (Khẩn cấp!)

### Bước 1: Đổi mật khẩu MongoDB

1. Vào [MongoDB Atlas](https://cloud.mongodb.com/)
2. **Database Access** → Chọn user `htechvolam`
3. Click **Edit**
4. **Edit Password** → Tạo mật khẩu mới
5. **Update User**

### Bước 2: Xóa lịch sử Git (Quan trọng!)

MongoDB URI đã nằm trong Git history, cần xóa hoàn toàn:

```bash
cd web_monitor

# Option 1: Xóa toàn bộ history (Khuyên dùng)
rm -rf .git
git init
git add .
git commit -m "Initial commit - Removed sensitive data"
git remote add origin https://github.com/HomeHusky/htech-volam-monitor
git push -f origin main

# Option 2: Dùng git filter-repo (Nâng cao)
# Cài đặt: pip install git-filter-repo
git filter-repo --path app.py --invert-paths
git filter-repo --path render.yaml --invert-paths
```

### Bước 3: Update code với URI mới

File `app.py` đã được sửa để dùng environment variable.

**Chạy local:**
```bash
# Tạo file .env
cp .env.example .env

# Sửa .env với URI mới
MONGO_URI=mongodb+srv://htechvolam:NEW_PASSWORD@htechvolam.oefc26z.mongodb.net/...
```

**Deploy trên Render:**
1. Vào Render Dashboard → Service
2. **Environment** tab
3. Add environment variable:
   - Key: `MONGO_URI`
   - Value: `mongodb+srv://htechvolam:NEW_PASSWORD@...`
4. Save changes

### Bước 4: Push code đã sửa

```bash
git add .
git commit -m "Security: Remove hardcoded credentials"
git push origin main
```

## 🔒 Ngăn chặn tương lai

### 1. Đã thêm vào .gitignore

File `.gitignore` đã có:
```
.env
*.log
```

### 2. Sử dụng environment variables

Code đã được sửa:
```python
MONGO_URI = os.environ.get('MONGO_URI', 'default-placeholder')
```

### 3. File .env.example

Template cho local development (không chứa credentials thật).

## ✅ Checklist bảo mật

- [ ] Đổi mật khẩu MongoDB
- [ ] Xóa Git history (force push)
- [ ] Update MONGO_URI trên Render
- [ ] Verify website vẫn hoạt động
- [ ] Kiểm tra không còn credentials trong code
- [ ] Thêm .env vào .gitignore
- [ ] Không bao giờ commit .env

## 🛡️ Best Practices

### ❌ KHÔNG BAO GIỜ:
- Hardcode credentials trong code
- Commit file .env
- Share credentials qua chat/email
- Dùng credentials trong commit messages

### ✅ NÊN:
- Dùng environment variables
- Dùng .env.example làm template
- Rotate credentials định kỳ
- Sử dụng secrets management (Render, AWS Secrets Manager)
- Enable MongoDB IP whitelist

## 📊 Kiểm tra bảo mật

### Scan GitHub repository:
```bash
# Dùng truffleHog để scan secrets
pip install truffleHog
truffleHog --regex --entropy=False https://github.com/HomeHusky/htech-volam-monitor
```

### Kiểm tra MongoDB logs:
1. Vào MongoDB Atlas
2. **Metrics** tab
3. Xem có connection lạ không
4. Nếu có → Block IP ngay

## 🚨 Nếu database bị compromise

1. **Backup ngay:**
   - Export tất cả collections
   - Save ở nơi an toàn

2. **Tạo database mới:**
   - Tạo cluster mới
   - Migrate data
   - Update connection string

3. **Xóa database cũ:**
   - Sau khi verify data mới OK
   - Xóa cluster cũ

## 📞 Liên hệ

Nếu phát hiện hoạt động bất thường:
1. Đổi password ngay
2. Check MongoDB logs
3. Scan malware trên server
4. Review access logs

---

**⚠️ LƯU Ý:** Credentials đã public trên Internet, coi như đã bị lộ. Phải đổi ngay!
