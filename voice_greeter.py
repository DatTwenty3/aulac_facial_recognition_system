import os
from gtts import gTTS
import pygame
from datetime import datetime, date
import json

class VoiceGreeter:
    def __init__(self):
        self.greetings_dir = "greetings"
        self.greeted_today = {}
        self.current_date = date.today()
        self._init_pygame()
        self._load_greeted_today()
        
    def _init_pygame(self):
        pygame.mixer.init()
        
    def _load_greeted_today(self):
        """Load danh sách người đã được chào trong ngày"""
        greeted_file = os.path.join(self.greetings_dir, "greeted_today.json")
        if os.path.exists(greeted_file):
            with open(greeted_file, 'r') as f:
                data = json.load(f)
                last_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
                if last_date == self.current_date:
                    self.greeted_today = data['greetings']
                else:
                    self.greeted_today = {}
    
    def _save_greeted_today(self):
        """Lưu danh sách người đã được chào trong ngày"""
        os.makedirs(self.greetings_dir, exist_ok=True)
        greeted_file = os.path.join(self.greetings_dir, "greeted_today.json")
        with open(greeted_file, 'w') as f:
            json.dump({
                'date': self.current_date.strftime('%Y-%m-%d'),
                'greetings': self.greeted_today
            }, f, indent=2)
    
    def create_greeting(self, name):
        """Tạo file âm thanh chào mừng cho người mới"""
        os.makedirs(self.greetings_dir, exist_ok=True)
        greeting_file = os.path.join(self.greetings_dir, f"{name}.mp3")
        
        if not os.path.exists(greeting_file):
            tts = gTTS(text=f"Xin chào {name}, chào mừng bạn đến với công ty tư vấn và thiết kế Âu Lạc, chúc bạn có 1 ngày tốt lành!", lang='vi')
            tts.save(greeting_file)
    
    def greet(self, name):
        """Phát âm thanh chào mừng nếu chưa chào trong ngày"""
        # Kiểm tra và reset danh sách nếu sang ngày mới
        if date.today() != self.current_date:
            self.current_date = date.today()
            self.greeted_today = {}
            self._save_greeted_today()
        
        # Nếu chưa chào trong ngày
        if name not in self.greeted_today:
            greeting_file = os.path.join(self.greetings_dir, f"{name}.mp3")
            
            # Tạo file âm thanh nếu chưa có
            if not os.path.exists(greeting_file):
                self.create_greeting(name)
            
            # Phát âm thanh
            pygame.mixer.music.load(greeting_file)
            pygame.mixer.music.play()
            
            # Đợi cho đến khi phát xong
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            
            # Thêm vào danh sách đã chào với thời gian hiện tại
            current_time = datetime.now().strftime('%H:%M:%S')
            self.greeted_today[name] = current_time
            self._save_greeted_today() 