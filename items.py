import random

class Items:
    def __init__(self, title: str, type: str, symbol: str):
        self.title = title
        self.type = type
        self.symbol = symbol
    
    def _break_and_remove(self, inventory, suppress_update=False):
        if inventory:
            print(f"DEBUG: Attempting to remove {self.title} from inventory: {inventory.items}")
            removed = False
            for slot in list(inventory.items.keys()):
                if inventory.items[slot] == self:
                    del inventory.items[slot]
                    removed = True
                    print(f"DEBUG: Removed {self.title} from slot {slot}")
            if removed and inventory.game and not suppress_update:
                inventory.game._update_interface()
                inventory.active_slot = inventory.active_slot
            print(f"DEBUG: Removal of {self.title} successful: {removed}")
            return removed
        print(f"DEBUG: No inventory provided for {self.title}")
        return False

class Weapon(Items):
    def __init__(self, title: str, type: str, symbol: str, damage: int):
        super().__init__(title, type, symbol)
        self.damage = damage
        
    def use(self, inventory) -> int:
        return self.damage

class Sword(Weapon):
    def __init__(self, title: str, damage: int, symbol: str):
        super().__init__(title, "melee", symbol, damage)
        self.double_strike_chance = 0.2  # 20% шанс на двойной удар
        
    def use(self, inventory) -> int:
        if random.random() < self.double_strike_chance:
            return self.damage * 2  # Двойной удар
        return self.damage

class Bow(Weapon):
    def __init__(self, title: str, damage: int, symbol: str):
        super().__init__(title, "ranged", symbol, damage)
        self.critical_shot_chance = 0.25  # 25% шанс на точный выстрел
        
    def use(self, inventory) -> int:
        if random.random() < self.critical_shot_chance:
            return int(self.damage * 1.5)  # Точный выстрел
        return self.damage
    
class IceStaff(Weapon):
    def __init__(self, title: str, damage: int, symbol: str):
        super().__init__(title, "magic", symbol, damage)
        self.freeze_chance = 0.15  # 15% шанс на заморозку
        self.freeze_duration = 3  # Заморозка на 3 хода
    
    def use(self, inventory) -> tuple:
        if random.random() < self.freeze_chance:
            return (self.damage, self.freeze_duration)  # Урон и заморозка
        return (self.damage, 0)  # Только урон

class HealthPotion(Items):
    def __init__(self, title: str, heal_amount: int, symbol: str):
        super().__init__(title, "heal_potion", symbol)
        self.heal_amount = heal_amount

    def use(self, target, inventory) -> int:
        heal = self.heal_amount
        target.current_health = min(target.max_health, target.current_health + heal)
        return heal

class PoisonPotion(Items):
    def __init__(self, title: str, damage_per_turn: int, symbol: str, duration: int = 3):
        super().__init__(title, "poison_potion", symbol)
        self.damage_per_turn = damage_per_turn
        self.duration = duration

    def use(self, target, inventory) -> tuple:
        # Возвращаем начальный урон и параметры для эффекта яда
        return (0, self.damage_per_turn, self.duration)  # Начальный урон 0, урон в ход, длительность