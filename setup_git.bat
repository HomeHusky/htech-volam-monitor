@echo off
REM ===============================
REM 🚀 Script setup Git và push lên GitHub (Windows)
REM ===============================

echo ============================================================
echo 🚀 SETUP GIT REPOSITORY
echo ============================================================
echo.

REM Kiểm tra đã có git chưa
if exist ".git" (
    echo ⚠️  Git repository đã tồn tại!
    set /p confirm="Bạn có muốn xóa và tạo mới? (y/n): "
    if /i "%confirm%"=="y" (
        rmdir /s /q .git
        echo ✅ Đã xóa git repository cũ
    ) else (
        echo ❌ Hủy bỏ
        exit /b 1
    )
)

REM Khởi tạo git
echo.
echo 📦 Khởi tạo Git repository...
git init
echo ✅ Git initialized

REM Tạo .gitignore nếu chưa có
if not exist ".gitignore" (
    echo 📝 Tạo .gitignore...
    (
        echo __pycache__/
        echo *.py[cod]
        echo *$py.class
        echo *.so
        echo .Python
        echo env/
        echo venv/
        echo ENV/
        echo .venv
        echo *.log
        echo .env
        echo .DS_Store
    ) > .gitignore
    echo ✅ .gitignore created
)

REM Add files
echo.
echo 📦 Adding files...
git add .
echo ✅ Files added

REM Commit
echo.
echo 💾 Creating initial commit...
git commit -m "Initial commit - Htech Volam Server Monitor"
echo ✅ Commit created

REM Nhập GitHub repository URL
echo.
echo ============================================================
echo 📡 GITHUB REPOSITORY SETUP
echo ============================================================
echo.
echo Vui lòng tạo repository mới trên GitHub:
echo 1. Vào https://github.com/new
echo 2. Repository name: htech-volam-monitor (hoặc tên khác)
echo 3. Chọn Public hoặc Private
echo 4. KHÔNG chọn 'Initialize with README'
echo 5. Click 'Create repository'
echo.
set /p repo_url="Nhập GitHub repository URL (ví dụ: https://github.com/username/repo.git): "

if "%repo_url%"=="" (
    echo ❌ URL không được để trống!
    exit /b 1
)

REM Add remote
echo.
echo 🔗 Adding remote repository...
git remote add origin %repo_url%
echo ✅ Remote added

REM Đổi branch thành main
echo.
echo 🌿 Renaming branch to main...
git branch -M main
echo ✅ Branch renamed

REM Push
echo.
echo 🚀 Pushing to GitHub...
git push -u origin main

if %errorlevel% equ 0 (
    echo.
    echo ============================================================
    echo ✅ THÀNH CÔNG!
    echo ============================================================
    echo.
    echo 📦 Repository đã được push lên GitHub!
    echo 🔗 URL: %repo_url%
    echo.
    echo 🚀 Tiếp theo:
    echo 1. Vào Render.com
    echo 2. New → Web Service
    echo 3. Connect repository vừa tạo
    echo 4. Deploy!
    echo.
) else (
    echo.
    echo ❌ Push thất bại!
    echo Vui lòng kiểm tra:
    echo - GitHub repository URL đúng chưa
    echo - Đã đăng nhập GitHub chưa (git config)
    echo - Repository đã tồn tại chưa
)

pause
