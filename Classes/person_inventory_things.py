class Position:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Person:
    def __init__(self, health, position =(), inventory, active_slot = None):
        self.health = health
        self.max_health = health
        self.position = position        
        self.inventory = Inventory(5)
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
    def __init__ (self, count_of_slots, items = {}):
        self.count_of_slots = count_of_slots
        self.items = items

class Items:
    def __init__(self, title, type):
        self.title = title
        self.type = type

class Sword:
    def __init__(self, title, type, damage, symbol):
        super().__init__(title, type)
        self.damage = damage
        self.symbol = symbol


class Bomb:
    def __init__(self, title, type, damage, self_damage, symbol):
        super().__init__(title, type)
        self.damage = damage
        self.self_damage = self_damage
        self.symbol = symbol


class Dog:
    def __init__(self, title, type, damage, symbol):
        super().__init__(title, type)
        self.damage = damage
        self.symbol = symbol


class Potion:
    def __init__(self, title, type, damage_, symbol):
        super().__init__(title, type)
        self.damage = damage
        self.symbol = symbol


class Shield:
    def __init__(self, title, type, save_from_damage, symbol):
        super().__init__(title, type)
        self.save_from_damage = save_from_damage
        self.symbol = symbol


class Medicine:
    def __init__(self, title, type, medication, symbol):
        super().__init__(title, type)
        self.medication = medication
        self.symbol = symbol



hero_position = Position(3, 5)

hero = Hero(health=100, position=hero_position, symbol="@")

sword = Sword("Меч", "attack", 50, "🗡")
bomb = Bomb("Бомба", "attack", 100, 50, "☭")
dog_friend = Bomb("Пёся", "attack", 50, "𓃠")
position = Position("Зелье", "attack", 5, "🧪")

shield = Shield("Shit", "block", 20, "⛨")
medicine = Medicine("Хилка", "medicine", 20, "✙")
