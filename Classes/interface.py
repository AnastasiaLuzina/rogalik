from map import MAP_WIDTH, MAP_HEIGHT
import re
import curses

PANEL_WIDTH = 30
HEALTH_HEIGHT = 7
INTERACTION_HEIGHT = MAP_HEIGHT - HEALTH_HEIGHT - 1

class HealthPanel:
    def __init__(self, x: int, y: int, width: int, height: int, 
                 current_hp: int, max_hp: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.current_hp = current_hp
        self.max_hp = max_hp

    def render(self, screen):
        # Отрисовка рамки
        screen.addstr(self.y, self.x, '╔' + '═'*(self.width-2) + '╗')
        for dy in range(1, self.height-1):
            screen.addstr(self.y + dy, self.x, '║' + ' '*(self.width-2) + '║')
        screen.addstr(self.y + self.height - 1, self.x, '╚' + '═'*(self.width-2) + '╝')
        
        # Текст здоровья
        current_hp = max(0, min(self.current_hp, self.max_hp))  # Ограничиваем значение
        hp_text = f"HP: {current_hp}/{self.max_hp}"
        hp_percent = current_hp / self.max_hp
        bar_width = self.width - 4
        filled = int(bar_width * hp_percent)
        health_bar = '█'*filled + '░'*(bar_width-filled)
        
        # Центрируем текст и прогресс-бар
        screen.addstr(self.y + 1, self.x + 1, hp_text.center(self.width-2))
        screen.addstr(self.y + 2, self.x + 1, health_bar, curses.color_pair(3))

class InteractionPanel:
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.messages = []

    def add_message(self, message: str):
        max_length = self.width - 2
        if len(message) > max_length:
            message = message[:max_length-3] + '...'
        self.messages.append(message)
        if len(self.messages) > self.height - 2:
            self.messages.pop(0)

    def show_inventory(self, items: list, selected: int):
        self.messages = []
        for i, item in enumerate(items):
            button = f"[{i+1}] {item.title}"
            if i == selected:
                button = f"> {button}"
            else:
                button = f"  {button}"
            self.add_message(button)
        self.add_message("")
        self.add_message("↑/↓ - выбрать, Enter - подтвердить")

    def render(self, screen):
        screen.addstr(self.y, self.x, '╔' + '═'*(self.width-2) + '╗')
        for dy in range(1, self.height-1):
            screen.addstr(self.y + dy, self.x, '║' + ' '*(self.width-2) + '║')
        screen.addstr(self.y + self.height - 1, self.x, '╚' + '═'*(self.width-2) + '╝')
        
        for i, msg in enumerate(self.messages):
            screen.addstr(self.y + 1 + i, self.x + 1, msg[:self.width-2])