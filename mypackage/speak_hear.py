from .library import pygame, sr, gTTS, os

def hear():
    print("Đang chờ: ...")
    r = sr.Recognizer()

    with sr.Microphone() as source:
        print("Tôi: ", end='')
        audio = r.listen(source, phrase_time_limit=5)
        try:
            text = r.recognize_google(audio, language="vi-VN")
            print(text)
            return str(text).lower()
        except sr.UnknownValueError:
            #print("Google Speech Recognition không thể nhận diện âm thanh.")
            return None
        except sr.RequestError as e:
            #print(f"Không thể kết nối tới Google Speech Recognition service; {e}")
            return None

def speak(text):
    print("Thư ký: " + text)
    tts = gTTS(text, lang='vi', slow=False)
    tts.save("sound.mp3")

    pygame.mixer.init()
    pygame.mixer.music.load("sound.mp3")
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

    pygame.mixer.music.stop()  # Dừng phát nhạc
    pygame.mixer.quit()        # Giải phóng mixer
    os.remove("sound.mp3")     # Xóa file

