import random

class Inventory:
    def __init__(self, count_of_slots: int, items: dict = None):
        self.count_of_slots = count_of_slots
        self.items = items if items is not None else {}

    def add_item(self, item) -> bool:
        if len(self.items) < self.count_of_slots:
            slot = len(self.items) + 1
            self.items[slot] = item
            print(f"Предмет {item.title} добавлен в слот {slot}.")
            return True
        else:
            print("Инвентарь полон!")
            return False

class Items:
    def __init__(self, title: str, type: str, symbol: str):
        self.title = title
        self.type = type
        self.symbol = symbol
        
    def _break_and_remove(self, inventory: 'Inventory'):
        """Удаляет сломанный предмет из инвентаря"""
        if hasattr(self, 'durability') and self.durability <= 0 and inventory:
            for slot, item in list(inventory.items.items()):
                if item == self:
                    del inventory.items[slot]
                    print(f"{self.title} сломался и был удалён из инвентаря!")
                    return True
        return False

class Weapon(Items):
    def __init__(self, title: str, type: str, symbol: str, damage: int, durability: int):
        super().__init__(title, type, symbol)
        self.damage = damage
        self.durability = durability
        self.max_durability = durability
        
    def use(self, inventory: 'Inventory' = None) -> int:
        if self.durability > 0:
            self.durability -= 1
            self._break_and_remove(inventory)
            return self.damage
        return 0

class Sword(Weapon):
    def __init__(self, title: str, damage: int, symbol: str, durability: int = 70):
        super().__init__(title, "melee", symbol, damage, durability)
        self.combo_counter = 0
        
    def use(self, inventory: 'Inventory' = None) -> int:
        damage = super().use(inventory)
        self.combo_counter += 1
        if self.combo_counter % 3 == 0:
            print(f"⚔️ Комбо-удар! Урон x2")
            return damage * 2
        return damage

class Bow(Weapon):
    def __init__(self, title: str, damage: int, symbol: str, range: int = 5, durability: int = 30):
        super().__init__(title, "ranged", symbol, damage, durability)
        self.range = range
        
    def use(self, inventory: 'Inventory' = None) -> int:
        damage = super().use(inventory)
        if random.random() < 0.25:
            print(f"🎯 Критический выстрел! Урон x1.5")
            return int(damage * 1.5)
        return damage

class IceStaff(Weapon):
    def __init__(self, title: str, damage: int, symbol: str, range: int = 3, durability: int = 50):
        super().__init__(title, "magic", symbol, damage, durability)
        self.combo_counter = 0
        self.range = range
    
    def use(self, inventory: 'Inventory' = None) -> int:
        damage = super().use(inventory)
        self.combo_counter += 1
        if self.combo_counter % 3 == 0:
            print(f"❄️ Ледяной выстрел! Урон x3")
            return damage * 3
        return damage

class Shield(Items):
    def __init__(self, title: str, save_from_damage: int, symbol: str, durability: int = 20):
        super().__init__(title, "armor", symbol)
        self.save_from_damage = save_from_damage
        self.durability = durability
        self.max_durability = durability
        
    def block(self, damage: int, inventory: 'Inventory' = None) -> int:
        if self.durability <= 0:
            return damage
        blocked = min(damage, self.save_from_damage)
        self.durability -= 1
        self._break_and_remove(inventory)
        return damage - blocked

class HealthPotion(Items):
    def __init__(self, title: str, heal_amount: int, symbol: str, durability: int = 1):
        super().__init__(title, "heal_potion", symbol)
        self.heal_amount = heal_amount
        self.durability = durability
        self.max_durability = durability

    def use(self, target, inventory: 'Inventory' = None) -> int:
        if self.durability <= 0:
            return 0
            
        heal = self.heal_amount
        self.durability -= 1
        target.current_health = min(target.max_health, target.current_health + heal)
        print(f"Герой восстановил {heal} HP!")
        
        self._break_and_remove(inventory)
        return heal

class PoisonPotion(Items):
    def __init__(self, title: str, damage_per_turn: int, symbol: str, duration: int, durability: int = 1):
        super().__init__(title, "poison_potion", symbol)
        self.damage_per_turn = damage_per_turn
        self.duration = duration
        self.durability = durability
        self.max_durability = durability

    def use(self, target, inventory: 'Inventory' = None) -> int:
        if self.durability <= 0:
            return 0
            
        self.durability -= 1
        total_damage = self.damage_per_turn * self.duration
        target.current_health -= total_damage
        print(f"Враг получил {total_damage} урона от яда!")
        
        self._break_and_remove(inventory)
        return total_damage