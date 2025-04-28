from colorama import Fore, Back, Style 
from map import MAP_WIDTH, MAP_HEIGHT
import re
import curses

PANEL_WIDTH = 35
HEALTH_HEIGHT = 7
INTERACTION_HEIGHT = MAP_HEIGHT - HEALTH_HEIGHT - 1

class HealthPanel:
    def __init__(self, x: int, y: int, width: int, height: int, 
                 current_hp: int, max_hp: int, 
                 killed_enemies: int = 0, total_enemies: int = 0):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.current_hp = current_hp
        self.max_hp = max_hp
        self.killed_enemies = killed_enemies  # Убитые враги
        self.total_enemies = total_enemies   # Общее количество врагов

    def render(self, screen):
        # Отрисовка рамки
        screen.addstr(self.y, self.x, '╔' + '═'*(self.width-2) + '╗')
        for dy in range(1, self.height-1):
            screen.addstr(self.y + dy, self.x, '║' + ' '*(self.width-2) + '║')
        screen.addstr(self.y + self.height - 1, self.x, '╚' + '═'*(self.width-2) + '╝')
        
        # Текст здоровья
        current_hp = max(0, min(self.current_hp, self.max_hp))
        hp_text = f"HP: {current_hp}/{self.max_hp}"
        hp_percent = current_hp / self.max_hp
        bar_width = self.width - 3
        filled = int(bar_width * hp_percent)
        health_bar = '█'*filled + '░'*(bar_width-filled)
        
        # Отображение здоровья
        screen.addstr(self.y + 1, self.x + 1, hp_text.center(self.width-2))
        screen.addstr(self.y + 2, self.x + 1, health_bar, curses.color_pair(3))
        
        # Новая визуализация счетчика убитых врагов
        enemy_icon = "💀"  # Символ черепа
        enemy_count_text = f"{enemy_icon} {self.killed_enemies}/{self.total_enemies}"  # Дробь
        formatted_text = enemy_count_text.ljust(self.width-2)
        
        # Анимация мигания при обновлении счетчика
        if self.killed_enemies > 0:
            color_pair = 4 if (self.killed_enemies % 2 == 0) else 5  # Чередуем цвета
        else:
            color_pair = 4
            
        screen.addstr(self.y + 4, self.x + 1, formatted_text, 
                     curses.color_pair(color_pair) | curses.A_BOLD)

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
        self.messages.append(("ИНВЕНТАРЬ (TAB - закрыть)", curses.color_pair(6)))
        
        # Слоты
        for slot in range(1, 9):
            item = items.get(slot)
            color = curses.color_pair(6) if slot == active_slot else curses.color_pair(2)
            prefix = "> " if slot == active_slot else "  "
            text = f"{prefix}Слот {slot}: {item.title if item else 'Пусто'}"
            self.messages.append((text, color))
        
        # Кнопки управления
        self.messages.append(("[E] Использовать  [R] Выбросить", curses.color_pair(5)))


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