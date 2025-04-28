from typing import Set, Tuple, List, Dict
from map import Map
from persons import Hero, Enemy
from items import Items
import math

class VisionSystem:
    def __init__(self, vision_radius: int = 10):
        self.vision_radius = vision_radius
        self.visible_tiles: Set[Tuple[int, int]] = set()
        self.explored_tiles: Set[Tuple[int, int]] = set()
        self.last_hero_pos: Tuple[int, int] = (-1, -1)

    def update_vision(self, hero: Hero, map: Map, enemies: List[Enemy], items: List[Tuple[int, int, Items]]) -> Dict[str, Set[Tuple[int, int]]]:
        """
        Обновляет видимые и исследованные тайлы на основе позиции героя.
        """
        self.visible_tiles.clear()
        hero_x, hero_y = hero.x, hero.y

        # Пересчет видимых тайлов в радиусе зрения
        for y in range(max(0, hero_y - self.vision_radius), min(map.height, hero_y + self.vision_radius + 1)):
            for x in range(max(0, hero_x - self.vision_radius), min(map.width, hero_x + self.vision_radius + 1)):
                if self._is_visible(hero_x, hero_y, x, y, map):
                    self.visible_tiles.add((x, y))
                    self.explored_tiles.add((x, y))  # Тайлы остаются исследованными

        self.last_hero_pos = (hero_x, hero_y)
        return {
            'visible_tiles': self.visible_tiles.copy(),
            'explored_tiles': self.explored_tiles.copy()
        }

    def _is_visible(self, x0: int, y0: int, x1: int, y1: int, map: Map) -> bool:
        """
        Проверяет видимость тайла (x1,y1) из (x0,y0) с учетом препятствий.
        Использует оптимизированный алгоритм Брезенхэма.
        """
        # Проверка радиуса видимости
        if math.hypot(x1 - x0, y1 - y0) > self.vision_radius:
            return False

        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        x, y = x0, y0
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy

        while True:
            # Проверка границ карты
            if not (0 <= x < map.width and 0 <= y < map.height):
                return False

            # Проверка препятствий (кроме целевого тайла)
            if (x != x1 or y != y1) and map.tiles[y][x] == map.wall_char:
                return False

            # Успешное завершение при достижении цели
            if x == x1 and y == y1:
                return True

            # Расчет следующего тайла
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

    def get_visible_entities(self, hero: Hero, map: Map, enemies: List[Enemy], items: List[Tuple[int, int, Items]]) -> Dict[str, List]:
        """
        Возвращает видимых сущностей и предметы.
        """
        # Фильтрация врагов в зоне видимости
        visible_enemies = [e for e in enemies 
                          if (e.x, e.y) in self.visible_tiles 
                          and e.current_health > 0]

        # Фильтрация предметов в зоне видимости
        visible_items = [item for item in items 
                        if (item[0], item[1]) in self.visible_tiles]

        return {
            'enemies': visible_enemies,
            'items': visible_items
        }

    def is_visible(self, x: int, y: int) -> bool:
        return (x, y) in self.visible_tiles

    def is_explored(self, x: int, y: int) -> bool:
        return (x, y) in self.explored_tiles