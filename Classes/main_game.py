import random
import os
import sys
import curses
from map import Map, MAP_WIDTH, MAP_HEIGHT
from persons import Hero, Undead, Ghost, DarkMage
from items import Sword, Bow, IceStaff, Shield, HealthPotion, PoisonPotion
from interface import HealthPanel, InteractionPanel, PANEL_WIDTH, HEALTH_HEIGHT, INTERACTION_HEIGHT
from map_render import Renderer
from combat import CombatSystem
from vision import VisionSystem
from inventory import Inventory
from colorama import init


init(autoreset=True) 

class Game:
    def __init__(self):
        # Инициализация основных компонентов
        self.renderer = Renderer()
        self.renderer.init_screen()
        
        # Создание героя ПЕРВЫМ
        self.hero = Hero(x=0, y=0, game=self)
        
        # Инициализация инвентаря
        self.inventory = Inventory(count_of_slots=8, game=self)
        self.hero.inventory = self.inventory
        
        # Инициализация карты и систем
        self.map = Map(MAP_WIDTH, MAP_HEIGHT)
        self.vision_system = VisionSystem(vision_radius=5)
        self.enemies = []
        self.items = []
        self.game_over = False
        self.messages = []
        
        # Инициализация панелей интерфейса
        self.health_panel = HealthPanel(
            x=MAP_WIDTH + 1, y=1,
            width=PANEL_WIDTH, height=HEALTH_HEIGHT,
            current_hp=self.hero.current_health,  # Используем реальное здоровье
            max_hp=self.hero.max_health
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
        self.hero.x = hero_x
        self.hero.y = hero_y

        item_templates = [
            Sword("Меч", 20, '/', 50),
            Bow("Лук", 15, ')', 5, 30),
            IceStaff("Ледяной посох", 25, '*', 3, 50),
            Shield("Щит", 10, '0', 20),
            HealthPotion("Зелье здоровья", 30, 'H'),
            PoisonPotion("Ядовитое зелье", 5, 'P', 3)
        ]

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

        for room in self.map.rooms:
            if room != hero_room:
                num_enemies = random.randint(0, 3)
                for _ in range(num_enemies):
                    enemy_type = random.choice([Undead, Ghost, DarkMage])
                    x = random.randint(room['x1'], room['x2'])
                    y = random.randint(room['y1'], room['y2'])
                    self.enemies.append(enemy_type(x, y))

                if items_to_place and random.random() < 0.8:
                    item = items_to_place.pop()
                    x = random.randint(room['x1'], room['x2'])
                    y = random.randint(room['y1'], room['y2'])
                    self.items.append((x, y, item))

    def _draw_initial_map(self):
        # Initialize vision system and get visible entities
        self.vision_system.update_vision(self.hero, self.map, self.enemies, self.items)
        visible_entities = self.vision_system.get_visible_entities(self.hero, self.map, self.enemies, self.items)
        
        # Render map with vision system
        self.renderer.render_map(
            self.map,
            self.hero,
            visible_entities['enemies'],
            visible_entities['items'],
            self.vision_system,
            force_redraw=True  # Force redraw to ensure correct initial render
        )
        self._draw_panels()
        self.renderer.screen.refresh()

    def _draw_panels(self):
        self.health_panel.render(self.renderer.screen)
        self.interaction_panel.render(self.renderer.screen)


    def _update_display(self):
        # Update visibility
        self.vision_system.update_vision(self.hero, self.map, self.enemies, self.items)
        visible_entities = self.vision_system.get_visible_entities(self.hero, self.map, self.enemies, self.items)
        
        
        self.renderer.screen.clear()
        self.renderer.render_map(
            self.map,
            self.hero,
            visible_entities['enemies'],
            visible_entities['items'],
            self.vision_system,
            force_redraw=True
        )
        self._draw_panels()
        self.renderer.screen.refresh()

    def _move_hero(self, dx, dy):
        new_x, new_y = self.hero.x + dx, self.hero.y + dy
        if (new_x, new_y) in self.map.walkable:
            enemy = self._get_enemy_at(new_x, new_y)
            if enemy:
                self._handle_combat(enemy)  # Запуск боя
                return  # Не перемещаем героя, если начался бой
            self.hero.x, self.hero.y = new_x, new_y
            self._update_display()

    def _get_enemy_at(self, x, y):
        for enemy in self.enemies:
            if enemy.x == x and enemy.y == y and enemy.current_health > 0:
                return enemy
        return None


    def _handle_combat(self, enemy):
        """Запускает боевую систему с выбранным врагом"""
        combat = CombatSystem(self, enemy, self.renderer.screen)
        while combat.in_combat and not self.game_over:
            try:
                key = self.renderer.screen.getch()
                if key != -1:
                    combat.process_input(chr(key).lower())
            except curses.error:
                pass
        self._update_display()  # Перерисовываем карту после боя
        self.messages = []  # Очищаем сообщения

    def _sync_health(self):
        self.health_panel.current_hp = self.hero.current_health
        
    def _update_interface(self):
        self._sync_health()  # Синхронизируем здоровье
        self.check_item_interaction()  # Проверяем взаимодействие с предметами
        if self.inventory.is_open:
            self._draw_inventory()  # Отрисовываем инвентарь
        else:
            self._update_display() 
        # Показ/скрытие кнопки
        if self.nearby_items:
            self.interaction_panel.show_pickup_button(len(self.nearby_items))
        else:
            self.interaction_panel.hide_pickup_button()

    def _draw_inventory(self):
        """Новый метод отрисовки слотов"""
        self.interaction_panel.show_inventory(
            self.inventory.items,
            self.inventory.active_slot
        )
        self._update_display()         

    def _handle_key_press(self, key):
        # Обработка инвентаря
        if self.inventory.is_open:
            if key == curses.KEY_LEFT:
                self.inventory.change_slot(-1)
            elif key == curses.KEY_RIGHT:
                self.inventory.change_slot(1)
            elif key == ord('e'):  # Использовать
                self.inventory.use_active_item()
            elif key == ord('r'):  # Выбросить
                self.inventory.remove_active_item()
            elif key == 9:  # TAB
                self.inventory.toggle()
            self._update_interface()
            return

        # Обработка обычного режима
        if key == 9:  # Открыть инвентарь (TAB)
            self.inventory.toggle()
        elif key == ord('f'):  # Подобрать предмет
            self.handle_pickup()
        elif key in (ord('w'), ord('a'), ord('s'), ord('d')):  # Движение
            dx = 1 if key == ord('d') else -1 if key == ord('a') else 0
            dy = 1 if key == ord('s') else -1 if key == ord('w') else 0
            self._move_hero(dx, dy)
        elif key == ord('q'):  # Выход
            self.game_over = True

    def _toggle_inventory(self):
        self.inventory_open = not self.inventory_open
        if self.inventory_open:
            self._show_inventory()
        else:
            self.interaction_panel.messages = []
            self._update_interface()

    def _show_inventory(self):
        self.interaction_panel.show_inventory(
            items=self.inventory_items,
            selected=self.selected_item
        )
        self._update_display()

    def check_item_interaction(self):
        """Проверяет предметы в соседних клетках (без диагоналей)"""
        self.nearby_items = []
        hero_x, hero_y = self.hero.x, self.hero.y
        for item in self.items:
            x, y, _ = item
            # Проверка на прямое соседство (вверх/вниз/влево/вправо)
            if (abs(hero_x - x) == 1 and hero_y == y) or (abs(hero_y - y) == 1 and hero_x == x):
                self.nearby_items.append(item)
        return len(self.nearby_items) > 0

    def handle_pickup(self):
        if not self.nearby_items:
            return
        
        picked_items = []
        for item in self.nearby_items[:]:
            x, y, item_obj = item
            if self.inventory.add_item(item_obj):
                self.items.remove(item)
                picked_items.append(item_obj.title)
        
        if picked_items:
            self.interaction_panel.add_message(f"Подобрано: {', '.join(picked_items)}")
            self.nearby_items.clear()  # Очищаем список после подбора
            self._update_interface()  # Принудительно обновляем интерфейс

                
    def _select_item(self, direction: int):
        if not self.inventory_open:
            return
        self.selected_item = (self.selected_item + direction) % len(self.inventory_items)
        self._show_inventory()

    def _use_item(self):
        if not self.inventory_open or not self.inventory_items:
            return
        selected = self.inventory_items[self.selected_item]
        self.inventory_open = False
        self.messages.append(f"Вы выбрали: {selected.title}")
        self._update_interface()

    def run(self):
        try:
            while not self.game_over:
                try:
                    key = self.renderer.screen.getch()
                    if key != -1:
                        self._handle_key_press(key)
                except curses.error:
                    pass
        finally:
            self.renderer.close_screen()

if __name__ == "__main__":
    game = Game()
    game.run()