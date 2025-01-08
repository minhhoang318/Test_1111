from mypackage.library import *  # Thư viện của bạn
from mypackage.myfunction import *
from mypackage.speak_hear import *
import threading
from time import sleep


# Kết nối tới MongoDB Atlas
server = 'mongodb+srv://ducanhnguyenxuan51:ducanhnguyenxuan51@dataenviromentairc.ux7gs.mongodb.net/?retryWrites=true&w=majority&appName=DataEnviromentAIRC'
client = MongoClient(server, tlsCAFile=certifi.where())
db = client['DataEnviroment']
collection = db['AIRC']

# Thiết lập MQTT
broker = "broker.emqx.io"
port = 1883
mqtt_client = mqtt.Client()

# Biến toàn cục lưu số lượng người
num_people = 0

# Hàm callback khi kết nối MQTT
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
   

# Hàm callback khi nhận thông điệp từ broker
# Hàm callback khi nhận thông điệp từ broker
def on_message(client, userdata, msg):
    global num_people
    message = msg.payload.decode()
    num_people = int(message)


# Kết nối MQTT
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(broker, port, 60)
mqtt_client.subscribe("/AIRC/OranPi/")
mqtt_client.loop_start()

# Hàm lấy dữ liệu nhiệt độ và độ ẩm từ MongoDB
def get_latest_data():
    latest_record = collection.find_one({}, {"temp": 1, "humi": 1, "_id": 0}, sort=[("date", -1), ("time", -1)])
    if latest_record:
        temperature = latest_record.get('temp')
        humidity = latest_record.get('humi')
        return temperature, humidity
    return None, None

# Hàm tìm kiếm thông tin trên Wikipedia
wikipedia.set_lang("vi")
def wiki_search(text):
    try:
        infor = wikipedia.summary(text).split('\n')
        speak(infor[0].split(".")[0])
        for a in infor[1:]:
            speak("Sếp muốn nghe thêm không?")
            ans = hear()
            if "có" not in ans:
                break
            print(a)
        speak("Cảm ơn sếp")
    except:
        speak("Tôi không tìm được thông tin thưa sếp")

# Biến trạng thái toàn cục để điều khiển auto_control
auto_control_enabled = True  # Ban đầu cho phép auto_control

# Khai báo Lock
lock = threading.Lock()

# Hàm điều khiển tự động dựa trên luật mờ
def auto_control():
    global auto_control_enabled

    while True:
        try:
            if auto_control_enabled:
                # Lấy dữ liệu từ MongoDB hoặc cảm biến
                temperature, humidity = get_latest_data()

                if temperature is not None and humidity is not None and num_people is not None:
                    with lock:  # Đảm bảo các thao tác bên trong được đồng bộ hóa
                        # Gọi hàm vofancontrol
                        fan_status = vofancontrol(temperature, humidity, num_people)
                        print(f"Quyết định tự động: {fan_status}")

                        # Gửi qua MQTT  
                        mqtt_client.publish("/AIRC/Fan1/", fan_status)

                        # Phản hồi qua giọng nói (tùy chọn)
                        if fan_status != 'off':
                            speak(f"Tôi đã bật quạt ở mức {fan_status}%")
                        else:
                            speak("Tôi đã tắt quạt")

                # Kiểm tra điều kiện để tự động dừng nếu cần
                if not auto_control_enabled:
                    auto_control_enabled = False
                    print("Auto_control tạm dừng do người dùng ra lệnh.")
            else:
                # Chờ cho đến khi num_people = 0 để khởi động lại auto_control
                if num_people == 0:
                    auto_control_enabled = True
                    print("Số người = 0. Auto_control được khởi động lại.")
            sleep(60)  # Chu kỳ kiểm tra
        except Exception as e:
            print(f"Lỗi trong quá trình tự động kiểm tra: {e}")
            sleep(60)

# Hàm xử lý tương tác với người dùng
def hydro():
    global auto_control_enabled
    while True:
        try:
            while True:
                you = hear()
                with lock:
                    if you is None:
                        continue
                    elif "thư ký" in you.lower():
                        speak("Dạ")
                        break
            while True:
                you = hear()
                with lock:
                    if you is None:
                        speak("Tôi chưa nghe sếp nói gì, sếp nói lại đi")
                        continue
                    
                    elif "nhiệt độ" in you.lower():
                        temperature, _ = get_latest_data()
                        if temperature is not None:
                            temperature = int(temperature)
                            speak(f"Nhiệt độ hiện tại là {temperature} độ C")
                        else:
                            speak("Tôi không tìm thấy dữ liệu về nhiệt độ.")
                    
                    elif "độ ẩm" in you.lower():
                        _, humidity = get_latest_data()
                        if humidity is not None:
                            humidity = int(humidity)
                            speak(f"Độ ẩm hiện tại là {humidity} phần trăm")
                        else:
                            speak("Tôi không tìm thấy dữ liệu về độ ẩm.")

                    elif you is not None and "quạt" in you:
                        # Dừng auto_control khi người dùng ra lệnh
                        auto_control_enabled = False
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
                    
                    elif "tìm kiếm" in you or "wikipedia" in you:
                        query = you.replace("tìm kiếm", "").replace("wikipedia", "").strip()
                        wiki_search(query)
                    
                    elif "tạm biệt" in you.lower():
                        speak("Tạm biệt sếp")
                        return
                    break
        except Exception as e:
            speak("Tôi gặp lỗi, sếp thử lại nhé!")

# Khởi chạy luồng tự động
#auto_thread = threading.Thread(target=auto_control, daemon=True)
#auto_thread.start()

# Bắt đầu giao tiếp với người dùng
hydro()

