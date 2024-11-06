import cv2
import numpy as np
import tensorflow as tf

# Đọc nhãn COCO từ file
with open("assets/coco_labels.txt", "r") as f:
    labels = f.read().strip().split("\n")

# Tải mô hình TensorFlow Lite
interpreter = tf.lite.Interpreter(model_path="ssd_mobilenet_v2_coco_quant_postprocess.tflite")
interpreter.allocate_tensors()

# Lấy thông tin đầu vào và đầu ra của mô hình
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Kiểm tra loại dữ liệu và kích thước đầu vào của mô hình
input_dtype = input_details[0]['dtype']
input_shape = input_details[0]['shape']

# Khởi tạo webcam USB với độ phân giải cao hơn
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

while True:
    ret, frame = cap.read()
    if not ret:
        print("Không nhận được khung hình từ webcam.")
        break

    # Sao chép khung hình ban đầu để hiển thị kết quả
    display_frame = frame.copy()

    # Thay đổi kích thước khung hình cho đầu vào mô hình
    resized_frame = cv2.resize(frame, (input_shape[2], input_shape[1]))

    # Chuyển đổi kiểu dữ liệu đầu vào (UINT8 nếu mô hình yêu cầu)
    if input_dtype == np.uint8:
        input_data = np.expand_dims(resized_frame, axis=0).astype(np.uint8)
    else:
        input_data = np.expand_dims(resized_frame, axis=0).astype(np.float32) / 255.0

    # Đưa khung hình vào mô hình để nhận diện
    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()

    # Lấy kết quả từ mô hình
    boxes = interpreter.get_tensor(output_details[0]['index'])[0]  # Vị trí khung bao
    classes = interpreter.get_tensor(output_details[1]['index'])[0]  # Nhãn lớp
    scores = interpreter.get_tensor(output_details[2]['index'])[0]  # Độ chính xác

    # Khởi tạo biến đếm số người
    person_count = 0

    # Duyệt qua các kết quả và tìm nhãn "person" (người)
    for i in range(len(scores)):
        if scores[i] > 0.5:  # Chỉ xử lý nếu độ chính xác > 0.5
            class_id = int(classes[i])
            if labels[class_id] == "person":
                person_count += 1  # Tăng biến đếm nếu phát hiện người

                # Tính toán vị trí khung bao
                y_min, x_min, y_max, x_max = boxes[i]
                x_min = int(x_min * frame.shape[1])
                x_max = int(x_max * frame.shape[1])
                y_min = int(y_min * frame.shape[0])
                y_max = int(y_max * frame.shape[0])

                # Vẽ khung bao quanh đối tượng phát hiện trên khung hình ban đầu
                cv2.rectangle(display_frame, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
                cv2.putText(display_frame, f"Person: {scores[i]:.2f}", (x_min, y_min - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                cv2.putText(display_frame, f"phat hien {person_count} anh dep dai", (60, 400), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
    # Hiển thị số người đếm được trên khung hình
    cv2.putText(display_frame, f"Number of People: {person_count}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

    # Hiển thị khung hình với kết quả nhận diện
    cv2.imshow("Person Detection", display_frame)

    # Nhấn 'q' để thoát
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Giải phóng tài nguyên
cap.release()
cv2.destroyAllWindows()
