from mypackage.library import *
from mypackage.myfunction import *
from mypackage.speak_hear import *
from datetime import datetime
from gpiozero import LED
from pymongo import MongoClient
import certifi
from time import sleep
import re

import paho.mqtt.client as mqtt

# Kết nối tới MongoDB Atlas
server = 'mongodb+srv://ducanhnguyenxuan51:ducanhnguyenxuan51@dataenviromentairc.ux7gs.mongodb.net/?retryWrites=true&w=majority&appName=DataEnviromentAIRC'
client = MongoClient(server, tlsCAFile=certifi.where())
db = client['DataEnviroment']
collection = db['AIRC']

led_speak = LED(23)
led_hear = LED(24)


# Thiết lập MQTT
broker = "broker.emqx.io"
port = 1883
topic = "/AIRC/Fan1/"
mqtt_client = mqtt.Client()

# Hàm callback khi kết nối MQTT
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe(topic)

# Hàm callback khi nhận thông điệp từ broker
def on_message(client, userdata, msg):
    message = msg.payload.decode()
    print(f"Message received: {message}")

# Kết nối MQTT
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(broker, port, 60)
mqtt_client.loop_start()

def get_latest_data():
    """
    Truy vấn dữ liệu mới nhất từ MongoDB
    """
    latest_record = collection.find_one({}, {"temp": 1, "humi": 1, "_id": 0}, sort=[("date", -1), ("time", -1)])

    if latest_record:
        temp = latest_record.get('temp')
        humi = latest_record.get('humi')
        return temp, humi
    return None, None

def hydro():
    try:
        # Đọc câu hỏi và câu trả lời từ tệp
        with open("database/question.txt", mode="r", encoding="utf8") as f:
            questions = f.readlines()
        
        with open("database/answer.txt", mode="r", encoding="utf8") as f:
            answers = f.readlines()

        led_hear.off()
        led_speak.on()

        while True:
            # Lắng nghe lệnh "xin chào" để bắt đầu tương tác
            while True:
                led_hear.on()
                led_speak.off()
                you = hear()  # Lắng nghe câu nói từ người dùng
                led_hear.off()
                led_speak.on()

                if you is None:
                    continue  # Nếu không nghe thấy gì, tiếp tục lắng nghe
                elif "thư ký" in you.lower():
                    speak("Dạ")
                    break

            # Bắt đầu lắng nghe và phản hồi các lệnh của người dùng
            while True:
                you = hear()  # Lắng nghe câu nói từ người dùng

                if you is None:
                    #speak("Em chưa nghe sếp nói gì, sếp nói lại đi")
                    led_hear.on()
                    led_speak.off()

                # Kiểm tra câu hỏi về nhiệt độ
                elif "nhiệt độ" in you.lower():
                    temp, _ = get_latest_data()
                    if temp is not None:
                        speak(f"Nhiệt độ hiện tại là {temp} độ C")
                    else:
                        speak("Em không tìm thấy dữ liệu về nhiệt độ.")

                # Kiểm tra câu hỏi về độ ẩm
                elif "độ ẩm" in you.lower():
                    _, humi = get_latest_data()
                    if humi is not None:
                        speak(f"Độ ẩm hiện tại là {humi} phần trăm")
                    else:
                        speak("Em không tìm thấy dữ liệu về độ ẩm")

                elif "hôm nay" in you or "bây giờ" in you:
                    now = datetime.now()
                    if "giờ" in you:
                        t = f"Bây giờ là: {now.strftime('%H:%M:%S')}"
                        speak(t)
                    if "ngày" in you:
                        t = now.strftime("Hôm nay là ngày %d tháng %m năm %Y")
                        speak(t)
                elif you is not None and "điều chỉnh quạt" in you:
                    brightness_level = re.search(r'\d+', you)  # Tìm các chữ số trong chuỗi
                    if brightness_level:
                        value = brightness_level.group()  # Lấy giá trị số từ chuỗi
                        speak(f"Đã điều chỉnh quạt {value} phần trăm")
                        mqtt_client.publish(topic, f"{value}")
                        #time.sleep(1)
                        
                    else:
                        speak("Vui lòng nhập nằm trong khoảng từ 0 đến 100. Xin vui lòng nhập lại!")

                elif "tạm biệt" in you.lower():
                    speak("Tạm biệt sếp")
                    return

                else:
                    # Tìm kiếm câu hỏi phù hợp trong tệp và phản hồi câu trả lời
                    idx = handle_data(you)
                    if idx is not None:
                        speak(answers[idx])
                    else:
                        speak("Dạ sếp nói lại đi em không hiểu")

                # Sau mỗi câu trả lời, quay lại trạng thái chờ lệnh "xin chào"
                break

    except Exception as e:
        print(f"Lỗi trong hàm hydro: {e}")

# Gọi trực tiếp hàm hydro mà không cần dùng phân luồng
hydro()
