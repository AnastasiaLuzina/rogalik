from colorama import Fore, Back, Style
from map import MAP_WIDTH, MAP_HEIGHT
import re
import curses

PANEL_WIDTH = 35
HEALTH_HEIGHT = 7
INTERACTION_HEIGHT = MAP_HEIGHT - HEALTH_HEIGHT - 1

class HealthPanel:
    def __init__(self, x: int, y: int, width: int, height: int, 
                 current_hp: int, max_hp: int, game=None, killed_enemies: int = 0, total_enemies: int = 0):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.current_hp = current_hp
        self.max_hp = max_hp
        self.game = game
        self.killed_enemies = killed_enemies 
        self.total_enemies = total_enemies 


    def render(self, screen):
        try:
            screen.addstr(self.y, self.x, '╔' + '═'*(self.width-2) + '╗')
            for dy in range(1, self.height-1):
                screen.addstr(self.y + dy, self.x, '║' + ' '*(self.width-2) + '║')
            screen.addstr(self.y + self.height - 1, self.x, '╚' + '═'*(self.width-2) + '╝')
            
            current_hp = max(0, min(self.current_hp, self.max_hp))
            hp_text = f"HP: {current_hp}/{self.max_hp}"
            hp_percent = current_hp / self.max_hp
            bar_width = self.width - 3
            filled = int(bar_width * hp_percent)
            health_bar = '█'*filled + '░'*(bar_width-filled)
            
            screen.addstr(self.y + 1, self.x + 1, hp_text.center(self.width-2))
            screen.addstr(self.y + 2, self.x + 1, health_bar, curses.color_pair(3))
            
            enemy_icon = "💀"
            enemy_count_text = f"{enemy_icon} {self.killed_enemies}/{self.total_enemies}"
            formatted_text = enemy_count_text.ljust(self.width-2)
            
            color_pair = 4 if (self.killed_enemies % 2 == 0) else 5
            screen.addstr(self.y + 4, self.x + 1, formatted_text, 
                        curses.color_pair(color_pair) | curses.A_BOLD)
            
            weapon_text = f"Оружие: {self.game.hero.inventory.equipped_weapon.title if self.game.hero.inventory.equipped_weapon else 'Без оружия'}"
            screen.addstr(self.y + 3, self.x + 1, weapon_text[:self.width-2], curses.color_pair(5))
        except curses.error:
            pass

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
    

    def show_inventory(self, items, active_slot, equipped_weapon=None):
        self.messages.clear()
        self.messages.append(("ИНВЕНТАРЬ (TAB - закрыть)", curses.color_pair(6)))
        
        for slot in range(1, 9):
            item = items.get(slot)
            color = curses.color_pair(6) if slot == active_slot else curses.color_pair(2)
            prefix = "> " if slot == active_slot else "  "
            equipped = " [Э]" if item and equipped_weapon == item else ""
            text = f"{prefix}Слот {slot}: {item.title + equipped if item else 'Пусто'}"
            self.messages.append((text, color))
        
       
        self.messages.append(("[E] Использовать  [R] Выбросить", curses.color_pair(5)))
       
        self.messages.append(("[U] Снять экипировку", curses.color_pair(5)))

    def show_pickup_button(self):
        if not self.messages or "[F] Подобрать" not in self.messages[0]:
            self.messages.insert(0, "[F] Подобрать")

    def hide_pickup_button(self):
        if self.messages and "[F] Подобрать" in self.messages[0]:
            self.messages.pop(0)
            
    def render(self, screen):
        try:
            screen.addstr(self.y, self.x, '╔' + '═'*(self.width-2) + '╗')
            for i in range(1, self.height-1):
                screen.addstr(self.y + i, self.x, '║' + ' '*(self.width-2) + '║')
            screen.addstr(self.y + self.height - 1, self.x, '╚' + '═'*(self.width-2) + '╝')
            
            for i, msg in enumerate(self.messages):
                if i >= self.height - 2:
                    break
                if isinstance(msg, tuple):
                    text, color = msg
                    screen.addstr(self.y + 1 + i, self.x + 1, text[:self.width-2], color)
                else:
                    screen.addstr(self.y + 1 + i, self.x + 1, msg[:self.width-2], curses.color_pair(5))
        except curses.error:
            pass