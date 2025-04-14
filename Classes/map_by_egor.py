import random
import sys
import msvcrt  # Для Windows
from typing import List, Dict
from colorama import init, Back, Fore

init(autoreset=True)

#----------------------------------------------------------------------------
#----------------------------Base Classes------------------------------------

class Person:
    def __init__(self, x, y, char, color): 
        self.x = x
        self.y = y
        self.char = char
        self.color = color


class Hero(Person):
    def __init__(self, x, y, max_health, current_health):
        super().__init__(x, y, '@', Fore.RED)
        self.max_health = max_health
        self.current_health = current_health
        self.max_health = max_health
        self.current_health = current_health


class Enemy(Person):
    def __init__(self, x, y, max_health, current_health):
        super().__init__(x, y, 'E', Fore.GREEN)


#----------------------------------------------------------------------------
#----------------------------Классы для врагов------------------------------------
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

#----------------------------------------------------------------------------
#------------------------------Инвентарь-------------------------------------

class Inventory:
    def __init__(self, count_of_slots, items=None):
        self.count_of_slots = count_of_slots
        self.items = items if items is not None else {}

    def add_item(self, item):
        if len(self.items) < self.count_of_slots:
            slot = len(self.items) + 1
            self.items[slot] = item
            print(f"Предмет {item.title} добавлен в слот {slot}.")
        else:
            print("Инвентарь полон!")

#----------------------------------------------------------------------------
#------------------------------Вещи------------------------------------------

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

#-----------------------------------------------------------------------------
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
#-------------------------------------------------------------------------------
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


#----------------------------------------------------------------------------
#----------------------------Генерация карты------------------------------------

class RoomGenerator:
    def __init__(self, width: int, height: int, max_rooms: int = 7):
        self.width = width
        self.height = height
        self.max_rooms = max_rooms

    def generate_tiles(self) -> tuple[List[List[str]], List[Dict]]:
        tiles = [[Back.BLACK + ' ' for _ in range(self.width)] for _ in range(self.height)]
        rooms = []

        for _ in range(self.max_rooms):
            room_width = random.randint(4, 8)
            room_height = random.randint(4, 8)

            x = random.randint(1, self.width - room_width - 2)
            y = random.randint(1, self.height - room_height - 2)

            new_room = {
                'x1': x,
                'y1': y,
                'x2': x + room_width - 1,
                'y2': y + room_height - 1
            }

            if not self._rooms_intersect(new_room, rooms):
                self._create_room(tiles, new_room)

                if rooms:
                    self._connect_rooms(tiles, rooms[-1], new_room)

                rooms.append(new_room)

        return tiles, rooms

    def _rooms_intersect(self, room: Dict, rooms: List[Dict]) -> bool:
        for r in rooms:
            if (room['x1'] <= r['x2'] + 1 and
                room['x2'] >= r['x1'] - 1 and
                room['y1'] <= r['y2'] + 1 and
                room['y2'] >= r['y1'] - 1):
                return True
        return False

    def _create_room(self, tiles: List[List[str]], room: Dict):
        for y in range(room['y1'], room['y2'] + 1):
            for x in range(room['x1'], room['x2'] + 1):
                if 0 <= x < self.width and 0 <= y < self.height:
                    tiles[y][x] = Back.WHITE + ' '

    def _connect_rooms(self, tiles: List[List[str]], room1: Dict, room2: Dict):
        x1, y1 = (room1['x1'] + room1['x2']) // 2, (room1['y1'] + room1['y2']) // 2
        x2, y2 = (room2['x1'] + room2['x2']) // 2, (room2['y1'] + room2['y2']) // 2

        if random.random() < 0.5:
            self._create_h_tunnel(tiles, x1, x2, y1)
            self._create_v_tunnel(tiles, y1, y2, x2)
        else:
            self._create_v_tunnel(tiles, y1, y2, x1)
            self._create_h_tunnel(tiles, x1, x2, y2)

    def _create_h_tunnel(self, tiles: List[List[str]], x1: int, x2: int, y: int):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            if 0 <= x < self.width and 0 <= y < self.height:
                tiles[y][x] = Back.WHITE + ' '

    def _create_v_tunnel(self, tiles: List[List[str]], y1: int, y2: int, x: int):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            if 0 <= x < self.width and 0 <= y < self.height:
                tiles[y][x] = Back.WHITE + ' '


#----------------------------------------------------------------------------
#----------------------------Управление игроком-------------------------------

class PlayerManager:
    def __init__(self, player, map_width: int, map_height: int):
        self.player = player
        self.map_width = map_width
        self.map_height = map_height

    def place_player(self, rooms: List[Dict]):
        if rooms:
            first_room = rooms[0]
            self.player.x = (first_room['x1'] + first_room['x2']) // 2
            self.player.y = (first_room['y1'] + first_room['y2']) // 2

    def move_player(self, dx: int, dy: int, tiles: List[List[str]]):
        new_x, new_y = self.player.x + dx, self.player.y + dy

        if (0 <= new_x < self.map_width and
            0 <= new_y < self.map_height and
            tiles[new_y][new_x] != Back.BLACK + ' '):
            self.player.x = new_x
            self.player.y = new_y


#----------------------------------------------------------------------------
#----------------------------Отрисовка карты----------------------------------

class MapRenderer:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height

    def render(self, tiles: List[List[str]], player):
        display = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                if Back.BLACK in tiles[y][x]:
                    row.append(Back.BLACK + ' ')
                else:
                    row.append(Back.WHITE + ' ')
            display.append(row)

        if 0 <= player.y < self.height and 0 <= player.x < self.width:
            bg = Back.BLACK if Back.BLACK in tiles[player.y][player.x] else Back.WHITE
            display[player.y][player.x] = bg + player.color + player.char

        print("\033[H\033[J")  # Очистка терминала
        for row in display:
            print(''.join(row))
        print("WASD - движение, Q - выход (без Enter)")
        print(" <- -> - переключаться между сломами)")

#----------------------------------------------------------------------------
#----------------------------Основной класс Map-------------------------------

class Map:
    def __init__(self, width: int, height: int, max_rooms: int = 7):
        self.width = width
        self.height = height
        self.max_rooms = max_rooms

        # Генерация карты
        self.room_generator = RoomGenerator(width, height, max_rooms)
        self.tiles, self.rooms = self.room_generator.generate_tiles()

        # Игрок
        self.player = Hero(0, 0, 100, 100)
        self.player_manager = PlayerManager(self.player, width, height)
        self.player_manager.place_player(self.rooms)

        # Отрисовка
        self.renderer = MapRenderer(width, height)

    def render(self):
        self.renderer.render(self.tiles, self.player)

    def move_player(self, dx: int, dy: int):
        self.player_manager.move_player(dx, dy, self.tiles)

#----------------------------------------------------------------------------
#----------------------------Запуск основного кода---------------------------

def get_key():
    """Функция для получения нажатой клавиши без Enter"""
    while True:
        if msvcrt.kbhit():
            try:
                # Исправление: Добавлена обработка возможных ошибок декодирования
                key = msvcrt.getch().decode('utf-8', errors='ignore').lower()
                if key in ['w', 'a', 's', 'd', 'q']:
                    return key
            except UnicodeDecodeError:
                # Игнорируем символы, которые не могут быть декодированы
                continue


""" sword = Sword(title="Меч", damage=20, symbol="⚔️")
bow = Bow(title="Лук", damage=15, symbol="🏹", range=5)
ice_staff = IceStaff(title="Ледяной посох", damage=25, symbol="❄️", range=3)
shield = Shield(title="Щит", save_from_damage=10, symbol="🛡️")
health_potion = HealthPotion(title="Зелье здоровья", heal_amount=30, symbol="❤️")
poison_potion = PoisonPotion(title="Ядовитое зелье", damage_per_turn=5, symbol="🧪", duration=3)


inventory = Inventory(count_of_slots=10)
inventory.add_item(sword)


hero_position = Position(3, 5)
hero = Hero(health=100, symbol="@", position=hero_position, inventory=inventory, active_slot=sword)


undead = Undead(health=40, symbol="💀", position=Position(1, 1), damage=10)
ghost = Ghost(health=50, symbol="👻", position=Position(2, 2), damage=15)
dark_mage = DarkMage(health=80, symbol="🧙", position=Position(3, 3), damage=15) """

def main():
    game_map = Map(40, 20)
    
    while True:
        game_map.render()
        key = get_key()
        
        if key == 'q':
            break
        elif key == 'w':
            game_map.move_player(0, -1)
        elif key == 'a':
            game_map.move_player(-1, 0)
        elif key == 's':
            game_map.move_player(0, 1)
        elif key == 'd':
            game_map.move_player(1, 0)

        # Исправление: Добавлена принудительная отрисовка после движения
        game_map.render()

if __name__ == "__main__":
    main()