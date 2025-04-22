import keyboard
import random
from threading import Thread
import time

class Position:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Person:
    def __init__(self, health, symbol, position=Position(0, 0)):
        self.health = health
        self.max_health = health
        self.position = position
        self.symbol = symbol    

class Hero(Person):
    def __init__(self, health, symbol, position, inventory_size=10):
        super().__init__(health, symbol, position)
        self.inventory = Inventory(inventory_size) # всегда создаём новый инвентарь
    
    """Проверка расстояния между героем и предметом"""
    def check_item_interaction(self, item_position):
        dx = abs(self.position.x - item_position.x)
        dy = abs(self.position.y - item_position.y)
        return dx <= 1 and dy <= 1

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

""" Класс врагов и Их виды (3) """

class Enemy(Person):
    def __init__(self, health, symbol, position, damage):
        super().__init__(health, symbol, position)
        self.damage = damage

# Нежить ( может возродиться до 1 раза)
class Undead(Enemy):
    def __init__(self, health, symbol, position, damage):
        super().__init__(health, symbol, position, damage)
        self.can_resurrect = True

    def resurrect(self):
        if self.can_resurrect:
            self.health = 1
            self.can_resurrect = False
            return True
        return False
    
# Призрак ( может проходить сквозь стены )
class Ghost(Enemy):
    def __init__(self, health, symbol, position, damage):
        super().__init__(health, symbol, position, damage)
        self.is_phased = True

# Тёмный маг ( раз в 3 хода кастует заклинание )
class DarkMage(Enemy):
    def __init__(self, health, symbol, position, damage):
        super().__init__(health, symbol, position, damage)
        self.spell_damage = damage * 2  # урон от заклинания (в 2 раза больше)
        self.spell_cooldown = 0

    def cast_spell(self):
        if self.spell_cooldown > 0:
            self.spell_cooldown -= 1
            return 0
        self.spell_cooldown = 3
        return self.spell_damage
    
""" Предметы, которые можно подбирать и Инвентарь для них """

class Inventory:
    def __init__(self, count_of_slots):
        self.count_of_slots = count_of_slots
        self.items = {}
        self.active_slot = 1
        self._running = False  # по умолчанию закрыт
        self._setup_keyboard()

    def _setup_keyboard(self):
        def listener():
            while True:
                if self._running:  # если инвентарь открыт
                    keyboard.on_press_key("left", lambda _: self._change_slot(-1), suppress=True)
                    keyboard.on_press_key("right", lambda _: self._change_slot(1), suppress=True)
                    keyboard.on_press_key("e", lambda _: self.use_active_item(), suppress=True)
                keyboard.wait("tab")  # ждём нажатия Tab
                self.toggle()  # открываем/закрываем инвентарь

        Thread(target=listener, daemon=True).start()

    def toggle(self):
        """Переключает состояние инвентаря (открыт/закрыт)"""
        self._running = not self._running
        status = "открыт" if self._running else "закрыт"
        print(f"\nИнвентарь {status}. Активный слот: {self.active_slot}")

    def _change_slot(self, direction):
        new_slot = self.active_slot + direction
        if 1 <= new_slot <= self.count_of_slots:
            self.active_slot = new_slot
            print(f"Активный слот изменён на слот номер {self.active_slot}")

    def add_to_active_slot(self, item):
        """Добавляет предмет в активный слот"""
        if self.active_slot in self.items:
            print(f"Слот номер {self.active_slot} уже занят!")
            return False
            
        self.items[self.active_slot] = item
        print(f"{item.title} добавлен в слот номер {self.active_slot}")
        return True

    def remove_from_active_slot(self):
        """Удаляет предмет из активного слота"""
        if self.active_slot not in self.items:
            print(f"Слот {self.active_slot} пуст!")
            return None
            
        item = self.items.pop(self.active_slot)
        print(f"{item.title} удалён из слота номер {self.active_slot}")
        return item
    
    def get_active_item(self):
        """Возвращает предмет из активного слота или None"""
        return self.items.get(self.active_slot)

    def use_active_item(self, target=None):
        """Использует предмет из активного слота"""
        item = self.get_active_item()
        
        if not item:
            print("Активный слот пуст!")
            return False
        
        if isinstance(item, Weapon):
            damage = item.use(self)
            print(f"Использовано оружие {item.title}! Урон: {damage}")
            return damage
            
        elif isinstance(item, HealthPotion):
            if not target:
                print("Не указана цель для зелья!")
                return False
            item.use(target, self)
            return True
            
        elif isinstance(item, Shield):
            print(f"Щит {item.title} активирован!")
            return True
            
        elif isinstance(item, PoisonPotion):
            if not target:
                print("Не указана цель для яда!")
                return False
            item.use(target, self)
            return True
            
        return False
    
class Items:
    def __init__(self, title, type, symbol):
        self.title = title
        self.type = type
        self.symbol = symbol
        
    def _break_and_remove(self, inventory):
        """Общий метод для удаления сломанного предмета из инвентаря"""
        if hasattr(self, 'durability') and self.durability <= 0 and inventory:
            for slot, item in inventory.items.items():
                if item == self:
                    del inventory.items[slot]
                    print(f"{self.title} сломался и был удалён из инвентаря!")
                    return True
        return False

class Weapon(Items):
    def __init__(self, title, type, symbol, damage, durability):
        super().__init__(title, type, symbol)
        self.damage = damage
        self.durability = durability
        self.max_durability = durability
        
    def use(self, inventory=None):
        if self.durability > 0:
            self.durability -= 1
            self._break_and_remove(inventory)
            return self.damage
        return 0

class Sword(Weapon):
    def __init__(self, title, damage, symbol, durability=70):
        super().__init__(title, "melee", symbol, damage, durability)
        self.combo_counter = 0
        
    def use(self, inventory=None):
        damage = super().use(inventory)
        self.combo_counter += 1
        if self.combo_counter % 3 == 0:
            print(f"⚔️ Комбо-удар! Урон x2")
            return damage * 2
        return damage

class Bow(Weapon):
    def __init__(self, title, damage, symbol, range=5, durability=30):
        super().__init__(title, "ranged", symbol, damage, durability)
        self.range = range
        
    def use(self, inventory=None):
        damage = super().use(inventory)
        if random.random() < 0.25:
            print(f"🎯 Критический выстрел! Урон x1.5")
            return int(damage * 1.5)
        return damage

class IceStaff(Weapon):
    def __init__(self, title, damage, symbol, range=3, durability=50):
        super().__init__(title, "magic", symbol, damage, durability)
        self.combo_counter = 0
        self.range = range
    
    def use(self, inventory=None):
        damage = super().use(inventory)
        self.combo_counter += 1
        if self.combo_counter % 3 == 0:
            print(f"❄️ Ледяной выстрел! Урон x3")
            return damage * 3
        return damage

class Shield(Items):
    def __init__(self, title, save_from_damage, symbol, durability=20):
        super().__init__(title, "armor", symbol)
        self.save_from_damage = save_from_damage
        self.durability = durability
        self.max_durability = durability
        
    def block(self, damage, inventory=None):
        if self.durability <= 0:
            return damage
        blocked = min(damage, self.save_from_damage)
        self.durability -= 1
        self._break_and_remove(inventory)
        return damage - blocked

class HealthPotion(Items):
    def __init__(self, title, heal_amount, symbol, durability=1):  # прочность 1 - одноразовое
        super().__init__(title, "heal_potion", symbol)
        self.heal_amount = heal_amount
        self.durability = durability
        self.max_durability = durability

    def use(self, target, inventory=None):
        if self.durability <= 0:
            return 0
            
        heal = self.heal_amount
        self.durability -= 1
        target.health += heal
        print(f"{target.symbol} восстановил {heal} HP!")
        
        self._break_and_remove(inventory)
        return heal

class PoisonPotion(Items):
    def __init__(self, title, damage_per_turn, symbol, duration, durability=1):
        super().__init__(title, "poison_potion", symbol)
        self.damage_per_turn = damage_per_turn
        self.duration = duration
        self.durability = durability
        self.max_durability = durability

    def use(self, target, inventory=None):
        if self.durability <= 0:
            return 0
            
        self.durability -= 1
        target.apply_effect("poison", self.damage_per_turn, self.duration)
        print(f"{target.symbol} отравлен на {self.duration} ходов!")
        
        self._break_and_remove(inventory)
        return self.damage_per_turn * self.duration  


sword = Sword(title="Меч", damage=20, symbol="⚔️")
bow = Bow(title="Лук", damage=15, symbol="🏹", range=5)
ice_staff = IceStaff(title="Ледяной посох", damage=25, symbol="❄️", range=3)
shield = Shield(title="Щит", save_from_damage=10, symbol="🛡️")
health_potion = HealthPotion(title="Зелье здоровья", heal_amount=30, symbol="❤️")
poison_potion = PoisonPotion(title="Ядовитое зелье", damage_per_turn=5, symbol="🧪", duration=3)

undead = Undead(health=40, symbol="💀", position=Position(1, 1), damage=10)
ghost = Ghost(health=50, symbol="👻", position=Position(2, 2), damage=15)
dark_mage = DarkMage(health=80, symbol="🧙", position=Position(3, 3), damage=15)

hero = Hero(100, "@", Position(0, 0))
hero.inventory = Inventory(10)

print("Нажмите Tab чтобы открыть/закрыть инвентарь")
while True:
    time.sleep(1)