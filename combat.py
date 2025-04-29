import time
import random
import curses
from items import Sword, Bow, IceStaff, HealthPotion, PoisonPotion, Weapon
from colorama import Fore

class CombatSystem:
    def __init__(self, game, enemy, screen):
        self.game = game
        self.enemy = enemy
        self.screen = screen
        self.in_combat = True
        self.combat_log = []
        self.defense_bonus = 0
        self.victory_delay = 2
        self.max_log_lines = 4  
        self.enemy_frozen_turns = 0
        self.poison_effect = {'damage': 0, 'turns': 0}
        self._enter_combat()

    def _enter_combat(self):
        self.screen.clear()
        self.draw_combat_screen()

    def _exit_combat(self):
        self.in_combat = False
        self.screen.clear()
        self.game.vision_system.update_vision(self.game.hero, self.game.map, [], self.game.items)
        self.game.renderer.render_map(
            self.game.map,
            self.game.hero,  
            [],
            self.game.items,
            self.game.vision_system,
            force_redraw=True
        )
        self.game._draw_panels()
        self.screen.refresh()

    def draw_combat_screen(self):
        self.screen.clear()
        max_y, max_x = self.screen.getmaxyx()
        if max_y < 16 or max_x < 50:
            self.screen.addstr(0, 0, "Увеличьте терминал!", curses.color_pair(3))
            self.screen.refresh()
            return
        
        try:
            hero_hp = f"Герой: HP {self.game.hero.current_health}/{self.game.hero.max_health}"[:max_x-2]
            enemy_hp = f"{self.enemy.title}: HP {self.enemy.current_health}/{self.enemy.max_health}"[:max_x-2]
            separator = "═" * min(30, max_x-2)
            action_prompt = "Выберите действие (1-3): "[:max_x-2]

            self.screen.addstr(0, 0, hero_hp, curses.color_pair(5))
            self.screen.addstr(1, 0, enemy_hp, curses.color_pair(3))
            self.screen.addstr(2, 0, separator, curses.color_pair(2))
            self.screen.addstr(3, 0, "1. Атаковать", curses.color_pair(5))
            self.screen.addstr(4, 0, "2. Использовать предмет", curses.color_pair(5))
            self.screen.addstr(5, 0, "3. Попытаться убежать", curses.color_pair(5))
            self.screen.addstr(6, 0, separator, curses.color_pair(2))
            
            for i, message in enumerate(self.combat_log[-self.max_log_lines:]):
                if 8 + i < max_y:
                    self.screen.addstr(8 + i, 0, message[:max_x-2], curses.color_pair(5))

            
            if self.enemy_frozen_turns > 0:
                self.screen.addstr(7, 0, f"Противник заморожен: {self.enemy_frozen_turns} ходов"[:max_x-2], curses.color_pair(3))
            
            if 14 < max_y and self.in_combat:
                self.screen.addstr(min(14, max_y-1), 0, action_prompt, curses.color_pair(2))
            
            self.screen.refresh()
        except curses.error as e:
            print(f"DEBUG: Curses error in draw_combat_screen: {e}")

    def process_input(self, key):
        if key in ('1', '2', '3'):
            if key == '1':
                self.player_attack()
            elif key == '2':
                self.use_item()
            elif key == '3':
                self.try_escape()
            return True
        return False

    def add_log_message(self, message):
        max_y, max_x = self.screen.getmaxyx()
        message = message[:max_x-2]
        self.combat_log.append(message)
        self.draw_combat_screen()

    def calculate_damage(self, base_damage, variation=0.3):
        min_dmg = max(1, int(base_damage * (1 - variation)))
        max_dmg = int(base_damage * (1 + variation))
        return random.randint(min_dmg, max_dmg)

    def apply_poison_damage(self):
        if self.poison_effect['turns'] > 0:
            poison_damage = self.poison_effect['damage']
            self.enemy.current_health -= poison_damage
            self.poison_effect['turns'] -= 1
            self.add_log_message(f"{self.enemy.title} получил {poison_damage} урона от яда! Осталось {self.poison_effect['turns']} ходов.")

    def player_attack(self):
        time.sleep(0.2)
        weapon = self.game.hero.inventory.equipped_weapon
        damage = 5 
        freeze_duration = 0
        attack_message = f"Вы нанесли {damage} урона кулаком!"

        if weapon:
            result = weapon.use(self.game.hero.inventory)
            if isinstance(weapon, IceStaff):
                base_damage, freeze_duration = result
                damage = self.calculate_damage(base_damage)
                attack_message = f"Вы нанесли {damage} урона (Ледяной посох)"
                if freeze_duration > 0:
                    attack_message += " Противник заморожен!"
            elif isinstance(weapon, Sword) and result == weapon.damage * 2:
                base_damage = result
                damage = self.calculate_damage(base_damage)
                attack_message = f"Вы нанесли двойной удар {damage} урона (Меч)!"
            elif isinstance(weapon, Bow) and result == int(weapon.damage * 1.5):
                base_damage = result
                damage = self.calculate_damage(base_damage)
                attack_message = f"Вы нанесли точный выстрел {damage} урона (Лук)!"
            else:
                base_damage = result
                damage = self.calculate_damage(base_damage)
                attack_message = f"Вы нанесли {damage} урона ({weapon.title})!"
        else:
            damage = self.calculate_damage(damage)

        print(f"DEBUG: Preparing to log attack message: {attack_message}")
        self.enemy.current_health -= damage
        self.add_log_message(attack_message)
        print(f"DEBUG: Player attacked {self.enemy.title}, dealt {damage} damage")

        if freeze_duration > 0:
            self.enemy_frozen_turns = freeze_duration
            self.add_log_message(f"{self.enemy.title} заморожен на {freeze_duration} хода!")

        if self.enemy.current_health <= 0:
            self.victory_sequence()
        else:
            time.sleep(0.5)
            self.enemy_turn()

    def enemy_turn(self):
        if not self.in_combat or self.enemy.current_health <= 0:
            return

        self.apply_poison_damage()

        if self.enemy.current_health <= 0:
            self.victory_sequence()
            return

        if self.enemy_frozen_turns > 0:
            self.enemy_frozen_turns -= 1
            self.add_log_message(f"{self.enemy.title} заморожен, осталось {self.enemy_frozen_turns} ходов.")
            print(f"DEBUG: Enemy is frozen, {self.enemy_frozen_turns} turns left")
            self.draw_combat_screen()
            return

        damage = self.enemy.attack()
        self.game.hero.current_health -= damage
        self.add_log_message(f"{self.enemy.title} атаковал вас и нанес {damage} урона!")
        self.game._sync_health()
        
        if self.game.hero.current_health <= 0:
            self.add_log_message("Вы погибли!")
            self.game.game_over = True
            self.in_combat = False

    def try_escape(self):
        if random.random() < 0.5:
            escape_message = f"✔ Вы сбежали от {self.enemy.title}!"
            self.add_log_message(escape_message)
            self.game.interaction_panel.add_message(escape_message)
            self.in_combat = False
            self._exit_combat()
        else:
            self.add_log_message(f"✖ Вам не удалось сбежать!")
            time.sleep(0.5)
            self.enemy_turn()
    def use_item(self):
        items = list(self.game.hero.inventory.items.values())
        if not items:
            self.add_log_message("В инвентаре нет предметов!")
            return
        
        self.screen.clear()
        max_y, max_x = self.screen.getmaxyx()
        try:
            self.screen.addstr(0, 0, "Выберите предмет:"[:max_x-2], curses.color_pair(2))
            for i, item in enumerate(items, 1):
                equipped = " [Э]" if item == self.game.hero.inventory.equipped_weapon else ""
                item_text = f"{i}. {item.title}{equipped}"[:max_x-2]
                if i < max_y:
                    self.screen.addstr(i, 0, item_text, curses.color_pair(5))
            if len(items) + 2 < max_y:
                self.screen.addstr(len(items) + 2, 0, "Нажмите цифру или другую клавишу для отмены"[:max_x-2], curses.color_pair(2))
            self.screen.refresh()
        except curses.error as e:
            print(f"DEBUG: Curses error in use_item: {e}")

        while True:
            key = self.screen.getch()
            if key != -1:
                break
        
        self.draw_combat_screen()
        
        key = chr(key) if 0 <= key <= 255 else None
        if key and key.isdigit() and 0 < int(key) <= len(items):
            item = items[int(key)-1]
            if isinstance(item, HealthPotion):
                heal = item.use(self.game.hero, self.game.hero.inventory)
                self.game._sync_health()
                heal_message = f"Использовано зелье здоровья: +{heal} HP"
                self.add_log_message(heal_message)
                self.game.interaction_panel.add_message(heal_message)
                item._break_and_remove(self.game.hero.inventory, suppress_update=True)  # <-- исправлено
                time.sleep(0.5)
                self.enemy_turn()
            elif isinstance(item, PoisonPotion):
                initial_damage, poison_damage, duration = item.use(self.enemy, self.game.hero.inventory)
                self.poison_effect = {'damage': poison_damage, 'turns': duration}
                poison_message = f"Использовано ядовитое зелье: {poison_damage} урона/ход на {duration} хода"
                self.add_log_message(poison_message)
                self.game.interaction_panel.add_message(poison_message)

                item._break_and_remove(self.game.hero.inventory, suppress_update=True)  # <-- исправлено
                time.sleep(0.5)
                self.enemy_turn()
            elif isinstance(item, Weapon):
                self.game.hero.inventory.equip_weapon(item)
                equip_message = f"Экипировано: {item.title}"
                self.add_log_message(equip_message)
                self.game.interaction_panel.add_message(equip_message)
            else:
                self.add_log_message("Этот предмет нельзя использовать сейчас!")
        else:
            self.add_log_message("Отмена выбора предмета!")

    def victory_sequence(self):
        victory_message = f"Вы победили {self.enemy.title}!"
        self.add_log_message(victory_message)
        self.game.interaction_panel.add_message(victory_message)
        
        if self.enemy in self.game.enemies:
            self.game.enemies.remove(self.enemy)
        
        self.game.update_killed_counter()
        
        max_y, max_x = self.screen.getmaxyx()
        for i in range(self.victory_delay, 0, -1):
            countdown_msg = f"Возвращение через {i}..."
            self.add_log_message(countdown_msg)
            self.screen.refresh()
            time.sleep(1)
        
        self._exit_combat()