from threading import Thread
from mypackage.library import *
from mypackage.myfunction import *
from mypackage.speak_hear import *
from datetime import datetime
from gpiozero import LED
from pymongo import MongoClient
import certifi
from time import sleep

# Kết nối tới MongoDB Atlas
server = 'mongodb+srv://ducanhnguyenxuan51:ducanhnguyenxuan51@dataenviromentairc.ux7gs.mongodb.net/?retryWrites=true&w=majority&appName=DataEnviromentAIRC'
client = MongoClient(server, tlsCAFile=certifi.where())
db = client['DataEnviroment']
collection = db['AIRC']

led_speak = LED(23)
led_hear = LED(24)

def get_latest_data():
    """
    Truy vấn dữ liệu mới nhất từ MongoDB
    """
    latest_record = collection.find_one({}, sort=[("date", -1), ("time", -1)])
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
        speak("Thưa sếp")

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
                led_hear.on()
                led_speak.off()
                you = hear()  # Lắng nghe câu nói từ người dùng
                led_hear.off()
                led_speak.on()

                if you is None:
                    speak("Em chưa nghe sếp nói gì, sếp nói lại đi")

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

                elif "baby" in you.lower():
                    speak("Dạ")

                elif "tạm biệt" in you.lower():
                    speak("Tạm biệt sếp")
                    return  # Thoát hẳn chương trình

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

# Chạy Hydro trên một luồng riêng
Thread1 = Thread(target=hydro)
Thread1.start()
