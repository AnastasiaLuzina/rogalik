import random
import os
import sys
from colorama import init, Fore, Back
from map_by_egor import Map, MAP_WIDTH, MAP_HEIGHT
from persons import Hero, Undead, Ghost, DarkMage
from items import Sword, Bow, IceStaff, Shield, HealthPotion, PoisonPotion

# Для обработки нажатий клавиш без Enter
if os.name == 'nt':
    import msvcrt
else:
    import tty, termios

init(autoreset=True)

class Game:
    def __init__(self):
        self.map = Map(MAP_WIDTH, MAP_HEIGHT)
        print("Map wall_char:", self.map.wall_char)
        print("Map empty_char:", self.map.empty_char)
        self.hero = None
        self.enemies = []
        self.items = []
        self.game_over = False
        self.last_hero_pos = (0, 0)
        
        self._place_hero_and_entities()
        self._draw_initial_map()
    
    def _place_hero_and_entities(self):
        hero_room = random.choice(self.map.rooms)
        hero_x = random.randint(hero_room['x1'], hero_room['x2'])
        hero_y = random.randint(hero_room['y1'], hero_room['y2'])
        self.hero = Hero(hero_x, hero_y)
        self.last_hero_pos = (hero_x, hero_y)
        
        # Создаем список всех возможных предметов с количеством от 1 до 2
        item_templates = [
            Sword("Меч", 20, '⚔️', 50),
            Bow("Лук", 15, '🏹', 5, 30),
            IceStaff("Ледяной посох", 25, '❄️', 3, 50),
            Shield("Щит", 10, '🛡️', 20),
            HealthPotion("Зелье здоровья", 30, '❤️'),
            PoisonPotion("Ядовитое зелье", 5, '🧪', 3)
        ]
        
        # Для каждого типа предмета создаем от 1 до 2 экземпляров
        items_to_place = []
        for item in item_templates:
            count = random.randint(1, 2)
            for _ in range(count):
                # Создаем новый экземпляр предмета
                if isinstance(item, Sword):
                    new_item = Sword(item.title, item.damage, item.symbol, item.durability)
                elif isinstance(item, Bow):
                    new_item = Bow(item.title, item.damage, item.symbol, item.range, item.durability)
                elif isinstance(item, IceStaff):
                    new_item = IceStaff(item.title, item.damage, item.symbol, item.range, item.durability)
                elif isinstance(item, Shield):
                    new_item = Shield(item.title, item.save_from_damage, item.symbol, item.durability)
                elif isinstance(item, HealthPotion):
                    new_item = HealthPotion(item.title, item.heal_amount, item.symbol)
                elif isinstance(item, PoisonPotion):
                    new_item = PoisonPotion(item.title, item.damage_per_turn, item.symbol, item.duration)
                items_to_place.append(new_item)
        
        # Размещаем врагов и предметы
        for room in self.map.rooms:
            if room != hero_room:
                # Размещаем врагов
                num_enemies = random.randint(0, 3)
                for _ in range(num_enemies):
                    enemy_type = random.choice([Undead, Ghost, DarkMage])
                    x = random.randint(room['x1'], room['x2'])
                    y = random.randint(room['y1'], room['y2'])
                    self.enemies.append(enemy_type(x, y))
                
                # Размещаем предметы, если они есть
                if items_to_place and random.random() < 0.8:  # Увеличили шанс появления предметов
                    item = items_to_place.pop()
                    x = random.randint(room['x1'], room['x2'])
                    y = random.randint(room['y1'], room['y2'])
                    self.items.append((x, y, item))
    
    def _draw_initial_map(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # Рисуем всю карту один раз
        for y in range(self.map.height):
            for x in range(self.map.width):
                self._draw_cell(x, y)
        
        # Рисуем предметы
        for x, y, item in self.items:
            print(f"\033[{y+1};{x+1}H" + Fore.GREEN + item.symbol, end='', flush=True)
        
        # Рисуем врагов
        for enemy in self.enemies:
            if enemy.current_health > 0:
                print(f"\033[{enemy.y+1};{enemy.x+1}H" + enemy.color + enemy.char, end='', flush=True)
        
        # Рисуем героя
        print(f"\033[{self.hero.y+1};{self.hero.x+1}H" + self.hero.color + self.hero.char, end='', flush=True)
        
        self._display_hero_status()
    
    def _draw_cell(self, x, y):
        if (x, y) in [(item[0], item[1]) for item in self.items]:
            return  # Предметы рисуем отдельно
        
        for enemy in self.enemies:
            if enemy.x == x and enemy.y == y and enemy.current_health > 0:
                return  # Врагов рисуем отдельно
        
        if self.hero.x == x and self.hero.y == y:
            return  # Героя рисуем отдельно
        
        cell = self.map.tiles[y][x]
        if cell == self.map.wall_char:  # Используем атрибут из класса Map
            print(f"\033[{y+1};{x+1}H" + Fore.BLACK + cell, end='', flush=True)
        else:
            print(f"\033[{y+1};{x+1}H" + self.map.empty_char, end='', flush=True)  # Используем атрибут из класса Map
    
    def _update_display(self):
        # Очищаем предыдущую позицию героя
        old_x, old_y = self.last_hero_pos
        if (old_x, old_y) not in [(item[0], item[1]) for item in self.items]:
            self._draw_cell(old_x, old_y)
        
        # Рисуем героя на новой позиции
        print(f"\033[{self.hero.y+1};{self.hero.x+1}H" + self.hero.color + self.hero.char, end='', flush=True)
        
        self.last_hero_pos = (self.hero.x, self.hero.y)
        self._display_hero_status()
    
    def _display_hero_status(self):
        status_line = MAP_HEIGHT + 1
        health_bar = f"HP: {self.hero.current_health}/{self.hero.max_health}"
        print(f"\033[{status_line};1H" + Fore.RED + health_bar + " " + Fore.YELLOW + "Управление: WASD, Q-выход", end='', flush=True)
        print("\033[K", end='')  # Очищаем строку от возможных предыдущих сообщений
    
    def _move_hero(self, dx, dy):
        new_x, new_y = self.hero.x + dx, self.hero.y + dy
        
        if (new_x, new_y) in self.map.walkable:
            enemy = self._get_enemy_at(new_x, new_y)
            if enemy and enemy.current_health > 0:
                self._handle_combat(enemy)
                return
            
            self.hero.x, self.hero.y = new_x, new_y
            self._update_display()
    
    def _get_enemy_at(self, x, y):
        for enemy in self.enemies:
            if enemy.x == x and enemy.y == y and enemy.current_health > 0:
                return enemy
        return None
    
    def _handle_combat(self, enemy):
        hero_damage = 10
        enemy.current_health -= hero_damage
        print(f"\033[{MAP_HEIGHT+2};1H" + Fore.RED + f"Вы атаковали {enemy.char} и нанесли {hero_damage} урона!", end='', flush=True)
        
        if enemy.current_health <= 0:
            if isinstance(enemy, Undead) and enemy.resurrect():
                pass
            else:
                print(f"\033[{MAP_HEIGHT+3};1H" + Fore.GREEN + f"Вы победили {enemy.char}!", end='', flush=True)
        
        if enemy.current_health > 0:
            damage_to_hero = enemy.damage
            self.hero.current_health -= damage_to_hero
            print(f"\033[{MAP_HEIGHT+3};1H" + Fore.RED + f"{enemy.char} атаковал вас и нанес {damage_to_hero} урона!", end='', flush=True)
            
            if self.hero.current_health <= 0:
                print(f"\033[{MAP_HEIGHT+4};1H" + Fore.RED + "Вы погибли! Игра окончена.", end='', flush=True)
                self.game_over = True
        
        self._update_display()

    def _get_key(self):
        if os.name == 'nt':
            if msvcrt.kbhit():
                char = msvcrt.getch().decode('utf-8').lower()
                return char
        else:
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(sys.stdin.fileno())
                if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                    char = sys.stdin.read(1).lower()
                    return char
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return None

    def run(self):
        while not self.game_over:
            key = self._get_key()
            if not key:
                continue
                
            if key == 'q':
                break
            
            elif key == 'w':
                self._move_hero(0, -1)
            elif key == 'a':
                self._move_hero(-1, 0)
            elif key == 's':
                self._move_hero(0, 1)
            elif key == 'd':
                self._move_hero(1, 0)

if __name__ == "__main__":
    os.system('mode con: cols={} lines={}'.format(MAP_WIDTH+2, MAP_HEIGHT+5))
    game = Game()
    game.run()