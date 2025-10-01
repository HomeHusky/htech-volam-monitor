@echo off
REM ===============================
REM 🔒 Script sửa lỗi bảo mật
REM ===============================

echo ============================================================
echo 🔒 FIX SECURITY ISSUE
echo ============================================================
echo.

echo ⚠️  MongoDB URI đã bị public trên GitHub!
echo.
echo Cần làm:
echo 1. Đổi mật khẩu MongoDB ngay
echo 2. Xóa Git history
echo 3. Push code mới
echo.

set /p confirm="Bạn đã đổi mật khẩu MongoDB chưa? (y/n): "
if /i not "%confirm%"=="y" (
    echo.
    echo ❌ Vui lòng đổi mật khẩu MongoDB trước!
    echo.
    echo Hướng dẫn:
    echo 1. Vào https://cloud.mongodb.com/
    echo 2. Database Access → Edit user
    echo 3. Edit Password → Tạo mật khẩu mới
    echo 4. Update User
    echo.
    pause
    exit /b 1
)

echo.
echo 🗑️  Xóa Git history...
rmdir /s /q .git
echo ✅ Đã xóa Git history

echo.
echo 📦 Khởi tạo Git mới...
git init
git add .
git commit -m "Security: Remove hardcoded credentials"
echo ✅ Git initialized

echo.
echo 🔗 Add remote...
git remote add origin https://github.com/HomeHusky/htech-volam-monitor
git branch -M main
echo ✅ Remote added

echo.
echo 🚀 Force push...
git push -f origin main

if %errorlevel% equ 0 (
    echo.
    echo ============================================================
    echo ✅ HOÀN TẤT!
    echo ============================================================
    echo.
    echo ✅ Đã xóa credentials khỏi Git history
    echo ✅ Đã push code mới
    echo.
    echo 🚀 Tiếp theo:
    echo 1. Vào Render Dashboard
    echo 2. Environment tab
    echo 3. Add MONGO_URI với mật khẩu MỚI
    echo 4. Save changes
    echo.
) else (
    echo.
    echo ❌ Push thất bại!
    echo Vui lòng chạy thủ công:
    echo   git push -f origin main
)

pause
