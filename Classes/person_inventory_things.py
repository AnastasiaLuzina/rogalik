class Position:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Person:
    def __init__(self, health, position=Position(0, 0), inventory=None, active_slot=None):
        self.health = health
        self.max_health = health
        self.position = position        
        self.inventory = inventory if inventory is not None else Inventory(5)
        self.active_slot = active_slot

class Hero(Person):
    def __init__(self, health, position, symbol):
        super().__init__(health, position)
        self.symbol = symbol

class Enemy(Person):
    def __init__(self, health, position, symbol):
        super().__init__(health, position)
        self.symbol = symbol

class Inventory:
    def __init__(self, count_of_slots, items=None):
        self.count_of_slots = count_of_slots
        self.items = items if items is not None else {}

class Items:
    def __init__(self, title, type):
        self.title = title
        self.type = type

class Sword(Items):
    def __init__(self, title, type, damage, symbol):
        super().__init__(title, type)
        self.damage = damage
        self.symbol = symbol

class Bomb(Items):
    def __init__(self, title, type, damage, self_damage, symbol):
        super().__init__(title, type)
        self.damage = damage
        self.self_damage = self_damage
        self.symbol = symbol

class Dog(Items):
    def __init__(self, title, type, damage, symbol):
        super().__init__(title, type)
        self.damage = damage
        self.symbol = symbol

class Potion(Items):
    def __init__(self, title, type, damage, symbol):
        super().__init__(title, type)
        self.damage = damage
        self.symbol = symbol

class Shield(Items):
    def __init__(self, title, type, save_from_damage, symbol):
        super().__init__(title, type)
        self.save_from_damage = save_from_damage
        self.symbol = symbol

class Medicine(Items):
    def __init__(self, title, type, medication, symbol):
        super().__init__(title, type)
        self.medication = medication
        self.symbol = symbol
hero_position = Position(3, 5)
hero = Hero(health=100, position=hero_position, symbol="@")
sword = Sword("Меч", "attack", 50, "🗡")
bomb = Bomb("Бомба", "attack", 100, 50, "☭")
dog_friend = Dog("Пёся", "attack", 50, "𓃠")
potion = Potion("Зелье", "attack", 5, "🧪")
shield = Shield("Shit", "block", 20, "⛨")
medicine = Medicine("Хилка", "medicine", 20, "✙")