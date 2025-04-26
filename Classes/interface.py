from colorama import Fore, Back, Style 
from map import MAP_WIDTH, MAP_HEIGHT
import re
import curses

PANEL_WIDTH = 35
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
        bar_width = self.width - 3
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
        self.show_pickup = False

    def add_message(self, message: str):
        max_length = self.width - 2
        if len(message) > max_length:
            message = message[:max_length-3] + '...'
        self.messages.append(message)
        if len(self.messages) > self.height - 2:
            self.messages.pop(0)

    def show_inventory(self, items, active_slot):
        self.messages.clear()
        # Заголовок желтым (пара 6)
        self.messages.append(("ИНВЕНТАРЬ (TAB для закрытия)", curses.color_pair(6)))  
        
        # Слоты
        for slot in sorted(items.keys()):
            item = items.get(slot)
            if item:
                # Активный слот: желтый (пара 6), остальные: белый (пара 2)
                color = curses.color_pair(6) if slot == active_slot else curses.color_pair(2)
                self.messages.append((f"Слот {slot}: {item.title}", color))

    def show_pickup_button(self, count):
        """Показывает кнопку подбора"""
        self.messages = [f"[F] Подобрать ({count} предметов)"]

    def hide_pickup_button(self):
        """Скрывает кнопку подбора"""
        if self.messages and "[F] Подобрать" in self.messages[0]:
            self.messages.clear()
            
    def render(self, screen):
        # Отрисовка рамки
        screen.addstr(self.y, self.x, '╔' + '═'*(self.width-2) + '╗')
        for i in range(1, self.height-1):
            screen.addstr(self.y + i, self.x, '║' + ' '*(self.width-2) + '║')
        screen.addstr(self.y + self.height - 1, self.x, '╚' + '═'*(self.width-2) + '╝')
        
        # Отрисовка сообщений с учётом цветов
        for i, msg in enumerate(self.messages):
            if isinstance(msg, tuple):  # Если сообщение содержит цвет
                text, color = msg
                screen.addstr(self.y + 1 + i, self.x + 1, text[:self.width-2], color)
            else:
                screen.addstr(self.y + 1 + i, self.x + 1, msg[:self.width-2])