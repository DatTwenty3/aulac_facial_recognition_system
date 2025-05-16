import pyttsx3
import threading
from queue import Queue
import time
from greeting_log import GreetingLog

class VoiceGreeter:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)  # Tốc độ nói
        self.engine.setProperty('volume', 1.0)  # Âm lượng
        
        # Lấy danh sách giọng nói có sẵn
        voices = self.engine.getProperty('voices')
        # Tìm giọng tiếng Việt nếu có
        vietnamese_voice = None
        for voice in voices:
            if 'vietnamese' in voice.name.lower():
                vietnamese_voice = voice
                break
        if vietnamese_voice:
            self.engine.setProperty('voice', vietnamese_voice.id)
        
        self.queue = Queue()
        self.is_speaking = False
        self.speaking_thread = threading.Thread(target=self._speaking_worker, daemon=True)
        self.speaking_thread.start()
        
        # Thêm GreetingLog để theo dõi người đã được chào trong ngày
        self.greeting_log = GreetingLog()
    
    def _speaking_worker(self):
        while True:
            if not self.queue.empty() and not self.is_speaking:
                self.is_speaking = True
                name = self.queue.get()
                self.engine.say(f"Hello {name}, Wellcome to Au Lac Construction, Good you have a nice day!")
                self.engine.runAndWait()
                self.is_speaking = False
            time.sleep(0.1)
    
    def greet(self, name):
        if name != "Unknown" and not self.greeting_log.is_greeted_today(name):
            self.queue.put(name)
            self.greeting_log.mark_as_greeted(name) 