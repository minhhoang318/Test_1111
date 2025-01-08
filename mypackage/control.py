### Các hàm điều khiển thiết bị  ###

# Import các thư viện cần thiết
from .myfunction import mqtt_client
from .speak_hear import speak
from .library import re

# Hàm điều khiển đèn
def control_light(command):
    # Nếu keyword "bật" và "số" trong lệnh của người dùng
    if "bật" in command and "số" in command:
        brightness_level = re.search(r'\d+', command) # Tìm số trong chuỗi
        if brightness_level:
            value = brightness_level.group() # Lấy giá trị số
            speak(f"Tôi đã bật đèn số {value} thưa sếp")
            mqtt_client.publish(f"/AIRC/LED{value}/", "on")
    # Nếu keyword "tắt" và "số" trong lệnh của người dùng
    elif "tắt" in command and "số" in command:
        brightness_level = re.search(r'\d+', command)
        if brightness_level:
            value = brightness_level.group()
            speak(f"Đã tắt đèn số {value} thưa sếp")
            mqtt_client.publish(f"/AIRC/LED{value}/", "off")
    # Nếu lựa chọn bật toàn bộ
    elif "bật" in command and "toàn bộ" in command:
        speak("Thưa sếp toàn bộ đèn đã được bật")
        mqtt_client.publish(f"/AIRC/LED1/", "on")
        mqtt_client.publish(f"/AIRC/LED2/", "on")
        mqtt_client.publish(f"/AIRC/LED3/", "on")
    # Nếu tắt toàn bộ
    elif "tắt" in command and "toàn bộ" in command:
        speak("Thưa sếp toàn bộ đèn đã được tắt")
        mqtt_client.publish(f"/AIRC/LED1/", "off")
        mqtt_client.publish(f"/AIRC/LED2/", "off")
        mqtt_client.publish(f"/AIRC/LED3/", "off")

# Hàm điều khiển quạt
def control_fan(command):
    if "bật" in command and "quạt" in command and "số" in command:
        fan_number = re.search(r'\d+', command)
        level = None
        # Nếu có mức --> điều chỉnh mức quạt
        if "mức" in command:
            level = re.search(r'(25|50|75|99)', command) # Tìm mức quạt

        if fan_number:
            fan_id = fan_number.group()
            if level:
                level_value = level.group()
                speak(f"Tôi đã bật quạt số {fan_id} ở mức {level_value} phần trăm thưa sếp.")
                mqtt_client.publish(f"/AIRC/Fan{fan_id}/", f"{level_value}")
            else:
                speak(f"Tôi đã bật quạt số {fan_id} thưa sếp.")
                mqtt_client.publish(f"/AIRC/Fan{fan_id}/", "50") 
    elif "tắt" in command and "quạt" in command and "số" in command:
        fan_number = re.search(r'\d+', command)
        if fan_number:
            fan_id = fan_number.group()
            speak(f"Đã tắt quạt số {fan_id} thưa sếp.")
            mqtt_client.publish(f"/AIRC/Fan{fan_id}/", "0")
    elif "bật" in command and "toàn bộ" in command:
        speak("Thưa sếp toàn bộ quạt đã được bật ở mức 50 phần trăm mặc định.")
        mqtt_client.publish(f"/AIRC/Fan1/", "50")
        mqtt_client.publish(f"/AIRC/Fan2/", "50")
        mqtt_client.publish(f"/AIRC/Fan3/", "50")
    elif "tắt" in command and "toàn bộ" in command:
        speak("Thưa sếp toàn bộ quạt đã được tắt.")
        mqtt_client.publish(f"/AIRC/Fan1/", "0")
        mqtt_client.publish(f"/AIRC/Fan2/", "0")
        mqtt_client.publish(f"/AIRC/Fan3/", "0")
