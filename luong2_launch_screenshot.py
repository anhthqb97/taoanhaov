#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LUỒNG 2: RESET MÀN HÌNH CHÍNH -> TÌM APP LIÊN QUÂN -> MỞ APP -> CHỤP HÌNH
"""
import os
import subprocess
import time

class Luong2LaunchScreenshot:
    def __init__(self):
        self.device_id = None
        
        # Thiết lập environment
        self.android_home = os.path.expanduser('~/Library/Android/sdk')
        os.environ['ANDROID_HOME'] = self.android_home
        os.environ['PATH'] = f"{os.environ.get('PATH', '')}:{self.android_home}/emulator:{self.android_home}/platform-tools"

    def check_environment(self):
        """Kiểm tra môi trường"""
        print("🔍 Kiểm tra môi trường...")
        
        try:
            result = subprocess.run(['adb', 'version'], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ ADB: Đã cài đặt")
            else:
                print("❌ ADB không hoạt động")
                return False
        except Exception as e:
            print(f"❌ Lỗi kiểm tra ADB: {str(e)}")
            return False
        
        # Kiểm tra emulator
        try:
            result = subprocess.run(['adb', 'devices'], capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]
                devices = [line.split('\t')[0] for line in lines if line.strip() and '\t' in line]
                if devices:
                    self.device_id = devices[0]
                    print(f"✅ Emulator: {self.device_id}")
                else:
                    print("⚠️  Không có emulator nào")
                    return False
            else:
                print("❌ Lỗi kiểm tra thiết bị")
                return False
        except Exception as e:
            print(f"❌ Lỗi kiểm tra emulator: {str(e)}")
            return False
        
        return True

    def reset_to_home_screen(self):
        """Reset về màn hình chính"""
        print("🏠 Reset về màn hình chính...")
        
        try:
            # Nhấn nút Home
            cmd = ['adb', '-s', self.device_id, 'shell', 'input', 'keyevent', '3']
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Đã về màn hình chính")
                time.sleep(2)
                return True
            else:
                print(f"❌ Lỗi về màn hình chính: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Lỗi về màn hình chính: {str(e)}")
            return False

    def check_lienquan_installed(self):
        """Kiểm tra Liên Quân Mobile đã được cài đặt chưa"""
        print("🔍 Kiểm tra Liên Quân Mobile đã cài đặt...")
        
        try:
            # Không dùng shell=True để tránh lỗi trên Mac
            cmd = [
                'adb', '-s', self.device_id, 'shell', 'pm', 'list', 'packages'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0 and 'kgvn' in result.stdout:
                print("✅ Liên Quân Mobile đã được cài đặt!")
                return True
            else:
                print("❌ Liên Quân Mobile chưa được cài đặt")
                return False
                
        except Exception as e:
            print(f"❌ Lỗi kiểm tra app: {str(e)}")
            return False

    def find_lienquan_app(self):
        """Tìm app Liên Quân Mobile trên màn hình chính"""
        print("🔍 Tìm app Liên Quân Mobile trên màn hình chính...")
        
        try:
            # Sử dụng am start để mở app trực tiếp
            cmd = [
                'adb', '-s', self.device_id, 'shell', 'am', 'start', 
                '-n', 'com.garena.game.kgvn/com.garena.game.kgtw.SGameActivity'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Đã tìm thấy và mở app Liên Quân Mobile!")
                time.sleep(3)  # Đợi app khởi động
                return True
            else:
                print(f"❌ Lỗi mở app: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Lỗi mở app: {str(e)}")
            return False

    def launch_lienquan(self):
        """Khởi chạy app Liên Quân Mobile"""
        print("🚀 Khởi chạy app Liên Quân Mobile...")
        
        try:
            # Sử dụng am start để mở app
            cmd = [
                'adb', '-s', self.device_id, 'shell', 'am', 'start', 
                '-n', 'com.garena.game.kgvn/com.garena.game.kgtw.SGameActivity'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Đã khởi chạy app!")
                time.sleep(5)  # Đợi app load hoàn toàn
                return True
            else:
                print(f"❌ Lỗi khởi chạy app: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Lỗi khởi chạy app: {str(e)}")
            return False

    def take_screenshot(self):
        """Chụp ảnh màn hình"""
        print("📸 Chụp ảnh màn hình...")
        
        try:
            # Tạo thư mục screenshots nếu chưa có
            os.makedirs('screenshots', exist_ok=True)
            
            # Tạo tên file với timestamp
            timestamp = int(time.time())
            filename = f"screenshots/lienquan_luong2_{timestamp}.png"
            
            # Chụp ảnh màn hình
            cmd = [
                'adb', '-s', self.device_id, 'shell', 'screencap', '-p', '/sdcard/screenshot.png'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                # Kéo ảnh về máy
                cmd_pull = [
                    'adb', '-s', self.device_id, 'pull', '/sdcard/screenshot.png', filename
                ]
                
                result_pull = subprocess.run(cmd_pull, capture_output=True, text=True)
                if result_pull.returncode == 0:
                    print(f"✅ Đã chụp ảnh: {filename}")
                    return filename
                else:
                    print(f"❌ Lỗi kéo ảnh: {result_pull.stderr}")
                    return False
            else:
                print(f"❌ Lỗi chụp ảnh: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Lỗi chụp ảnh: {str(e)}")
            return False

    def run_luong2_launch_screenshot(self):
        """Chạy luồng 2: Launch app và chụp ảnh"""
        print("🚀 LUỒNG 2: RESET MÀN HÌNH CHÍNH -> TÌM APP LIÊN QUÂN -> MỞ APP -> CHỤP HÌNH")
        print("=" * 80)
        
        try:
            # Bước 1: Kiểm tra môi trường
            if not self.check_environment():
                print("❌ Môi trường chưa sẵn sàng")
                return False
            
            # Bước 2: Reset về màn hình chính
            print("\n🏠 BƯỚC RESET VỀ MÀN HÌNH CHÍNH...")
            if not self.reset_to_home_screen():
                print("❌ Không thể reset về màn hình chính")
                return False
            
            # Bước 3: Kiểm tra Liên Quân Mobile
            print("\n🔍 BƯỚC KIỂM TRA LIÊN QUÂN MOBILE...")
            if not self.check_lienquan_installed():
                print("❌ Liên Quân Mobile chưa được cài đặt")
                print("💡 Hãy chạy LUỒNG 1 trước để cài đặt app")
                return False
            
            # Bước 4: Tìm app Liên Quân Mobile
            print("\n🔍 BƯỚC TÌM APP LIÊN QUÂN MOBILE...")
            if not self.find_lienquan_app():
                print("❌ Không thể tìm app Liên Quân Mobile")
                return False
            
            # Bước 5: Khởi chạy app
            print("\n🚀 BƯỚC KHỞI CHẠY APP...")
            if not self.launch_lienquan():
                print("❌ Không thể khởi chạy app")
                return False
            
            # Bước 6: Chụp ảnh màn hình
            print("\n📸 BƯỚC CHỤP ẢNH MÀN HÌNH...")
            screenshot_file = self.take_screenshot()
            if not screenshot_file:
                print("❌ Không thể chụp ảnh")
                return False
            
            print("\n🎉 LUỒNG 2 HOÀN THÀNH!")
            print(f"📸 Screenshot: {screenshot_file}")
            return True
            
        except Exception as e:
            print(f"❌ Lỗi trong luồng 2: {str(e)}")
            return False

def main():
    """Hàm chính"""
    luong2 = Luong2LaunchScreenshot()
    success = luong2.run_luong2_launch_screenshot()
    
    if success:
        print("\n🎉 LUỒNG 2 THÀNH CÔNG!")
        print("📸 Screenshot Liên Quân Mobile đã hoàn tất!")
    else:
        print("\n⚠️  LUỒNG 2 THẤT BẠI")
        print("💡 Hãy kiểm tra lỗi và thử lại")

if __name__ == "__main__":
    main()
