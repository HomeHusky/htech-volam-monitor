#!/bin/bash

# ===============================
# 🚀 Script setup Git và push lên GitHub
# ===============================

echo "============================================================"
echo "🚀 SETUP GIT REPOSITORY"
echo "============================================================"
echo ""

# Kiểm tra đã có git chưa
if [ -d ".git" ]; then
    echo "⚠️  Git repository đã tồn tại!"
    read -p "Bạn có muốn xóa và tạo mới? (y/n): " confirm
    if [ "$confirm" = "y" ]; then
        rm -rf .git
        echo "✅ Đã xóa git repository cũ"
    else
        echo "❌ Hủy bỏ"
        exit 1
    fi
fi

# Khởi tạo git
echo ""
echo "📦 Khởi tạo Git repository..."
git init
echo "✅ Git initialized"

# Tạo .gitignore nếu chưa có
if [ ! -f ".gitignore" ]; then
    echo "📝 Tạo .gitignore..."
    cat > .gitignore << 'EOF'
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
.venv
*.log
.env
.DS_Store
EOF
    echo "✅ .gitignore created"
fi

# Add files
echo ""
echo "📦 Adding files..."
git add .
echo "✅ Files added"

# Commit
echo ""
echo "💾 Creating initial commit..."
git commit -m "Initial commit - Htech Volam Server Monitor"
echo "✅ Commit created"

# Nhập GitHub repository URL
echo ""
echo "============================================================"
echo "📡 GITHUB REPOSITORY SETUP"
echo "============================================================"
echo ""
echo "Vui lòng tạo repository mới trên GitHub:"
echo "1. Vào https://github.com/new"
echo "2. Repository name: htech-volam-monitor (hoặc tên khác)"
echo "3. Chọn Public hoặc Private"
echo "4. KHÔNG chọn 'Initialize with README'"
echo "5. Click 'Create repository'"
echo ""
read -p "Nhập GitHub repository URL (ví dụ: https://github.com/username/repo.git): " repo_url

if [ -z "$repo_url" ]; then
    echo "❌ URL không được để trống!"
    exit 1
fi

# Add remote
echo ""
echo "🔗 Adding remote repository..."
git remote add origin "$repo_url"
echo "✅ Remote added"

# Đổi branch thành main
echo ""
echo "🌿 Renaming branch to main..."
git branch -M main
echo "✅ Branch renamed"

# Push
echo ""
echo "🚀 Pushing to GitHub..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "============================================================"
    echo "✅ THÀNH CÔNG!"
    echo "============================================================"
    echo ""
    echo "📦 Repository đã được push lên GitHub!"
    echo "🔗 URL: $repo_url"
    echo ""
    echo "🚀 Tiếp theo:"
    echo "1. Vào Render.com"
    echo "2. New → Web Service"
    echo "3. Connect repository vừa tạo"
    echo "4. Deploy!"
    echo ""
else
    echo ""
    echo "❌ Push thất bại!"
    echo "Vui lòng kiểm tra:"
    echo "- GitHub repository URL đúng chưa"
    echo "- Đã đăng nhập GitHub chưa (git config)"
    echo "- Repository đã tồn tại chưa"
fi
