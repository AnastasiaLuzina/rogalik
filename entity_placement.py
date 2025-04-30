import random
from persons import Undead, Ghost, DarkMage
from items import Sword, Bow, IceStaff, HealthPotion, PoisonPotion

class EntityPlacer:
    def __init__(self, game):
        self.game = game

    def place_hero_and_entities(self):
        hero_room = random.choice(self.game.map.rooms)
        hero_x = random.randint(hero_room['x1'], hero_room['x2'])
        hero_y = random.randint(hero_room['y1'], hero_room['y2'])
        self.game.hero.x = hero_x
        self.game.hero.y = hero_y

        if (hero_x, hero_y) not in self.game.map.walkable:
            hero_room = random.choice(self.game.map.rooms)
            hero_x = random.randint(hero_room['x1'], hero_room['x2'])
            hero_y = random.randint(hero_room['y1'], hero_room['y2'])
            self.game.hero.x = hero_x
            self.game.hero.y = hero_y

        item_templates = [
            Sword("Меч", 20, '/'),
            Bow("Лук", 15, ')'),
            IceStaff("Ледяной посох", 25, '*'),
            HealthPotion("Зелье здоровья", 30, 'H'),
            PoisonPotion("Ядовитое зелье", 5, 'P', 3)
        ]
        items_to_place = []
        for item in item_templates:
            count = random.randint(1, 3)
            for _ in range(count):
                if isinstance(item, Sword):
                    new_item = Sword(item.title, item.damage, item.symbol)
                elif isinstance(item, Bow):
                    new_item = Bow(item.title, item.damage, item.symbol)
                elif isinstance(item, IceStaff):
                    new_item = IceStaff(item.title, item.damage, item.symbol)
                elif isinstance(item, HealthPotion):
                    new_item = HealthPotion(item.title, item.heal_amount, item.symbol)
                elif isinstance(item, PoisonPotion):
                    new_item = PoisonPotion(item.title, item.damage_per_turn, item.symbol, item.duration)
                items_to_place.append(new_item)

        for room in self.game.map.rooms:
            if room != hero_room:
                num_enemies = random.randint(0, 1)
                self.game.total_enemies += num_enemies
                for _ in range(num_enemies):
                    enemy_type = random.choice([Undead, Ghost, DarkMage])
                    x = random.randint(room['x1'], room['x2'])
                    y = random.randint(room['y1'], room['y2'])
                    self.game.enemies.append(enemy_type(x, y))
                if items_to_place:
                    item = items_to_place.pop()
                    x = random.randint(room['x1'], room['x2'])
                    y = random.randint(room['y1'], room['y2'])
                    self.game.items.append((x, y, item))

        self.game.health_panel.total_enemies = self.game.total_enemies