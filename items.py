import random

class Items:
    def __init__(self, title: str, type: str, symbol: str):
        self.title = title
        self.type = type
        self.symbol = symbol
    
    def _break_and_remove(self, inventory):
        """Удаляет сломанный предмет и обновляет интерфейс"""
        if inventory and getattr(self, 'durability', 1) <= 0:
            # Удаляем все копии предмета из инвентаря
            removed = False
            for slot in list(inventory.items.keys()):
                if inventory.items[slot] == self:
                    del inventory.items[slot]
                    removed = True
            
            if removed and inventory.game:
                # Обновляем интерфейс и корректируем активный слот
                inventory.game._update_interface()
                inventory.active_slot = inventory.active_slot  # Форсируем проверку слота
            return removed
        return False

class Weapon(Items):
    def __init__(self, title: str, type: str, symbol: str, damage: int):
        super().__init__(title, type, symbol)
        self.damage = damage
        
    def use(self, inventory) -> int:
        return self.damage  # Теперь оружие не ломается

class Sword(Weapon):
    def __init__(self, title: str, damage: int, symbol: str):
        super().__init__(title, "melee", symbol, damage)
        self.combo_counter = 0
        
    def use(self, inventory) -> int:
        self.combo_counter += 1
        if self.combo_counter % 3 == 0:
            return self.damage * 2
        return self.damage

class Bow(Weapon):
    def __init__(self, title: str, damage: int, symbol: str):
        super().__init__(title, "ranged", symbol, damage)
        
    def use(self, inventory) -> int:
        if random.random() < 0.25:
            return int(self.damage * 1.5)
        return self.damage
    
class IceStaff(Weapon):
    def __init__(self, title: str, damage: int, symbol: str):
        super().__init__(title, "magic", symbol, damage)
        self.combo_counter = 0
    
    def use(self, inventory) -> int:
        self.combo_counter += 1
        if self.combo_counter % 3 == 0:
            return self.damage * 3
        return self.damage

class HealthPotion(Items):
    def __init__(self, title: str, heal_amount: int, symbol: str):
        super().__init__(title, "heal_potion", symbol)
        self.heal_amount = heal_amount

    def use(self, target, inventory) -> int:
        heal = self.heal_amount
        target.current_health = min(target.max_health, target.current_health + heal)
        return heal

class PoisonPotion(Items):
    def __init__(self, title: str, damage_per_turn: int, symbol: str, duration: int):
        super().__init__(title, "poison_potion", symbol)
        self.damage_per_turn = damage_per_turn
        self.duration = duration

    def use(self, target, inventory) -> int:
        total_damage = self.damage_per_turn * self.duration
        target.current_health -= total_damage
        return total_damage