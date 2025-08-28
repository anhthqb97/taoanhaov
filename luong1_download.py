#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LUỒNG 1: RESET MÀN HÌNH CHÍNH -> MỞ GOOGLE PLAY -> DOWNLOAD APP LIÊN QUÂN

📝 CẬP NHẬT: Tọa độ nút Install đã được cập nhật thành (2117, 350)
🎯 Nguồn: UI dump từ màn hình thực tế
📱 Màn hình: 2400x1080 (đã xoay 90 độ)
"""
import os
import subprocess
import time

class Luong1Download:
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

    def open_google_play(self):
        """Mở Google Play Store"""
        print("🔍 Mở Google Play Store...")
        
        try:
            # Mở Play Store
            cmd = [
                'adb', '-s', self.device_id, 'shell', 'am', 'start', 
                '-n', 'com.android.vending/.AssetBrowserActivity'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Đã mở Google Play Store")
                time.sleep(5)
                return True
            else:
                print(f"❌ Lỗi mở Play Store: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Lỗi mở Play Store: {str(e)}")
            return False

    def check_app_installed(self):
        """Kiểm tra xem app đã cài đặt chưa bằng cách kiểm tra UI (nút Play/Uninstall)"""
        try:
            print("🔍 Kiểm tra UI để tìm nút Play/Uninstall...")
            
            # Xóa UI dump cũ trước khi lấy mới
            cmd_rm = ['adb', '-s', self.device_id, 'shell', 'rm', '/sdcard/ui_dump.xml']
            subprocess.run(cmd_rm, capture_output=True, text=True)
            
            # Lấy UI dump mới để kiểm tra nút Play/Uninstall
            cmd_dump = ['adb', '-s', self.device_id, 'shell', 'uiautomator', 'dump', '/sdcard/ui_dump.xml']
            result_dump = subprocess.run(cmd_dump, capture_output=True, text=True)
            
            if result_dump.returncode == 0:
                # Kéo file UI dump về máy Mac để tìm kiếm
                temp_file = f"ui_dump_fresh_{self.device_id}.xml"
                cmd_pull = ['adb', '-s', self.device_id, 'pull', '/sdcard/ui_dump.xml', temp_file]
                result_pull = subprocess.run(cmd_pull, capture_output=True, text=True)
                
                if result_pull.returncode == 0:
                    print(f"📁 Đang đọc file: {temp_file}")
                    
                    # Tìm kiếm nút Play hoặc Uninstall trong file đã kéo về
                    with open(temp_file, 'r', encoding='utf-8') as f:
                        content = f.read().lower()
                    
                    print(f"📊 Kích thước file: {len(content)} ký tự")
                    print(f"🔍 Tìm kiếm: 'play' in content = {'play' in content}")
                    print(f"🔍 Tìm kiếm: 'uninstall' in content = {'uninstall' in content}")
                    
                    # Xóa file tạm
                    try:
                        os.remove(temp_file)
                        print(f"🗑️ Đã xóa file: {temp_file}")
                    except:
                        pass
                    
                    # Tìm kiếm chính xác nút Play/Uninstall (không phải từ chung chung)
                    has_play_button = 'text="play"' in content or 'content-desc="play"' in content
                    has_uninstall_button = 'text="uninstall"' in content or 'content-desc="uninstall"' in content
                    
                    print(f"🔍 Nút Play button: {has_play_button}")
                    print(f"🔍 Nút Uninstall button: {has_uninstall_button}")
                    
                    if has_play_button or has_uninstall_button:
                        print("🎯 Tìm thấy nút Play/Uninstall! App đã cài đặt!")
                        return True
                    else:
                        print("❌ Không tìm thấy nút Play/Uninstall")
                        return False
                else:
                    print("❌ Không thể kéo UI dump về máy")
                    return False
            else:
                print("❌ Không thể lấy UI dump")
                return False
                
        except Exception as e:
            print(f"❌ Lỗi kiểm tra UI: {str(e)}")
            return False

    def open_lienquan_page(self):
        """Mở trang Liên Quân Mobile trên Play Store và kiểm tra trạng thái"""
        print("🔍 Mở trang Liên Quân Mobile...")
        
        try:
            # Mở trực tiếp trang app Liên Quân Mobile
            cmd = [
                'adb', '-s', self.device_id, 'shell', 'am', 'start', 
                '-a', 'android.intent.action.VIEW', 
                '-d', 'market://details?id=com.garena.game.kgvn'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Đã mở trang Liên Quân Mobile")
                time.sleep(8)  # Đợi trang load
                
                # Kiểm tra xem có nút Play hoặc Uninstall không
                print("🔍 Kiểm tra trạng thái app...")
                if self.check_app_installed():
                    print("🎉 App đã được cài đặt! Thấy nút Play/Uninstall!")
                    print("💡 Luồng 1 hoàn thành thành công!")
                    return "ALREADY_INSTALLED"
                
                return True
            else:
                print(f"❌ Lỗi mở trang: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Lỗi mở trang: {str(e)}")
            return False

    def click_install_button(self):
        """Click nút Install và kiểm tra kết quả"""
        print("🖱️  Click nút Install...")
        
        try:
            # Tọa độ chính xác của nút Install (từ UI dump)
            # Màn hình: 2400x1080, nút Install bounds: [1959,287][2274,413]
            # Tọa độ trung tâm: X = 2117, Y = 350
            install_x = "2117"
            install_y = "350"
            
            print(f"🎯 Tọa độ nút Install: ({install_x}, {install_y})")
            
            # Click vào nút Install với tọa độ chính xác
            cmd = ['adb', '-s', self.device_id, 'shell', 'input', 'tap', install_x, install_y]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Đã click nút Install!")
                
                # Click thêm vài lần để đảm bảo
                for i in range(3):
                    print(f"   🔄 Click lần {i+1}...")
                    subprocess.run(cmd, capture_output=True, text=True)
                    time.sleep(2)
                
                print("✅ Hoàn tất click nút Install!")
                
                # Kiểm tra xem app đã cài đặt thành công chưa
                print("🔍 Kiểm tra kết quả cài đặt...")
                time.sleep(5)  # Đợi cài đặt bắt đầu
                
                if self.check_app_installed():
                    print("🎉 App đã cài đặt thành công! Thấy nút Play/Uninstall!")
                    print("💡 Luồng 1 hoàn thành thành công!")
                    return "INSTALL_SUCCESS"
                
                return True
                
            else:
                print(f"❌ Lỗi click: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Lỗi click: {str(e)}")
            return False

    def wait_for_installation(self):
        """Đợi cài đặt hoàn tất hoặc kiểm tra đã cài đặt"""
        print("⏳ Kiểm tra trạng thái cài đặt...")
        
        try:
            # Kiểm tra ngay lập tức
            cmd = [
                'adb', '-s', self.device_id, 'shell', 'pm', 'list', 'packages'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0 and 'kgvn' in result.stdout:
                print("🎉 App đã được cài đặt!")
                return True
            
            # Nếu chưa cài đặt, đợi và kiểm tra
            print("⏳ App chưa cài đặt, đợi cài đặt hoàn tất...")
            
            for i in range(60):  # Đợi tối đa 5 phút (60 * 5 giây)
                time.sleep(5)
                print(f"   🔍 Kiểm tra... ({i+1}/60)")
                
                # Kiểm tra UI để tìm nút Play/Uninstall (luôn lấy ảnh mới nhất)
                print("   📸 Lấy UI dump mới nhất...")
                if self.check_app_installed():
                    print("🎉 Cài đặt hoàn tất! Thấy nút Play/Uninstall!")
                    return True
                
                print("   ⏳ Vẫn đang cài đặt...")
            
            print("⏰ Hết thời gian chờ cài đặt")
            return False
            
        except Exception as e:
            print(f"❌ Lỗi đợi cài đặt: {str(e)}")
            return False

    def run_luong1_download(self):
        """Chạy luồng 1: Download app Liên Quân"""
        print("🚀 LUỒNG 1: RESET MÀN HÌNH CHÍNH -> MỞ GOOGLE PLAY -> DOWNLOAD APP LIÊN QUÂN")
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
            
            # Bước 3: Mở Google Play Store
            print("\n🔍 BƯỚC MỞ GOOGLE PLAY STORE...")
            if not self.open_google_play():
                print("❌ Không thể mở Google Play Store")
                return False
            
            # Bước 4: Mở trang Liên Quân Mobile
            print("\n🔍 BƯỚC MỞ TRANG LIÊN QUÂN MOBILE...")
            open_result = self.open_lienquan_page()
            if open_result == "ALREADY_INSTALLED":
                print("🎉 LUỒNG 1 HOÀN THÀNH! App đã cài đặt sẵn!")
                return True
            elif not open_result:
                print("❌ Không thể mở trang Liên Quân Mobile")
                return False
            
            # Bước 5: Click nút Install
            print("\n🖱️  BƯỚC CLICK NÚT INSTALL...")
            click_result = self.click_install_button()
            if click_result == "INSTALL_SUCCESS":
                print("🎉 LUỒNG 1 HOÀN THÀNH! App cài đặt thành công!")
                return True
            elif not click_result:
                print("❌ Không thể click nút Install")
                return False
            
            # Bước 6: Đợi cài đặt hoàn tất (nếu cần)
            print("\n⏳ BƯỚC ĐỢI CÀI ĐẶT HOÀN TẤT...")
            if not self.wait_for_installation():
                print("❌ Cài đặt chưa hoàn tất")
                return False
            
            print("\n🎉 LUỒNG 1 HOÀN THÀNH!")
            print("📱 Liên Quân Mobile đã được cài đặt thành công!")
            return True
            
        except Exception as e:
            print(f"❌ Lỗi trong luồng 1: {str(e)}")
            return False

def main():
    """Hàm chính"""
    luong1 = Luong1Download()
    success = luong1.run_luong1_download()
    
    if success:
        print("\n🎉 LUỒNG 1 THÀNH CÔNG!")
        print("📱 Liên Quân Mobile đã sẵn sàng để chạy!")
    else:
        print("\n⚠️  LUỒNG 1 THẤT BẠI")
        print("💡 Hãy kiểm tra lỗi và thử lại")

if __name__ == "__main__":
    main()
