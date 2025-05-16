import json
import os
from datetime import datetime

class GreetingLog:
    def __init__(self):
        self.log_file = os.path.join('data', 'greeting_log.json')
        self.greeted_today = self._load_greeted_today()
    
    def _load_greeted_today(self):
        if os.path.exists(self.log_file):
            with open(self.log_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Kiểm tra xem log có phải của ngày hôm nay không
                if data.get('date') == datetime.now().strftime('%Y-%m-%d'):
                    return data.get('greetings', {})
        return {}
    
    def _save_greeted_today(self):
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump({
                'date': datetime.now().strftime('%Y-%m-%d'),
                'greetings': self.greeted_today
            }, f, ensure_ascii=False, indent=2)
    
    def is_greeted_today(self, name):
        return name in self.greeted_today
    
    def mark_as_greeted(self, name):
        current_time = datetime.now().strftime('%H:%M:%S')
        self.greeted_today[name] = current_time
        self._save_greeted_today() 