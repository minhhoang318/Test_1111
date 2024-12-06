from mypackage.library import *
from mypackage.myfunction import *
from mypackage.speak_hear import *
from datetime import datetime
#from gpiozero import LED
from pymongo import MongoClient
import certifi
from time import sleep
import re
import wikipedia 
import paho.mqtt.client as mqtt

# Kết nối tới MongoDB Atlas
server = 'mongodb+srv://ducanhnguyenxuan51:ducanhnguyenxuan51@dataenviromentairc.ux7gs.mongodb.net/?retryWrites=true&w=majority&appName=DataEnviromentAIRC'
client = MongoClient(server, tlsCAFile=certifi.where())
db = client['DataEnviroment']
collection = db['AIRC']

#led_speak = LED(23)
#led_hear = LED(24)


# Thiết lập MQTT
broker = "broker.emqx.io"
port = 1883
mqtt_client = mqtt.Client()

# Hàm callback khi kết nối MQTT
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

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

wikipedia.set_lang("vi")
def wiki_search(text):
    try:
        infor = wikipedia.summary(text).split('\n')
        speak(infor[0].split(".")[0])
        for a in infor[1:]:
            speak("Sếp muốn nghe thêm không ?")
            ans = hear()
            if "có" not in ans:
                break
            print(a)

        speak("Cảm ơn sếp")

    except:
        speak("Tôi không tìm được thông tin thưa sếp")

def hydro():
    while True:
        try:
            # Đọc câu hỏi và câu trả lời từ tệp
            with open("database/question.txt", mode="r", encoding="utf8") as f:
                questions = f.readlines()
            
            with open("database/answer.txt", mode="r", encoding="utf8") as f:
                answers = f.readlines()
    
           # led_hear.off()
           # led_speak.on()
    
            while True:
                # Lắng nghe lệnh "xin chào" để bắt đầu tương tác
                while True:
                    #led_hear.on()
                    #led_speak.off()
                    you = hear()  # Lắng nghe câu nói từ người dùng
                    #led_hear.off()
                    #led_speak.on()
    
                    if you is None:
                        continue  # Nếu không nghe thấy gì, tiếp tục lắng nghe
                    elif "thư ký" in you.lower():
                        speak("Dạ")
                        break
    
                # Bắt đầu lắng nghe và phản hồi các lệnh của người dùng
                while True:
                    you = hear()  # Lắng nghe câu nói từ người dùng
    
                    if you is None:
                        speak("Tôi chưa nghe sếp nói gì, sếp nói lại đi")
                        led_hear.on()
                        led_speak.off()
                        continue
    
                    elif "nhiệt độ" in you.lower():
                        temp, _ = get_latest_data()
                        if temp is not None:
                            temp = int(temp)
                            speak(f"Nhiệt độ hiện tại là {temp} độ C")
    
                            # Kiểm tra nhiệt độ nóng hoặc lạnh
                            if temp > 30:
                                speak("Nhiệt độ hiện tại khá nóng. Sếp có muốn bật điều hoà không?")
                            elif temp < 20:
                                speak("Nhiệt độ hiện tại khá lạnh. Sếp có muốn tăng nhiệt độ điều hoà lên không?")
                            else:
                                speak("Nhiệt độ hiện tại khá dễ chịu.")
                        else:
                            speak("Tôi không tìm thấy dữ liệu về nhiệt độ.")
    
                    # Kiểm tra câu hỏi về độ ẩm
                    elif "độ ẩm" in you.lower():
                        _, humi = get_latest_data()
                        if humi is not None:
                            humi = int(humi)
                            speak(f"Độ ẩm hiện tại là {humi} phần trăm")
    
                            # Kiểm tra độ ẩm cao hoặc thấp
                            if humi > 70:
                                speak("Độ ẩm hiện tại khá cao. Sếp có muốn bật máy hút ẩm không?")
                            elif humi < 30:
                                speak("Độ ẩm hiện tại khá thấp. Sếp có muốn bật máy tạo ẩm không?")
                            else:
                                speak("Độ ẩm hiện tại khá ổn định.")
                        else:
                            speak("Tôi không tìm thấy dữ liệu về độ ẩm")
    
                    elif "hôm nay" in you or "bây giờ" in you:
                        now = datetime.now()
                        if "giờ" in you:
                            t = f"Bây giờ là: {now.strftime('%H:%M:%S')}"
                            speak(t)
                        if "ngày" in you:
                            t = now.strftime("Hôm nay là ngày %d tháng %m năm %Y")
                            speak(t)
                            
                    elif you is not None and "quạt" in you:
                        if ("bật" in you or "điều chỉnh" in you) and "mức" in you:  # Kiểm tra nếu có "bật" hoặc "điều chỉnh" và có "mức"
                            brightness_level = re.search(r'\d+', you)  # Tìm các chữ số trong chuỗi
                            if brightness_level:
                                value = brightness_level.group()  # Lấy giá trị số từ chuỗi
                                speak(f"Tôi đã điều chỉnh quạt ở mức {value} phần trăm")
                                mqtt_client.publish("/AIRC/Fan1/", f"{value}")  # Gửi giá trị bật/điều chỉnh quạt lên MQTT
                        elif "tắt" in you:
                            speak("Vâng, tôi sẽ tắt quạt")
                            mqtt_client.publish("/AIRC/Fan1/", "0")
    
                    elif you is not None and "đèn" in you:
                        if "bật" in you and "số" in you:
                            brightness_level = re.search(r'\d+', you)  # Tìm các chữ số trong chuỗi
                            if brightness_level:
                                value = brightness_level.group()  # Lấy giá trị số từ chuỗi
                                speak(f"Tôi đã bật đèn số {value} thưa sếp")
                                mqtt_client.publish(f"/AIRC/LED{value}/", "on") 
                    
                        elif "tắt" in you and "số" in you:
                            brightness_level = re.search(r'\d+', you)  # Tìm các chữ số trong chuỗi
                            if brightness_level:
                                value = brightness_level.group()  # Lấy giá trị số từ chuỗi
                                speak(f"Đã tắt đèn số {value} thưa sếp")
                                mqtt_client.publish(f"/AIRC/LED{value}/", "off") 
                                #time.sleep(1)
                        elif "bật" in you and "toàn bộ" in you:
                            speak("Thưa sếp toàn bộ đèn đã được bật")
                            mqtt_client.publish(f"/AIRC/LED1/", "on")
                            mqtt_client.publish(f"/AIRC/LED2/", "on")
                            mqtt_client.publish(f"/AIRC/LED3/", "on")
                            
                        elif "tắt" in you and "toàn bộ" in you:
                            speak("Thưa sếp toàn bộ đèn đã được tắt")
                            mqtt_client.publish(f"/AIRC/LED1/", "off")
                            mqtt_client.publish(f"/AIRC/LED2/", "off")
                            mqtt_client.publish(f"/AIRC/LED3/", "off")
                  
                    # Kiểm tra nếu người dùng yêu cầu tìm kiếm thông tin trên Wikipedia
                    elif "tìm kiếm" in you or "wikipedia" in you:
                        query = you.replace("tìm kiếm", "").replace("wikipedia", "").strip()  # Lấy từ khóa cần tìm
                        wiki_search(query)
    
                    elif "tạm biệt" in you.lower():
                        speak("Tạm biệt sếp")
                        return
                        
    
                    else:
                        # Tìm kiếm câu hỏi phù hợp trong tệp và phản hồi câu trả lời
                        idx = handle_data(you)
                        if idx is not None:
                            speak(answers[idx])
                        else:
                            speak("Tôi không có thông tin thưa sếp")
    
                    # Sau mỗi câu trả lời, quay lại trạng thái chờ lệnh "xin chào"
                    break
    
        except Exception as e:
            speak("Thưa sếp tôi không có thông tin")
            continue
# Gọi trực tiếp hàm hydro mà không cần dùng phân luồng
hydro()
