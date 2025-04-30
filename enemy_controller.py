import random
from combat import CombatSystem
import curses

class EnemyController:
    def __init__(self, game):
        self.game = game

    def move_enemies(self):
        self.game.vision_system.update_vision(self.game.hero, self.game.map, self.game.enemies, self.game.items)
        visible_entities = self.game.vision_system.get_visible_entities(
            self.game.hero, self.game.map, self.game.enemies, self.game.items
        )
        visible_enemies = visible_entities['enemies']
        hero_pos = (self.game.hero.x, self.game.hero.y)
        occupied = {hero_pos}
        for enemy in visible_enemies:
            occupied.add((enemy.x, enemy.y))
        for enemy in self.game.enemies:
            if enemy.current_health <= 0:
                continue
            if enemy not in visible_enemies:
                continue
            dx, dy = self._calculate_enemy_move(enemy, hero_pos)
            new_x = enemy.x + dx
            new_y = enemy.y + dy
            if (new_x, new_y) in self.game.map.walkable and (new_x, new_y) not in occupied:
                if (new_x, new_y) == hero_pos:
                    self.handle_combat(enemy)
                    break
                enemy.x = new_x
                enemy.y = new_y
                occupied.add((new_x, new_y))
                if (enemy.x, enemy.y) == hero_pos:
                    self.handle_combat(enemy)

    def _calculate_enemy_move(self, enemy, hero_pos):
        hx, hy = hero_pos
        ex, ey = enemy.x, enemy.y
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
        if random.random() < 0.5:
            return (dx, 0) if dx != 0 else (0, dy)
        else:
            return (0, dy) if dy != 0 else (dx, 0)

    def get_enemy_at(self, x, y):
        for enemy in self.game.enemies:
            if enemy.x == x and enemy.y == y and enemy.current_health > 0:
                return enemy
        return None

    def handle_combat(self, enemy):

        combat = CombatSystem(self.game, enemy, self.game.renderer.screen)
        while combat.in_combat and not self.game.game_over:
            try:
                key = self.game.renderer.screen.getch()
                if key != -1:
                    combat.process_input(chr(key).lower())
            except curses.error:
                pass
        self.game.display_manager.update_display()
        self.game.messages = []