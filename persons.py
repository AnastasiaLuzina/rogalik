from colorama import init, Back, Fore
import random
from inventory import Inventory
from items import Weapon

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
        self.game = game
        self.max_health = max_health
        self.current_health = max_health
        self.inventory = None

    def attack(self):
        if self.inventory.equipped_weapon:
            damage = self.inventory.equipped_weapon.use(self.inventory)
            # Убрали добавление в interaction_panel
            print(f"DEBUG: Hero attacked with {self.inventory.equipped_weapon.title}, damage: {damage}")
            return damage
        else:
            damage = 5
            # Убрали добавление в interaction_panel
            print("DEBUG: Hero attacked with fist, damage: 5")
            return damage

class Enemy(Person):
    def __init__(self, x: int, y: int, char: str, color: str, max_health: int, damage: int, title: str):
        super().__init__(x, y, char, color)
        self.max_health = max_health
        self.current_health = max_health
        self.damage = damage
        self.title = title
        print(f"DEBUG: Created enemy {title} at ({x}, {y}) with char {char}")

class Undead(Enemy):
    def __init__(self, x: int, y: int):
        super().__init__(x, y, '▣', Fore.RED, max_health=50, damage=8, title="Нежить")
        self.can_resurrect = True

    def resurrect(self):
        if self.can_resurrect and self.current_health <= 0:
            self.current_health = 20
            self.can_resurrect = False
            print(f"DEBUG: Нежить воскресла!")
            return True
        return False

class Ghost(Enemy):
    def __init__(self, x: int, y: int):
        super().__init__(x, y, '▣', Fore.RED, max_health=30, damage=5, title="Призрак")
        self.is_phased = True

class DarkMage(Enemy):
    def __init__(self, x: int, y: int):
        super().__init__(x, y, '▣', Fore.RED, max_health=40, damage=6, title="Темный маг")
        self.spell_cooldown = 0
        self.spell_damage = 15