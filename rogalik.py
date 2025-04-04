class Hero:

    def __init__ (self, health, current_heath, position):
        self.health = health
        self.max_health = health

       


class Position:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Hero(Person):
    def __init__ (self, symbol):
        super().__init__(health, po sition)
        self.symbol = symbol
        self.inventory = Inventory(5)

         def attack_person(self,person):
    
class Hero(Person):
    def __init__ (self, symbol):
        super().__init__(health, position)
        self.symbol = symbol

class Item:
    def __init__ (self,title,type):
        self.title = title
        self.type = type

class Sword(Item):
    def __init__(self,title,type,damage):
        super.__init__(title,type)
        self.damage = damage

class Inventory:
    def __init__ (self,size, items=[]):
        self.items = items
        self.size

    def add_item(self,item):
        self.items.