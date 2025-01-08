from mypackage.library import *
from mypackage.myfunction import *
from mypackage.speak_hear import *
from mypackage.control import *

# Biến trạng thái toàn cục để điều khiển auto_control
auto_control_enabled = True  # Ban đầu cho phép auto_control
# Khai báo Lock
lock = threading.Lock()
# Biến toàn cục lưu số lượng người
num_people = 0


def hydro():
    global auto_control_enabled
    while True:
        try:
            # Đọc câu hỏi và câu trả lời từ tệp
            # with open("database/question.txt", mode="r", encoding="utf8") as f:
            #     questions = f.readlines()
            
            with open("database/answer.txt", mode="r", encoding="utf8") as f:
                answers = f.readlines()
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
                    elif "quạt" in you:
                        auto_control_enabled = False
                        control_fan(you)
                    elif "đèn" in you:
                        control_light(you)
                    elif "tìm kiếm" in you or "wikipedia" in you:
                        query = you.replace("tìm kiếm", "").replace("wikipedia", "").strip()
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
                            speak("Dạ sếp nói lại đi em không hiểu")

                    # Sau mỗi câu trả lời, quay lại trạng thái chờ lệnh "xin chào"
                    break
        except Exception as e:
            speak("Tôi gặp lỗi, sếp thử lại nhé!")


# Bắt đầu giao tiếp với người dùng
hydro()

