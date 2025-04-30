import random

class Items:
    def __init__(self, title: str, type: str, symbol: str):
        self.title = title
        self.type = type
        self.symbol = symbol
    
    def _break_and_remove(self, inventory, suppress_update=False):
        if inventory:
            removed = False
            for slot in list(inventory.items.keys()):
                if inventory.items[slot] == self:
                    del inventory.items[slot]
                    removed = True
            if removed and inventory.game and not suppress_update:
                inventory.game.updater._update_interface() 
                inventory.active_slot = inventory.active_slot
            return removed
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
        self.double_strike_chance = 0.2 
        
    def use(self, inventory) -> int:
        if random.random() < self.double_strike_chance:
            return self.damage * 2 
        return self.damage

class Bow(Weapon):
    def __init__(self, title: str, damage: int, symbol: str):
        super().__init__(title, "ranged", symbol, damage)
        self.critical_shot_chance = 0.25
        
    def use(self, inventory) -> int:
        if random.random() < self.critical_shot_chance:
            return int(self.damage * 1.5) 
        return self.damage
    
class IceStaff(Weapon):
    def __init__(self, title: str, damage: int, symbol: str):
        super().__init__(title, "magic", symbol, damage)
        self.freeze_chance = 0.15 
        self.freeze_duration = 3 
    
    def use(self, inventory) -> tuple:
        if random.random() < self.freeze_chance:
            return (self.damage, self.freeze_duration)  
        return (self.damage, 0)

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
        return (0, self.damage_per_turn, self.duration)  