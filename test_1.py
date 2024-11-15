import cv2
import threading
import numpy as np
import tensorflow as tf
import time
import paho.mqtt.client as mqtt
from main import hydro



class VideoCaptureThread:
    def __init__(self, src=0):
        self.cap = cv2.VideoCapture(src)
        self.frame = None
        self.running = True
        self.detections = []  # Danh sách lưu trữ bounding boxes
        self.thread = threading.Thread(target=self.update, daemon=True)
        self.thread.start()

    def update(self):
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                self.frame = frame

    def get_frame(self):
        return self.frame

    def stop(self):
        self.running = False
        self.cap.release()

def detection_thread(video_thread, interpreter, input_details, output_details, labels):
    previous_count = 0
    stable_count = 0
    stable_timer = time.time()
    debounce_time = 2

    while video_thread.running:
        frame = video_thread.get_frame()
        if frame is not None:
            resized_frame = cv2.resize(frame, (input_details[0]['shape'][2], input_details[0]['shape'][1]))
            input_data = np.expand_dims(resized_frame, axis=0).astype(np.uint8)

            interpreter.set_tensor(input_details[0]['index'], input_data)
            interpreter.invoke()

            boxes = interpreter.get_tensor(output_details[0]['index'])[0]
            classes = interpreter.get_tensor(output_details[1]['index'])[0]
            scores = interpreter.get_tensor(output_details[2]['index'])[0]

            person_count = 0
            video_thread.detections.clear()

            for i in range(len(scores)):
                if scores[i] > 0.4:
                    class_id = int(classes[i])
                    if labels[class_id] == "person":
                        person_count += 1

            # Cập nhật số lượng người ngay lập tức để hiển thị
            video_thread.current_person_count = person_count

            # Chỉ gửi thông báo khi số lượng người thay đổi ổn định
            if person_count != stable_count:
                stable_count = person_count
                stable_timer = time.time()

            if (time.time() - stable_timer > debounce_time) and (stable_count != previous_count):
                mqtt_send_notification(stable_count)
                print(f"Có {stable_count} người trong khung hình! Gửi thông báo MQTT.")
                previous_count = stable_count

        time.sleep(0.1)

# Luồng gửi thông báo qua MQTT
def mqtt_send_notification(person_count):
    broker = "broker.emqx.io"
    port = 1883
    topic = "/AIRC/Fan1/"
    
    # Tạo client MQTT và kết nối tới broker
    client = mqtt.Client()
    client.connect(broker, port, 60)

    # Gửi lệnh bật/tắt quạt dựa trên số lượng người
    if person_count > 0:
        client.publish(topic, "ON")
        print("Đã gửi lệnh: Bật quạt")
    else:
        client.publish(topic, "OFF")
        print("Đã gửi lệnh: Tắt quạt")

    client.disconnect()

def main():
    # Đọc nhãn COCO từ file
    with open("/media/pi/CENTOS-STRE/Detection_IoT/assets/coco_labels.txt", "r") as f:
        labels = f.read().strip().split("\n")

    # Tải mô hình TensorFlow Lite
    interpreter = tf.lite.Interpreter(model_path="ssd_mobilenet_v2_coco_quant_postprocess.tflite")
    interpreter.allocate_tensors()

    # Lấy thông tin đầu vào và đầu ra của mô hình
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    # Khởi tạo VideoCaptureThread
    video_thread = VideoCaptureThread()
    video_thread.current_person_count = 0  # Biến để lưu số lượng người phát hiện

    # Tạo luồng nhận diện
    detection_thread_instance = threading.Thread(target=detection_thread, args=(video_thread, interpreter, input_details, output_details, labels))
    detection_thread_instance.start()

    while True:
        frame = video_thread.get_frame()
        if frame is not None:
            # Vẽ các bounding box trên khung hình
            for (left, top, right, bottom) in video_thread.detections:
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)  # Màu xanh lá cây, độ dày 2

            # Tạo background cho số lượng người
            background_height = 50  # Chiều cao của background
            cv2.rectangle(frame, (0, 0), (400, background_height), (0, 0, 0), -1)  # Hình chữ nhật màu đen

            # Hiển thị số lượng người phát hiện
            cv2.putText(frame, f"Number of People: {video_thread.current_person_count}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

            # Hiển thị khung hình
            cv2.imshow("Video", frame)

        # Nhấn 'q' để thoát
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_thread.stop()  # Dừng luồng video
    detection_thread_instance.join()  # Đợi luồng nhận diện dừng lại
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

