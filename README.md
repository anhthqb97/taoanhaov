# 🎮 LIÊN QUÂN MOBILE AUTOMATION

**Tự động hóa cài đặt và chụp ảnh game Liên Quân Mobile trên Android Emulator**

## 📋 YÊU CẦU HỆ THỐNG

### 🖥️ Hệ điều hành
- **macOS** (đã test trên Mac M3)
- **Windows** (cần điều chỉnh đường dẫn)
- **Linux** (cần điều chỉnh đường dẫn)

### 📱 Android Development
- **Android Studio** (bắt buộc)
- **Android SDK** (tự động cài với Android Studio)
- **Android Emulator** (AVD - Android Virtual Device)

### 🐍 Python
- **Python 3.7+** (khuyến nghị Python 3.9+)
- **pip** (quản lý package)

## 🚀 CÀI ĐẶT

### 1️⃣ Cài đặt Android Studio
```bash
# Tải Android Studio từ trang chủ
https://developer.android.com/studio

# Hoặc dùng Homebrew (macOS)
brew install --cask android-studio
```

### 2️⃣ Cài đặt Android SDK
```bash
# Mở Android Studio
# Vào Tools > SDK Manager
# Cài đặt:
# - Android SDK Platform-Tools
# - Android SDK Build-Tools
# - Android Emulator
# - Android SDK Platform (API 34+)
```

### 3️⃣ Tạo Android Emulator (AVD)
```bash
# Mở Android Studio
# Vào Tools > AVD Manager
# Click "Create Virtual Device"
# Chọn:
# - Category: Phone
# - Device: Pixel 7 (hoặc tương tự)
# - System Image: API 34 (Android 14.0)
# - AVD Name: Medium_Phone_API_36.0
```

#### 🖥️ **Tạo AVD từ Command Line (Khuyến nghị):**
```bash
# Liệt kê system images có sẵn
$ANDROID_HOME/emulator/emulator -list-avds

# Tạo AVD mới (nếu chưa có)
$ANDROID_HOME/tools/bin/avdmanager create avd \
    -n "Medium_Phone_API_36.0" \
    -k "system-images;android-36;google_apis_playstore;arm64-v8a"

# Hoặc tạo AVD với cấu hình cụ thể
$ANDROID_HOME/tools/bin/avdmanager create avd \
    -n "Medium_Phone_API_36.0" \
    -k "system-images;android-36;google_apis_playstore;arm64-v8a" \
    -d "pixel_7" \
    -f

# Xác nhận AVD đã tạo
$ANDROID_HOME/emulator/emulator -list-avds
```

#### 📱 **Cấu hình AVD (Tùy chọn):**
```bash
# Tạo file config cho AVD
mkdir -p ~/.android/avd/Medium_Phone_API_36.0.avd/

# Tạo file config.ini
cat > ~/.android/avd/Medium_Phone_API_36.0.avd/config.ini << EOF
hw.cpu.arch=arm64
hw.cpu.ncore=4
hw.ramSize=4096
hw.screen=touch
hw.mainKeys=no
hw.keyboard=yes
hw.gps=yes
hw.accelerometer=yes
hw.audioInput=yes
hw.audioOutput=yes
hw.camera=yes
hw.camera.front=emulated
hw.camera.back=emulated
hw.battery=yes
hw.sensors.proximity=yes
hw.sensors.magnetic_field=yes
hw.sensors.orientation=yes
hw.sensors.temperature=yes
hw.gpu.enabled=yes
hw.gpu.mode=host
disk.dataPartition.size=10G
showDeviceFrame=yes
EOF
```

### 4️⃣ Cài đặt Python Dependencies
```bash
# Clone repository
git clone <repository-url>
cd lienquan

# Cài đặt dependencies
pip install -r requirements.txt
```

### 5️⃣ Thiết lập Environment Variables
```bash
# macOS/Linux
export ANDROID_HOME=~/Library/Android/sdk
export PATH=$PATH:$ANDROID_HOME/emulator:$ANDROID_HOME/platform-tools

# Windows
set ANDROID_HOME=C:\Users\%USERNAME%\AppData\Local\Android\Sdk
set PATH=%PATH%;%ANDROID_HOME%\emulator;%ANDROID_HOME%\platform-tools
```

## 🎯 CHỨC NĂNG CHÍNH

### 🔄 LUỒNG 1: CÀI ĐẶT APP
**Mục đích:** Tự động cài đặt Liên Quân Mobile từ Google Play Store

**Quy trình:**
1. **Reset** về màn hình chính
2. **Mở** Google Play Store
3. **Mở** trang Liên Quân Mobile
4. **Click** nút Install
5. **Đợi** cài đặt hoàn tất
6. **Phát hiện** nút Play/Uninstall

**Chạy:**
```bash
python3 luong1_download.py
```

### 📸 LUỒNG 2: LAUNCH & SCREENSHOT
**Mục đích:** Khởi chạy app và chụp ảnh màn hình

**Quy trình:**
1. **Reset** về màn hình chính
2. **Kiểm tra** app đã cài đặt
3. **Tìm** app Liên Quân Mobile
4. **Khởi chạy** app
5. **Chụp** ảnh màn hình

**Chạy:**
```bash
python3 luong2_launch_screenshot.py
```

## 🛠️ CÁCH SỬ DỤNG

### 🚀 Khởi động Emulator
```bash
# Khởi động emulator
$ANDROID_HOME/emulator/emulator -avd Medium_Phone_API_36.0

# Hoặc mở từ Android Studio
# Tools > AVD Manager > Play button
```

### 🔍 Kiểm tra Kết nối
```bash
# Kiểm tra emulator đã sẵn sàng
adb devices

# Kết quả mong đợi:
# List of devices attached
# emulator-5554   device
```

### 📱 Chạy Luồng 1 (Cài đặt)
```bash
# Chạy luồng cài đặt
python3 luong1_download.py

# Kết quả mong đợi:
# 🎉 LUỒNG 1 THÀNH CÔNG!
# 📱 Liên Quân Mobile đã sẵn sàng để chạy!
```

### 📸 Chạy Luồng 2 (Screenshot)
```bash
# Chạy luồng screenshot
python3 luong2_launch_screenshot.py

# Kết quả mong đợi:
# 🎉 LUỒNG 2 THÀNH CÔNG!
# 📸 Screenshot Liên Quân Mobile đã hoàn tất!
```

## 🚀 SAMPLE ALL STEPS - CHẠY TOÀN BỘ QUY TRÌNH

### 📋 **BƯỚC 1: CHUẨN BỊ MÔI TRƯỜNG**
```bash
# Thiết lập environment variables
export ANDROID_HOME=~/Library/Android/sdk
export PATH=$PATH:$ANDROID_HOME/emulator:$ANDROID_HOME/platform-tools

# Kiểm tra ADB
adb version

# Kiểm tra emulator có sẵn
$ANDROID_HOME/emulator/emulator -list-avds
```

### 📱 **BƯỚC 1.5: TẠO AVD (NẾU CHƯA CÓ)**
```bash
# Kiểm tra system images có sẵn
$ANDROID_HOME/tools/bin/sdkmanager --list | grep "system-images"

# Tạo AVD mới nếu chưa có
if ! $ANDROID_HOME/emulator/emulator -list-avds | grep -q "Medium_Phone_API_36.0"; then
    echo "📱 Tạo AVD mới..."
    
    # Tạo AVD với cấu hình cơ bản
    $ANDROID_HOME/tools/bin/avdmanager create avd \
        -n "Medium_Phone_API_36.0" \
        -k "system-images;android-36;google_apis_playstore;arm64-v8a" \
        -d "pixel_7" \
        -f
    
    echo "✅ AVD đã được tạo!"
else
    echo "✅ AVD đã tồn tại!"
fi

# Xác nhận AVD
$ANDROID_HOME/emulator/emulator -list-avds
```

### 📱 **BƯỚC 2: KHỞI ĐỘNG EMULATOR**
```bash
# Khởi động emulator
$ANDROID_HOME/emulator/emulator -avd Medium_Phone_API_36.0 &

# Đợi emulator khởi động (khoảng 30-60 giây)
sleep 45

# Kiểm tra emulator đã sẵn sàng
adb devices
```

### 🔍 **BƯỚC 3: KIỂM TRA TRẠNG THÁI HIỆN TẠI**
```bash
# Kiểm tra Liên Quân Mobile đã cài đặt chưa
adb -s emulator-5554 shell pm list packages | grep kgvn

# Nếu có kết quả -> app đã cài đặt
# Nếu không có -> cần chạy luồng 1
```

### 🔄 **BƯỚC 4: CHẠY LUỒNG 1 - CÀI ĐẶT APP**
```bash
# Chạy luồng cài đặt
python3 luong1_download.py

# Kết quả mong đợi:
# 🎉 LUỒNG 1 THÀNH CÔNG!
# 📱 Liên Quân Mobile đã sẵn sàng để chạy!
```

### 📸 **BƯỚC 5: CHẠY LUỒNG 2 - SCREENSHOT**
```bash
# Chạy luồng screenshot
python3 luong2_launch_screenshot.py

# Kết quả mong đợi:
# 🎉 LUỒNG 2 THÀNH CÔNG!
# 📸 Screenshot Liên Quân Mobile đã hoàn tất!
```

### 🎯 **BƯỚC 6: KIỂM TRA KẾT QUẢ**
```bash
# Xem danh sách screenshot
ls -la screenshots/

# Xem screenshot mới nhất
ls -la screenshots/lienquan_luong2_*.png | tail -1
```

## 🚀 **SAMPLE COMPLETE WORKFLOW - MỘT LỆNH DUY NHẤT**

### 💻 **Script tự động hoàn chỉnh:**
```bash
#!/bin/bash
# Liên Quân Mobile Complete Workflow

echo "🚀 LIÊN QUÂN MOBILE COMPLETE WORKFLOW"
echo "======================================"

# Bước 1: Thiết lập environment
export ANDROID_HOME=~/Library/Android/sdk
export PATH=$PATH:$ANDROID_HOME/emulator:$ANDROID_HOME/platform-tools

# Bước 1.5: Tạo AVD nếu chưa có
echo "📱 Kiểm tra và tạo AVD..."
if ! $ANDROID_HOME/emulator/emulator -list-avds | grep -q "Medium_Phone_API_36.0"; then
    echo "   📱 Tạo AVD mới..."
    $ANDROID_HOME/tools/bin/avdmanager create avd \
        -n "Medium_Phone_API_36.0" \
        -k "system-images;android-36;google_apis_playstore;arm64-v8a" \
        -d "pixel_7" \
        -f
    echo "   ✅ AVD đã được tạo!"
else
    echo "   ✅ AVD đã tồn tại!"
fi

# Bước 2: Khởi động emulator
echo "📱 Khởi động emulator..."
$ANDROID_HOME/emulator/emulator -avd Medium_Phone_API_36.0 &
EMULATOR_PID=$!

# Bước 3: Đợi emulator sẵn sàng
echo "⏳ Đợi emulator khởi động..."
sleep 45

# Bước 4: Kiểm tra kết nối
echo "🔍 Kiểm tra kết nối..."
until adb devices | grep -q "emulator-5554.*device"; do
    echo "   ⏳ Đợi emulator..."
    sleep 5
done
echo "✅ Emulator đã sẵn sàng!"

# Bước 5: Chạy luồng 1
echo "🔄 Chạy luồng 1 - Cài đặt app..."
python3 luong1_download.py
if [ $? -eq 0 ]; then
    echo "✅ Luồng 1 thành công!"
else
    echo "❌ Luồng 1 thất bại!"
    kill $EMULATOR_PID
    exit 1
fi

# Bước 6: Chạy luồng 2
echo "📸 Chạy luồng 2 - Screenshot..."
python3 luong2_launch_screenshot.py
if [ $? -eq 0 ]; then
    echo "✅ Luồng 2 thành công!"
else
    echo "❌ Luồng 2 thất bại!"
fi

# Bước 7: Hiển thị kết quả
echo "🎉 WORKFLOW HOÀN THÀNH!"
echo "📱 Liên Quân Mobile đã được cài đặt và chụp ảnh!"
echo "📸 Screenshot: screenshots/lienquan_luong2_*.png"

# Bước 8: Tắt emulator (tùy chọn)
read -p "🔄 Bạn có muốn tắt emulator không? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🛑 Tắt emulator..."
    kill $EMULATOR_PID
    adb kill-server
fi

echo "🎮 Chúc bạn test Liên Quân Mobile thành công!"
```

### 📝 **Cách sử dụng script:**
```bash
# Tạo file script
nano lienquan_complete_workflow.sh

# Copy nội dung trên vào file

# Cấp quyền thực thi
chmod +x lienquan_complete_workflow.sh

# Chạy script
./lienquan_complete_workflow.sh
```

## 📁 CẤU TRÚC PROJECT

```
lienquan/
├── README.md                    # Hướng dẫn này
├── requirements.txt             # Python dependencies
├── luong1_download.py          # Luồng 1: Cài đặt app
├── luong2_launch_screenshot.py # Luồng 2: Launch & Screenshot
├── screenshots/                 # Thư mục chứa ảnh
│   ├── lienquan_luong2_*.png   # Screenshot từ luồng 2
│   └── current_ui.png          # Ảnh debug UI
└── .gitignore                  # Git ignore rules
```

## 🔧 TROUBLESHOOTING

### ❌ Emulator không khởi động
```bash
# Kiểm tra AVD
$ANDROID_HOME/emulator/emulator -list-avds

# Xóa và tạo lại AVD nếu cần
# Android Studio > AVD Manager > Delete > Create
```

### ❌ Không thể tạo AVD
```bash
# Kiểm tra system images
$ANDROID_HOME/tools/bin/sdkmanager --list | grep "system-images"

# Cài đặt system image nếu chưa có
$ANDROID_HOME/tools/bin/sdkmanager "system-images;android-36;google_apis_playstore;arm64-v8a"

# Kiểm tra quyền thư mục
ls -la ~/.android/avd/

# Tạo thư mục nếu chưa có
mkdir -p ~/.android/avd/
```

### ❌ AVD bị lỗi
```bash
# Xóa AVD bị lỗi
$ANDROID_HOME/tools/bin/avdmanager delete avd -n "Medium_Phone_API_36.0"

# Tạo lại AVD
$ANDROID_HOME/tools/bin/avdmanager create avd \
    -n "Medium_Phone_API_36.0" \
    -k "system-images;android-36;google_apis_playstore;arm64-v8a" \
    -d "pixel_7" \
    -f
```

### ❌ ADB không kết nối
```bash
# Khởi động lại ADB
adb kill-server
adb start-server

# Kiểm tra emulator
adb devices
```

### ❌ App không cài đặt được
```bash
# Kiểm tra Google Play Store đã đăng nhập
# Mở Play Store thủ công và đăng nhập Google Account

# Xóa cache Play Store
adb -s emulator-5554 shell pm clear com.android.vending
```

### ❌ Screenshot không chụp được
```bash
# Kiểm tra quyền ghi file
ls -la screenshots/

# Tạo thư mục nếu chưa có
mkdir -p screenshots
```

## 📱 YÊU CẦU EMULATOR

### 💾 RAM
- **Tối thiểu:** 4GB
- **Khuyến nghị:** 8GB+

### 💿 Dung lượng
- **Tối thiểu:** 10GB trống
- **Khuyến nghị:** 20GB+ trống

### 🖥️ GPU
- **macOS:** Metal support (M1/M2/M3)
- **Windows:** DirectX 11+
- **Linux:** OpenGL 3.0+

## 🔒 BẢO MẬT

### ⚠️ Lưu ý quan trọng
- **Không chia sẻ** Google Account credentials
- **Không commit** file chứa thông tin cá nhân
- **Sử dụng** emulator riêng cho testing

### 🛡️ Best Practices
- **Luôn** đăng xuất Google Account sau khi test
- **Xóa** cache và data của Play Store
- **Khởi động lại** emulator giữa các lần test

## 📞 HỖ TRỢ

### 🐛 Báo lỗi
Nếu gặp vấn đề, hãy:
1. **Kiểm tra** log output
2. **Xác nhận** emulator đã sẵn sàng
3. **Kiểm tra** Google Play Store đã đăng nhập
4. **Tạo issue** với thông tin chi tiết

### 📧 Liên hệ
- **Repository:** [GitHub URL]
- **Issues:** [GitHub Issues]
- **Documentation:** [Wiki]

## 📄 LICENSE

**MIT License** - Xem file LICENSE để biết thêm chi tiết.

---

**🎮 Chúc bạn test Liên Quân Mobile thành công!**
