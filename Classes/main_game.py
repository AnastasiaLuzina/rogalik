import random
import os
import sys
from colorama import init, Fore
from map_by_egor import (
    Map, 
    HealthPanel,    # <--- Добавлено
    InteractionPanel, # <--- Добавлено
    MAP_WIDTH, 
    MAP_HEIGHT, 
    PANEL_WIDTH, 
    HEALTH_HEIGHT, 
    INTERACTION_HEIGHT
)
from persons import Hero, Undead, Ghost, DarkMage
from items import Sword, Bow, IceStaff, Shield, HealthPotion, PoisonPotion

if os.name == 'nt':
    import msvcrt
else:
    import tty, termios

init(autoreset=True)

class Game:
    def __init__(self):
        self.map = Map(MAP_WIDTH, MAP_HEIGHT)

        self.hero = None
        self.last_hero_pos = (0, 0)

        self.enemies = []

        self.items = []

        self.game_over = False

        self.messages = []

        self.inventory_items = []  # Список предметов в инвентаре
        self.inventory_open = False
        self.selected_item = 0


        #  дефолтный пример списка.
        self.inventory_items = [
            HealthPotion("Зелье здоровья", 30, '❤️'),
            Sword("Меч", 20, '⚔️', 50),
            Shield("Щит", 10, '🛡️', 20)
        ]

        


        # Панели интерфейса
        self.health_panel = HealthPanel(
            x=MAP_WIDTH + 1, y=1,
            width=PANEL_WIDTH, height=HEALTH_HEIGHT,
            current_hp=100, max_hp=100
        )
        self.interaction_panel = InteractionPanel(
            x=MAP_WIDTH + 1, y=HEALTH_HEIGHT + 1,
            width=PANEL_WIDTH, height=INTERACTION_HEIGHT
        )
        
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
            Sword("Меч", 20, '◻', 50),
            Bow("Лук", 15, '◻', 5, 30),
            IceStaff("Ледяной посох", 25, '◻', 3, 50),
            Shield("Щит", 10, '◻', 20),
            HealthPotion("Зелье здоровья", 30, '◻'),
            PoisonPotion("Ядовитое зелье", 5, '◻', 3)
        ]

        # Для каждого типа предмета создаем от 1 до 2 экземпляров
        items_to_place = []
        for item in item_templates:
            count = random.randint(1, 2)
            for _ in range(count):
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
        self.map.render(hero=self.hero, enemies=self.enemies, items=self.items)  # Используем обновленный render
        self._draw_panels()



    def _draw_map(self):
        for y in range(self.map.height):
            line = []
            for x in range(self.map.width):
                # Проверяем элементы на текущей позиции
                cell_content = None

                # Герой
                if x == self.hero.x and y == self.hero.y:
                    cell_content = self.hero.color + self.hero.char + Fore.RESET

                # Предметы
                for item_x, item_y, item in self.items:
                    if item_x == x and item_y == y:
                        cell_content = Fore.GREEN + item.symbol + Fore.RESET

                # Враги
                for enemy in self.enemies:
                    if enemy.x == x and enemy.y == y and enemy.current_health > 0:
                        cell_content = enemy.color + enemy.char + Fore.RESET

                # Стены/пол
                if not cell_content:
                    cell_content = Fore.BLACK + self.map.wall_char if self.map.tiles[y][x] == self.map.wall_char else '  '

                line.append(cell_content)

            # Добавляем правую границу карты
            line.append(Fore.BLACK + '▓')
            print(''.join(line))

    def _draw_panels(self):
    
        # Отрисовка панелей
        self.health_panel.render()
        self.interaction_panel.render()

    def _update_display(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        self.map.render(hero=self.hero, enemies=self.enemies, items=self.items)
        self._draw_panels()
    

    def _draw_cell(self, x, y):
        if (x, y) in [(item[0], item[1]) for item in self.items]:
            return  # Предметы рисуем отдельно
        for enemy in self.enemies:
            if enemy.x == x and enemy.y == y and enemy.current_health > 0:
                return  # Врагов рисуем отдельно
        if self.hero.x == x and self.hero.y == y:
            return  # Героя рисуем отдельно

        cell = self.map.tiles[y][x]
        if cell == self.map.wall_char:
            print(f"\033[{y+1};{x+1}H" + Fore.BLACK + cell, end='', flush=True)
        else:
            print(f"\033[{y+1};{x+1}H" + '  ', end='', flush=True)



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
        
        # Создаем базовое сообщение
        base_msg = f"Вы атаковали {enemy.char} (-{hero_damage} HP)"
        self.messages.append(Fore.RED + base_msg)
        
        if enemy.current_health <= 0:
            self.messages.append(Fore.GREEN + f"{enemy.char} побежден!")
        else:
            damage_to_hero = enemy.damage
            self.hero.current_health -= damage_to_hero
            self.messages.append(Fore.RED + f"{enemy.char} атакует вас (-{damage_to_hero} HP)")
        
        if self.hero.current_health <= 0:
            self.messages.append(Fore.RED + "ВЫ ПОГИБЛИ!")
            self.game_over = True
        
        self._update_interface()

    def _update_interface(self):
        # Обновляем здоровье

        self.health_panel.current_hp = self.hero.current_health
        self.health_panel.render()
        
        # Добавляем сообщения через InteractionPanel
        for msg in self.messages[-5:]:
            self.interaction_panel.add_message(msg)
        
        # Не очищаем self.messages здесь!
        # Очистка будет происходить только при закрытии инвентаря
        
        # Отрисовываем интерфейс
        self.interaction_panel.render()

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

    def _handle_key_press(self, key):

        if self.inventory_open:
            if key == 'w' or key == 'up':
                self._select_item(-1)
            elif key == 's' or key == 'down':
                self._select_item(+1)
            elif key == 'enter':
                self._use_item()
            return

        elif key == 'q':
            self.game_over = True
        elif key in ('w', 'a', 's', 'd'):
            self._move_hero(
                dx=1 if key == 'd' else -1 if key == 'a' else 0,
                dy=1 if key == 's' else -1 if key == 'w' else 0
                )
        elif key == 'i':  # Обработка нажатия "I"
            self._toggle_inventory()

    def _toggle_inventory(self):
        """Переключает состояние инвентаря"""
        if self.inventory_open:
            self.inventory_open = False
            self.interaction_panel.messages = []
            self._update_interface()
        else:
            self.inventory_open = True
            self._show_inventory()
    
    def _show_inventory(self):
        """Отображает интерфейс инвентаря"""
        self.interaction_panel.show_inventory(
            items=self.inventory_items,
            selected=self.selected_item
        )
    
    def _select_item(self, direction: int):
        """Переключает выбранный предмет (direction: +1 или -1)"""
        if not self.inventory_open:
            return
        
        self.selected_item = (self.selected_item + direction) % len(self.inventory_items)
        self._show_inventory()
    
    def _use_item(self):
        if not self.inventory_open or not self.inventory_items:
            return
        selected = self.inventory_items[self.selected_item]
        self.inventory_open = False
        self.messages.append(Fore.GREEN + f"Вы выбрали: {selected.title}")
        self._update_display()  # Обновляем весь экран

        
        selected = self.inventory_items[self.selected_item]
        self.inventory_open = False
        self.messages.append(Fore.GREEN + f"Вы выбрали: {selected.title}")
        self._update_interface()

    def run(self):
        while not self.game_over:
            key = self._get_key()
            if not key:
                continue
            self._handle_key_press(key)  # Используем новый метод для обработки клавиш      


if __name__ == "__main__":
    # Установка размера консоли
    os.system(f'mode con: cols={MAP_WIDTH + PANEL_WIDTH + 1} lines={MAP_HEIGHT + 5}')
    os.system('cls')  # Очистка экрана
    game = Game()
    game.run()