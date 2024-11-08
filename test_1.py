import cv2
import threading
import numpy as np
import tensorflow as tf
import time

class VideoCaptureThread:
    def __init__(self, src=0):
        self.cap = cv2.VideoCapture(src)
        self.frame = None
        self.running = True
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
    previous_count = 0  # Biến để lưu số lượng người trước đó
    while True:
        frame = video_thread.get_frame()
        if frame is not None:
            # Thay đổi kích thước khung hình cho đầu vào mô hình
            resized_frame = cv2.resize(frame, (input_details[0]['shape'][2], input_details[0]['shape'][1]))

            # Chuẩn bị đầu vào cho mô hình
            input_data = np.expand_dims(resized_frame, axis=0).astype(np.uint8)

            # Đưa khung hình vào mô hình để nhận diện
            interpreter.set_tensor(input_details[0]['index'], input_data)
            interpreter.invoke()

            # Lấy kết quả từ mô hình
            boxes = interpreter.get_tensor(output_details[0]['index'])[0]
            classes = interpreter.get_tensor(output_details[1]['index'])[0]
            scores = interpreter.get_tensor(output_details[2]['index'])[0]

            # Khởi tạo biến đếm số người
            person_count = 0

            # Duyệt qua các kết quả và tìm nhãn "person" (người)
            for i in range(len(scores)):
                if scores[i] > 0.5:  # Chỉ xử lý nếu độ chính xác > 0.3
                    class_id = int(classes[i])
                    if labels[class_id] == "person":
                        person_count += 1  # Tăng biến đếm nếu phát hiện người

            # Ghi lại số người phát hiện
            if person_count != previous_count:
                print(f"Có {person_count} người trong khung hình!")
                # Gửi thông báo hoặc thực hiện hành động cần thiết
                # Ví dụ: gửi thông báo tới một hệ thống hoặc ghi lại vào file

                previous_count = person_count  # Cập nhật số lượng trước đó

            # Cập nhật số lượng người phát hiện vào biến toàn cục để hiển thị
            video_thread.current_person_count = person_count

        time.sleep(0.1)  # Tạm dừng một chút trước khi tiếp tục nhận diện

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

    video_thread.stop()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
