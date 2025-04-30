import random
from colorama import init, Fore

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
        base_damage = 5 
        freeze_duration = 0
        if self.inventory.equipped_weapon:
            result = self.inventory.equipped_weapon.use(self.inventory)
            if isinstance(result, tuple):  
                base_damage, freeze_duration = result
            else:
                base_damage = result
        
        min_dmg = max(1, int(base_damage * 0.7))
        max_dmg = int(base_damage * 1.3)
        damage = random.randint(min_dmg, max_dmg)
        
        return damage, freeze_duration

class Enemy(Person):
    def __init__(self, x: int, y: int, char: str, color: str, max_health: int, damage: int, title: str):
        super().__init__(x, y, char, color)
        self.max_health = max_health
        self.current_health = max_health
        self.damage = damage
        self.title = title

    def attack(self):
        min_dmg = max(1, int(self.damage * 0.7))
        max_dmg = int(self.damage * 1.3)
        damage = random.randint(min_dmg, max_dmg)
        return damage

class Undead(Enemy):
    def __init__(self, x: int, y: int):
        super().__init__(x, y, '▣', Fore.RED, max_health=50, damage=8, title="Нежить")
        self.can_resurrect = True

    def resurrect(self):
        if self.can_resurrect and self.current_health <= 0:
            self.current_health = 20
            self.can_resurrect = False
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