from .library import fuzz, ctrl, np, wikipedia, MongoClient, certifi, mqtt
from .speak_hear import speak, hear


# Kết nối tới MongoDB Atlas
server = 'mongodb+srv://ducanhnguyenxuan51:ducanhnguyenxuan51@dataenviromentairc.ux7gs.mongodb.net/?retryWrites=true&w=majority&appName=DataEnviromentAIRC'
client = MongoClient(server, tlsCAFile=certifi.where())
db = client['DataEnviroment']
collection = db['AIRC']

# Hàm lấy dữ liệu nhiệt độ và độ ẩm từ MongoDB
def get_latest_data():
    latest_record = collection.find_one({}, {"temp": 1, "humi": 1, "_id": 0}, sort=[("date", -1), ("time", -1)])
    if latest_record:
        temperature = latest_record.get('temp')
        humidity = latest_record.get('humi')
        return temperature, humidity
    return None, None
         

f = open("database/question.txt", mode="r", encoding="utf8")
ques = f.read().split("\n")
def handle_data(text):
    # Chia thành các từ
    text = text.split(" ")
    # khởi tạo list rỗng để lưu tỉ lệ % giốn nhau giữa câu hỏi người dùng và data question
    ans = []
    # Tính toán tỷ lệ cho từng câu hỏi
    for s in ques :
        count = 0
        # Tính số từ trùng lặp
        for i in text:
            if i in s:
                # Cứ mỗi lần trùng lặp thì + 1
                count +=1
        # Chia số từ trùng lặp cho độ dài câu hỏi để lấy tỷ lệ trùng lặp
        ratio = count * 100 / len(s)
        # Gán tỷ lệ vào list
        ans.append(ratio)
    # Trả về thứ tự câu hỏi cao -> thấp
    return np.argmax(ans)
f = open("database/answer.txt", mode="r", encoding="utf8")
answer = f.read().split("\n")

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


# Hàm callback khi kết nối MQTT
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

# Hàm callback khi nhận thông điệp từ broker
def on_message(client, userdata, msg):
    global num_people
    message = msg.payload.decode()
    num_people = int(message)
# Thiết lập MQTT
broker = "broker.emqx.io"
port = 1883
mqtt_client = mqtt.Client()

# Kết nối MQTT
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(broker, port, 60)
mqtt_client.subscribe("/AIRC/OranPi/")
mqtt_client.loop_start()



# def vofancontrol(temp_input, humidity_input, num_people_input):
#     # Khai báo các biến đầu vào và đầu ra
#     temperature = ctrl.Antecedent(np.arange(0, 51, 1), 'temperature')  # Nhiệt độ từ 0 đến 50
#     humidity = ctrl.Antecedent(np.arange(0, 101, 1), 'humidity')  # Độ ẩm từ 0 đến 100
#     num_people = ctrl.Antecedent(np.arange(0, 16, 1), 'num_people')  # Số người từ 0 đến 30

#     # Consequents
#     fan_speed = ctrl.Consequent(np.arange(0, 4, 1), 'fan_speed')  # 0: off, 1: level 1, 2: level 2, 3: level 3

#     # Khai báo các hàm mờ cho nhiệt độ
#     temperature['cold'] = fuzz.trimf(temperature.universe, [0, 0, 15])
#     temperature['cool'] = fuzz.trimf(temperature.universe, [12, 18, 20])
#     temperature['normal'] = fuzz.trimf(temperature.universe, [18, 25, 27])
#     temperature['warm'] = fuzz.trimf(temperature.universe, [25, 35, 38])
#     temperature['hot'] = fuzz.trimf(temperature.universe, [35, 50, 50])

#     # Khai báo các hàm mờ cho độ ẩm
#     humidity['low'] = fuzz.trimf(humidity.universe, [0, 0, 45])
#     humidity['normal'] = fuzz.trimf(humidity.universe, [40, 50, 75])
#     humidity['high'] = fuzz.trimf(humidity.universe, [70, 100, 100])

#     # Membership functions for number of people
#     num_people['few'] = fuzz.trimf(num_people.universe, [0, 0, 6])
#     num_people['many'] = fuzz.trimf(num_people.universe, [5, 15, 15])
#     # num_people['few'] = fuzz.trimf(num_people.universe, [1, 1, 15])  # 1 to 15
#     # num_people['many'] = fuzz.trimf(num_people.universe, [16, 30, 30])  # 16 to 30 

#     fan_speed['off'] = fuzz.trapmf(fan_speed.universe, [0, 0, 0, 1])
#     fan_speed['level1'] = fuzz.trapmf(fan_speed.universe, [0, 1, 1, 2])
#     fan_speed['level2'] = fuzz.trapmf(fan_speed.universe, [1, 2, 2, 3])
#     fan_speed['level3'] = fuzz.trapmf(fan_speed.universe, [2, 3, 3, 3])

#     # Rules
#     rules = []
#     rules.append(ctrl.Rule(temperature['cold'] & humidity['high'] & num_people['few'], fan_speed['off']))
#     rules.append(ctrl.Rule(temperature['cold'] & humidity['normal'] & num_people['few'], fan_speed['level1']))
#     rules.append(ctrl.Rule(temperature['cold'] & humidity['low'] & num_people['few'], fan_speed['level2']))

#     rules.append(ctrl.Rule(temperature['cool'] & humidity['high'] & num_people['few'], fan_speed['level1']))
#     rules.append(ctrl.Rule(temperature['cool'] & humidity['normal'] & num_people['few'], fan_speed['level2']))
#     rules.append(ctrl.Rule(temperature['cool'] & humidity['low'] & num_people['few'], fan_speed['level3']))

#     rules.append(ctrl.Rule(temperature['normal'] & humidity['high'] & num_people['few'], fan_speed['level2']))
#     rules.append(ctrl.Rule(temperature['normal'] & humidity['normal'] & num_people['few'], fan_speed['level3']))
#     rules.append(ctrl.Rule(temperature['normal'] & humidity['low'] & num_people['few'], fan_speed['level3']))

#     rules.append(ctrl.Rule(temperature['warm'] & humidity['high'] & num_people['few'], fan_speed['level3']))
#     rules.append(ctrl.Rule(temperature['warm'] & humidity['normal'] & num_people['few'], fan_speed['level3']))
#     rules.append(ctrl.Rule(temperature['warm'] & humidity['low'] & num_people['few'], fan_speed['level3']))

#     rules.append(ctrl.Rule(temperature['hot'] & humidity['high'] & num_people['few'], fan_speed['level3']))
#     rules.append(ctrl.Rule(temperature['hot'] & humidity['normal'] & num_people['few'], fan_speed['level3']))
#     rules.append(ctrl.Rule(temperature['hot'] & humidity['low'] & num_people['few'], fan_speed['level3']))

#     # Quy tắc cho số người từ 16 đến 30
#     rules.append(ctrl.Rule(temperature['cold'] & humidity['high'] & num_people['many'], fan_speed['level1']))
#     rules.append(ctrl.Rule(temperature['cold'] & humidity['normal'] & num_people['many'], fan_speed['level2']))
#     rules.append(ctrl.Rule(temperature['cold'] & humidity['low'] & num_people['many'], fan_speed['level3']))

#     rules.append(ctrl.Rule(temperature['cool'] & humidity['high'] & num_people['many'], fan_speed['level2']))
#     rules.append(ctrl.Rule(temperature['cool'] & humidity['normal'] & num_people['many'], fan_speed['level3']))
#     rules.append(ctrl.Rule(temperature['cool'] & humidity['low'] & num_people['many'], fan_speed['level3']))

#     rules.append(ctrl.Rule(temperature['normal'] & humidity['high'] & num_people['many'], fan_speed['level3']))
#     rules.append(ctrl.Rule(temperature['normal'] & humidity['normal'] & num_people['many'], fan_speed['level3']))
#     rules.append(ctrl.Rule(temperature['normal'] & humidity['low'] & num_people['many'], fan_speed['level3']))

#     rules.append(ctrl.Rule(temperature['warm'] & humidity['high'] & num_people['many'], fan_speed['level3']))
#     rules.append(ctrl.Rule(temperature['warm'] & humidity['normal'] & num_people['many'], fan_speed['level3']))
#     rules.append(ctrl.Rule(temperature['warm'] & humidity['low'] & num_people['many'], fan_speed['level3']))

#     rules.append(ctrl.Rule(temperature['hot'] & humidity['high'] & num_people['many'], fan_speed['level3']))
#     rules.append(ctrl.Rule(temperature['hot'] & humidity['normal'] & num_people['many'], fan_speed['level3']))
#     rules.append(ctrl.Rule(temperature['hot'] & humidity['low'] & num_people['many'], fan_speed['level3']))

#     # (Thêm các quy tắc khác tương tự...)

#     # Control System Creation and Simulation
#     fan_control_system = ctrl.ControlSystem(rules)
#     fan_simulation = ctrl.ControlSystemSimulation(fan_control_system)

#     # Input the values into the simulation
#     fan_simulation.input['temperature'] = temp_input
#     fan_simulation.input['humidity'] = humidity_input
#     fan_simulation.input['num_people'] = num_people_input

#     # Compute the output
#     fan_simulation.compute()
#     print(f"Fan speed value: {fan_simulation.output['fan_speed']}")

#     # Return the fan speed level
#     if fan_simulation.output['fan_speed'] < 0.5:
#         fan_status = 'off'
#     elif 0.5 <= fan_simulation.output['fan_speed']< 1.5:
#         fan_status = '25'
#     elif 1.5 <= fan_simulation.output['fan_speed'] < 2.5:
#         fan_status = '50'
#     else:
#         fan_status = '75'

#     return fan_status
#     print('Fan speed level: ', fan_status)
# Hàm điều khiển tự động dựa trên luật mờ
# def auto_control():
#     global auto_control_enabled

#     while True:
#         try:
#             if auto_control_enabled:
#                 # Lấy dữ liệu từ MongoDB hoặc cảm biến
#                 temperature, humidity = get_latest_data()

#                 if temperature is not None and humidity is not None and num_people is not None:
#                     with lock:  # Đảm bảo các thao tác bên trong được đồng bộ hóa
#                         # Gọi hàm vofancontrol
#                         fan_status = vofancontrol(temperature, humidity, num_people)
#                         print(f"Quyết định tự động: {fan_status}")

#                         # Gửi qua MQTT  
#                         mqtt_client.publish("/AIRC/Fan1/", fan_status)

#                         # Phản hồi qua giọng nói (tùy chọn)
#                         if fan_status != 'off':
#                             speak(f"Tôi đã bật quạt ở mức {fan_status}%")
#                         else:
#                             speak("Tôi đã tắt quạt")

#                 # Kiểm tra điều kiện để tự động dừng nếu cần
#                 if not auto_control_enabled:
#                     auto_control_enabled = False
#                     print("Auto_control tạm dừng do người dùng ra lệnh.")
#             else:
#                 # Chờ cho đến khi num_people = 0 để khởi động lại auto_control
#                 if num_people == 0:
#                     auto_control_enabled = True
#                     print("Số người = 0. Auto_control được khởi động lại.")
#             sleep(60)  # Chu kỳ kiểm tra
#         except Exception as e:
#             print(f"Lỗi trong quá trình tự động kiểm tra: {e}")
#             sleep(60)


