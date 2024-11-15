import numpy as np

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