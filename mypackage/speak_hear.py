from mypackage.library import*
from gtts import gTTS


def hear():
    print("Đang hóng: ...")
    r = sr.Recognizer()

    with sr.Microphone() as source:
        print("Tôi: ", end='')
        audio = r.listen(source, phrase_time_limit=3)
        try:
            text = r.recognize_google(audio, language="vi-VN")
            print(text)
            return str(text).lower()
        except sr.UnknownValueError:
            print("Google Speech Recognition không thể nhận diện âm thanh.")
            return None
        except sr.RequestError as e:
            print(f"Không thể kết nối tới Google Speech Recognition service; {e}")
            return None

import pygame

def speak(text):
    print("Bờ dô: " + text)
    tts = gTTS(text, lang='vi', slow=False)
    tts.save("sound.mp3")

    # Khởi tạo pygame mixer và phát âm thanh
    pygame.mixer.init()
    pygame.mixer.music.load("sound.mp3")
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():  # Đợi âm thanh kết thúc
        pygame.time.Clock().tick(10)

    os.remove("sound.mp3")

