import random
import os
import sys
import curses
import time
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
        self.renderer = Renderer()
        self.renderer.init_screen()
        
        self.hero = Hero(x=0, y=0, game=self)
        self.inventory = Inventory(count_of_slots=8, game=self)
        self.hero.inventory = self.inventory
        
        self.map = Map(MAP_WIDTH, MAP_HEIGHT)
        self.vision_system = VisionSystem(vision_radius=5)
        self.enemies = []
        self.items = []
        self.game_over = False
        self.messages = []
        
        self.health_panel = HealthPanel(
            x=MAP_WIDTH + 1, y=1,
            width=PANEL_WIDTH, height=HEALTH_HEIGHT,
            current_hp=self.hero.current_health,
            max_hp=self.hero.max_health,
            game=self
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
            count = random.randint(1, 3)
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
                num_enemies = random.randint(1, 2)
                for _ in range(num_enemies):
                    enemy_type = random.choice([Undead, Ghost, DarkMage])
                    x = random.randint(room['x1'], room['x2'])
                    y = random.randint(room['y1'], room['y2'])
                    enemy = enemy_type(x, y)
                    self.enemies.append(enemy)
                    print(f"DEBUG: Added enemy {enemy.title} at ({x}, {y})")

                if items_to_place:
                    item = items_to_place.pop()
                    x = random.randint(room['x1'], room['x2'])
                    y = random.randint(room['y1'], room['y2'])
                    self.items.append((x, y, item))

        print(f"DEBUG: Placed {len(self.enemies)} enemies, {len(self.items)} items")

    def _draw_initial_map(self):
        self.vision_system.update_vision(self.hero, self.map, self.enemies, self.items)
        visible_entities = self.vision_system.get_visible_entities(self.hero, self.map, self.enemies, self.items)
        
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
        print("DEBUG: Initial map drawn")

    def _draw_panels(self):
        self.health_panel.render(self.renderer.screen)  # Изменено здесь
        self.interaction_panel.render(self.renderer.screen)  # И здесь
        print("DEBUG: Panels drawn, InteractionPanel messages: ", self.interaction_panel.messages)

    def _update_display(self):
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
        print("DEBUG: Display updated")

    def update_killed_counter(self):
        self.killed_enemies += 1
        self.health_panel.killed_enemies = self.killed_enemies
        self.health_panel.render(self.renderer.screen)  # Перерисовываем панель
        # Анимация обновления
        for _ in range(3):
            self.health_panel.render(self.renderer.screen)
            self.renderer.screen.refresh()
            time.sleep(0.1)
            curses.curs_set(0)

    def _move_hero(self, dx, dy):
        new_x, new_y = self.hero.x + dx, self.hero.y + dy
        if (new_x, new_y) in self.map.walkable:
            enemy = self._get_enemy_at(new_x, new_y)
            if enemy:
                self._handle_combat(enemy)
                return
            self.hero.x, self.hero.y = new_x, new_y
            self._move_enemies()
            self._update_interface()
            print(f"DEBUG: Hero moved to ({new_x}, {new_y})")

    def _move_enemies(self):
        """Обновляет позиции врагов только в зоне видимости"""
        # Обновляем данные о видимости перед расчетом движения
        self.vision_system.update_vision(self.hero, self.map, self.enemies, self.items)
        visible_entities = self.vision_system.get_visible_entities(
            self.hero, self.map, self.enemies, self.items
        )
        visible_enemies = visible_entities['enemies']
        
        hero_pos = (self.hero.x, self.hero.y)
        occupied = {hero_pos}

        # Собираем занятые позиции ВИДИМЫХ врагов
        for enemy in visible_enemies:
            occupied.add((enemy.x, enemy.y))

        # Перебираем всех врагов, но двигаем только видимых
        for enemy in self.enemies:
            if enemy.current_health <= 0:
                continue
                
            # Пропускаем врагов вне поля зрения
            if enemy not in visible_enemies:
                continue
                
            dx, dy = self._calculate_enemy_move(enemy, hero_pos)
            new_x = enemy.x + dx
            new_y = enemy.y + dy

            if (new_x, new_y) in self.map.walkable and (new_x, new_y) not in occupied:
                if (new_x, new_y) == hero_pos:
                    self._handle_combat(enemy)
                    break
                    
                enemy.x = new_x
                enemy.y = new_y
                occupied.add((new_x, new_y))
                
                if (enemy.x, enemy.y) == hero_pos:
                    self._handle_combat(enemy)

    def _calculate_enemy_move(self, enemy, hero_pos):
        """Рассчитывает направление движения врага к игроку"""
        hx, hy = hero_pos
        ex, ey = enemy.x, enemy.y
        
        # Определяем направление движения
        dx = 0
        if hx > ex:
            dx = 1
        elif hx < ex:
            dx = -1
            
        dy = 0
        if hy > ey:
            dy = 1
        elif hy < ey:
            dy = -1
            
        # Случайный выбор направления при равных условиях
        if random.random() < 0.5:
            return (dx, 0) if dx != 0 else (0, dy)
        else:
            return (0, dy) if dy != 0 else (dx, 0)

    def _get_enemy_at(self, x, y):
        for enemy in self.enemies:
            if enemy.x == x and enemy.y == y and enemy.current_health > 0:
                return enemy
        return None

    def _sync_health(self):
        self.health_panel.current_hp = self.hero.current_health
        print(f"DEBUG: Health synced: {self.hero.current_health}/{self.hero.max_health}")

    def _update_interface(self):
        self._sync_health()
        has_items = self.check_item_interaction()
        if self.inventory.is_open:
            self._draw_inventory()
        else:
            self._update_display()
        if self.nearby_items:
            self.interaction_panel.show_pickup_button(len(self.nearby_items))
        else:
            self.interaction_panel.hide_pickup_button()
        self._draw_panels()  # Явно перерисовываем панели
        self.renderer.screen.refresh()  # Обновляем экран
        print(f"DEBUG: Interface updated, messages in InteractionPanel: {self.interaction_panel.messages}")

    def _draw_inventory(self):
        self.interaction_panel.show_inventory(
            self.inventory.items,
            self.inventory.active_slot,
            self.inventory.equipped_weapon
        )
        self._update_display()
        print("DEBUG: Inventory drawn")

    def _handle_key_press(self, key):
        print(f"DEBUG: Key pressed: {key}")
        if self.inventory.is_open:
            if key == curses.KEY_LEFT or key == ord('a') or key == ord('A'):
                self.inventory.change_slot(-1)
            elif key == curses.KEY_RIGHT or key == ord('d') or key == ord('D'):
                self.inventory.change_slot(1)
            elif key == ord('e') or key == ord('E'):
                self.inventory.use_active_item()
            elif key == ord('r') or key == ord('R'):
                self.inventory.remove_active_item()
            elif key == ord('u') or key == ord('U'):
                self.inventory.unequip_weapon()
            elif key == ord('\t'):
                self.inventory.toggle()
            self._update_interface()
            return

        if key == ord('\t'):
            self.inventory.toggle()
        elif key == ord('f') or key == ord('F'):
            self.handle_pickup()
        elif key in (ord('w'), ord('W'), ord('a'), ord('A'), ord('s'), ord('S'), ord('d'), ord('D')):
            dx = 1 if key in (ord('d'), ord('D')) else -1 if key in (ord('a'), ord('A')) else 0
            dy = 1 if key in (ord('s'), ord('S')) else -1 if key in (ord('w'), ord('W')) else 0
            self._move_hero(dx, dy)
        elif key == ord('q') or key == ord('Q'):
            self.game_over = True

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
    
    def check_item_interaction(self):
        self.nearby_items = []
        hero_x, hero_y = self.hero.x, self.hero.y
        for item in self.items:
            x, y, item_obj = item
            if (abs(hero_x - x) <= 1 and hero_y == y) or (abs(hero_y - y) <= 1 and hero_x == x):
                self.nearby_items.append(item)
        if self.nearby_items:
            self.interaction_panel.show_pickup_button(len(self.nearby_items))
        else:
            self.interaction_panel.hide_pickup_button()
        print(f"DEBUG: Nearby items: {len(self.nearby_items)}, items: {[item[2].title for item in self.nearby_items]}")
        return len(self.nearby_items) > 0

    def handle_pickup(self):
        if not self.nearby_items:
            print("DEBUG: No nearby items to pick up")
            return
        
        picked_items = []
        for item in self.nearby_items[:]:
            x, y, item_obj = item
            if self.inventory.add_item(item_obj):
                self.items.remove(item)
                picked_items.append(item_obj.title)
        
        if picked_items:
            message = f"Подобрано: {', '.join(picked_items)}"
            self.interaction_panel.add_message(message)
            self.nearby_items.clear()
            self._update_interface()
            print(f"DEBUG: Picked up items: {picked_items}")

    def run(self):
        try:
            while not self.game_over:
                try:
                    key = self.renderer.screen.getch()
                    if key != -1:
                        self._handle_key_press(key)
                except curses.error as e:
                    print(f"DEBUG: Curses error in run: {e}")
        finally:
            self.renderer.close_screen()
            
if __name__ == "__main__":
    game = Game()
    game.run()