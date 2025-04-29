from typing import Set, Tuple, List, Dict
from map import Map
from persons import Hero, Enemy
from items import Items
import math

class VisionSystem:
    def __init__(self, vision_radius: int = 10):
        self.vision_radius = vision_radius  # Радиус обзора героя
        self.visible_tiles: Set[Tuple[int, int]] = set()  # Текущие видимые клетки
        self.explored_tiles: Set[Tuple[int, int]] = set()  # Все исследованные клетки
        self.last_hero_pos: Tuple[int, int] = (-1, -1)  # Последняя позиция героя

    def update_vision(self, hero: Hero, map: Map, enemies: List[Enemy], items: List[Tuple[int, int, Items]]) -> Dict[str, Set[Tuple[int, int]]]:
        self.visible_tiles.clear()  # Очистка текущих видимых клеток
        hero_x, hero_y = hero.x, hero.y  # Координаты героя
        
        # Перебор клеток в радиусе обзора
        for y in range(max(0, hero_y - self.vision_radius), min(map.height, hero_y + self.vision_radius + 1)):
            for x in range(max(0, hero_x - self.vision_radius), min(map.width, hero_x + self.vision_radius + 1)):
                if self._is_visible(hero_x, hero_y, x, y, map):  # Проверка видимости клетки
                    self.visible_tiles.add((x, y))  # Добавление видимой клетки
                    self.explored_tiles.add((x, y))  # Добавление в исследованные
        
        self.last_hero_pos = (hero_x, hero_y)  # Сохранение позиции героя

        # Возврат копий множеств видимых и исследованных клеток
        return {
            'visible_tiles': self.visible_tiles.copy(),
            'explored_tiles': self.explored_tiles.copy()
        }

    def _is_visible(self, x0: int, y0: int, x1: int, y1: int, map: Map) -> bool:
        # Проверка, входит ли клетка в радиус обзора
        if math.hypot(x1 - x0, y1 - y0) > self.vision_radius:
            return False
        
        # Инициализация для алгоритма Брезенхэма
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        x, y = x0, y0
        sx = 1 if x0 < x1 else -1  # Направление по X
        sy = 1 if y0 < y1 else -1  # Направление по Y
        err = dx - dy  # Начальная ошибка

        while True:
            # Проверка выхода за границы карты
            if not (0 <= x < map.width and 0 <= y < map.height):
                return False

            # Проверка стены (кроме целевой клетки)
            if (x != x1 or y != y1) and map.tiles[y][x] == map.wall_char:
                return False
            
            # Достигнута целевая клетка
            if x == x1 and y == y1:
                return True

            # Выбор следующей клетки по алгоритму Брезенхэма
            e2 = 2 * err
            if e2 > -dy:  # Движение по X
                err -= dy
                x += sx
            if e2 < dx:  # Движение по Y
                err += dx
                y += sy

    def get_visible_entities(self, hero: Hero, map: Map, enemies: List[Enemy], items: List[Tuple[int, int, Items]]) -> Dict[str, List]:
        # Фильтрация видимых врагов (живых и в видимых клетках)
        visible_enemies = [e for e in enemies 
                          if (e.x, e.y) in self.visible_tiles 
                          and e.current_health > 0]

        # Фильтрация видимых предметов
        visible_items = [item for item in items 
                        if (item[0], item[1]) in self.visible_tiles]

        # Возврат списков видимых врагов и предметов
        return {
            'enemies': visible_enemies,
            'items': visible_items
        }

    def is_visible(self, x: int, y: int) -> bool:
        # Проверка, видима ли клетка сейчас
        return (x, y) in self.visible_tiles

    def is_explored(self, x: int, y: int) -> bool:
        # Проверка, была ли клетка исследована
        return (x, y) in self.explored_tiles