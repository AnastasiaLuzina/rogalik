import time
import random
import curses
from items import Sword, Bow, IceStaff, Shield, HealthPotion
from colorama import Fore 
class CombatSystem:
    def __init__(self, game, enemy, screen):
        self.game = game
        self.enemy = enemy
        self.screen = screen  # Экран curses из Renderer
        self.in_combat = True
        self.combat_log = []
        self.defense_bonus = 0
        self.victory_delay = 2
        self.max_log_lines = 5
        self._enter_combat()

    def _enter_combat(self):
        """Очищает экран и переключает на боевой интерфейс"""
        self.screen.clear()
        self.draw_combat_screen()

    def _exit_combat(self):
        """Возвращает игрока на карту после боя"""
        self.in_combat = False
        self.screen.clear()
        self.game.renderer.last_positions.clear()
        self.game._sync_health()
        self.game._update_interface()  # Обновляем интерфейс для отображения сообщений
        self.game.renderer.render_map(self.game.map, self.game.hero, self.game.enemies, self.game.items, force_redraw=True)
        self.game._draw_panels()
        self.screen.refresh()

    def draw_combat_screen(self):
        """Отрисовывает боевой интерфейс"""
        self.screen.clear()

        # Статус героя и врага
        self.screen.addstr(0, 0, f"Герой: HP {self.game.hero.current_health}/{self.game.hero.max_health}", curses.color_pair(5))
        self.screen.addstr(1, 0, f"{self.enemy.char}: HP {self.enemy.current_health}/{self.enemy.max_health}", curses.color_pair(3))
        self.screen.addstr(2, 0, "═"*30, curses.color_pair(2))

        # Меню действий
        self.screen.addstr(3, 0, "1. Атаковать", curses.color_pair(5))
        self.screen.addstr(4, 0, "2. Использовать предмет", curses.color_pair(5))
        self.screen.addstr(5, 0, "3. Защищаться", curses.color_pair(5))
        self.screen.addstr(6, 0, "4. Попытаться убежать", curses.color_pair(5))
        self.screen.addstr(7, 0, "═"*30, curses.color_pair(2))

        # Лог боя
        for i, message in enumerate(self.combat_log[-self.max_log_lines:]):
            self.screen.addstr(8 + i, 0, message[:50], curses.color_pair(5))  # Ограничиваем длину сообщения

        # Приглашение к вводу
        self.screen.addstr(14, 0, "Выберите действие (1-4): ", curses.color_pair(2))
        self.screen.refresh()

    def add_log_message(self, message):
        """Добавляет сообщение в лог боя"""
        self.combat_log.append(message)
        self.draw_combat_screen()
        time.sleep(0.3)

    def calculate_damage(self, base_damage, variation=0.3):
        """Вычисляет случайный урон в заданном диапазоне"""
        min_dmg = max(1, int(base_damage * (1 - variation)))
        max_dmg = int(base_damage * (1 + variation))
        return random.randint(min_dmg, max_dmg)

    def process_input(self, key):
        """Обрабатывает ввод пользователя"""
        if key in ('1', '2', '3', '4'):
            if key == '1':
                self.player_attack()
            elif key == '2':
                self.use_item()
            elif key == '3':
                self.player_defend()
            elif key == '4':
                self.try_escape()
            return True
        return False

    def player_attack(self):
        """Обрабатывает атаку игрока"""
        time.sleep(0.2)
        
        weapon = None
        base_damage = 5
        
        # Поиск оружия в инвентаре
        for item in self.game.hero.inventory.items.values():
            if isinstance(item, (Sword, Bow, IceStaff)):
                weapon = item
                base_damage = item.damage
                break
            
        damage = self.calculate_damage(base_damage)
        
        if weapon:
            msg = f"Вы атаковали {self.enemy.char} ({weapon.title}) и нанесли {damage} урона!"
            weapon.use(self.game.hero.inventory)
        else:
            msg = f"Вы ударили {self.enemy.char} кулаком и нанесли {damage} урона!"
        
        self.add_log_message(msg)
        self.enemy.current_health -= damage
        
        if self.enemy.current_health <= 0:
            self.victory_sequence()
        else:
            time.sleep(0.5)
            self.enemy_turn()

    def enemy_turn(self):
        """Обрабатывает ход врага"""
        if not self.in_combat or self.enemy.current_health <= 0:
            return
        
        damage = self.calculate_damage(self.enemy.damage)
        actual_damage = max(1, damage - self.defense_bonus)
        self.game.hero.current_health -= actual_damage
        self.defense_bonus = 0
        
        msg = f"{self.enemy.char} атаковал вас и нанес {actual_damage} урона!"
        if damage != actual_damage:
            msg += f" (Заблокировано {damage - actual_damage})"
        
        self.add_log_message(msg)
        
        # Синхронизируем здоровье
        self.game._sync_health()
        
        if self.game.hero.current_health <= 0:
            self.add_log_message("☠️ Вы погибли! ☠️")
            self.game.game_over = True
            self.in_combat = False

    def player_defend(self):
        """Обрабатывает защиту игрока"""
        shield = None
        for item in self.game.hero.inventory.items.values():
            if isinstance(item, Shield):
                shield = item
                break
        
        if shield:
            self.defense_bonus = shield.save_from_damage
            msg = f"Вы подняли {shield.title} для защиты!"
        else:
            self.defense_bonus = 3
            msg = f"Вы приготовились к защите!"
        
        self.add_log_message(msg)
        time.sleep(0.5)
        self.enemy_turn()

    def try_escape(self):
        """Попытка убежать от врага"""
        if random.random() < 0.5:
            escape_message = f"✔ Вы сбежали от {self.enemy.char}!"
            self.add_log_message(escape_message)
            self.game.interaction_panel.add_message(escape_message) 
            self.in_combat = False
            self._exit_combat()
        else:
            self.add_log_message(f"✖ Вам не удалось сбежать!")
            time.sleep(0.5)
            self.enemy_turn()
    def use_item(self):
        """Использование предмета из инвентаря"""
        items = list(self.game.hero.inventory.items.values())
        if not items:
            self.add_log_message("В инвентаре нет предметов!")
            return
        
        # Отрисовка меню предметов
        self.screen.clear()
        self.screen.addstr(0, 0, "Выберите предмет:", curses.color_pair(2))
        for i, item in enumerate(items, 1):
            self.screen.addstr(i, 0, f"{i}. {item.title}", curses.color_pair(5))
        self.screen.addstr(len(items) + 2, 0, "Нажмите цифру или другую клавишу для отмены", curses.color_pair(2))
        self.screen.refresh()

        # Получение ввода
        while True:
            key = self.screen.getch()
            if key != -1:
                break
        
        # Возвращаем боевой экран
        self.draw_combat_screen()
        
        key = chr(key) if 0 <= key <= 255 else None
        if key and key.isdigit() and 0 < int(key) <= len(items):
            item = items[int(key)-1]
            if isinstance(item, HealthPotion):
                heal = item.use(self.game.hero, self.game.hero.inventory)
                self.game._sync_health()  # Синхронизируем здоровье
                self.add_log_message(f"Вы использовали {item.title} и восстановили {heal} HP!")
                time.sleep(0.5)
                self.enemy_turn()
            else:
                self.add_log_message("Этот предмет нельзя использовать сейчас!")
        else:
            self.add_log_message("Отмена выбора предмета!")
            
    def victory_sequence(self):
        """Обрабатывает победу над врагом"""
        victory_message = f"⚔️ Вы победили {self.enemy.char}!"
        self.add_log_message(victory_message)
        self.game.interaction_panel.add_message(victory_message)
        
        # Увеличиваем счетчик убитых врагов
        self.game.update_killed_counter()  # Новая строка
        
        for i in range(self.victory_delay, 0, -1):
            self.add_log_message(f"Возвращение через {i}...")
            time.sleep(1)
        
        self.in_combat = False
        if self.enemy in self.game.enemies:
            self.game.enemies.remove(self.enemy)
        
        self._exit_combat()