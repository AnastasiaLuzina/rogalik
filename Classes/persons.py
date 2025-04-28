from colorama import init, Back, Fore
import random
from inventory import Inventory

init(autoreset=True)

class Person:
    def __init__(self, x: int, y: int, char: str, color: str):
        self.x = x
        self.y = y
        self.char = char
        self.color = color

class Hero(Person):
    def __init__(self, x: int, y: int, game, max_health: int = 100):
        super().__init__(x, y, '@', Fore.CYAN)
        self.game = game  # Сохраняем ссылку на игру
        self.max_health = max_health
        self.current_health = max_health
        self.inventory = None  # Будет установлено позже

    def pick_up_item(self, item):
        """Подобрать предмет в активный слот"""
        return self.inventory.add_to_active_slot(item)

    def drop_item(self):
        """Выбросить предмет из активного слота"""
        return self.inventory.remove_from_active_slot()

    def use_item(self, target=None):
        return self.inventory.use_active_item(target)

    def attack(self):
        active_item = self.inventory.get_active_item()
        if isinstance(active_item, Weapon):
            damage = active_item.use(self.inventory)
            print(f"Вы нанесли {damage} урона!")
            return damage
        print("Нет оружия в активном слоте!")
        return 0



class Enemy(Person):
    def __init__(self, x: int, y: int, char: str, color: str, max_health: int, damage: int):
        super().__init__(x, y, char, color)
        self.max_health = max_health
        self.current_health = max_health
        self.damage = damage

class Undead(Enemy):
    def __init__(self, x: int, y: int):
        super().__init__(x, y, '▣', Fore.RED, max_health=50, damage=8) 
        self.can_resurrect = True

    def resurrect(self):
        if self.can_resurrect and self.current_health <= 0:
            self.current_health = 20
            self.can_resurrect = False
            print(f"Нежить воскресла!")
            return True
        return False

class Ghost(Enemy):
    def __init__(self, x: int, y: int):
        super().__init__(x, y, '▣', Fore.RED, max_health=30, damage=5)  
        self.is_phased = True

class DarkMage(Enemy):
    def __init__(self, x: int, y: int):
        super().__init__(x, y, '▣', Fore.RED, max_health=40, damage=6)  
        self.spell_cooldown = 0
        self.spell_damage = 15