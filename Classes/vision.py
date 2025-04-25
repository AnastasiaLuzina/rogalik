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
        Updates visible and explored tiles based on hero's position.
        """
        self.visible_tiles.clear()
        hero_pos = (hero.x, hero.y)

        for y in range(max(0, hero.y - self.vision_radius), min(map.height, hero.y + self.vision_radius + 1)):
            for x in range(max(0, hero.x - self.vision_radius), min(map.width, hero.x + self.vision_radius + 1)):
                if self._is_visible(hero.x, hero.y, x, y, map):
                    self.visible_tiles.add((x, y))
                    self.explored_tiles.add((x, y))

        self.last_hero_pos = hero_pos
        print(f"Visible tiles: {len(self.visible_tiles)}, Explored tiles: {len(self.explored_tiles)}")
        return {
            'visible_tiles': self.visible_tiles,
            'explored_tiles': self.explored_tiles
        }

    def _is_visible(self, x0: int, y0: int, x1: int, y1: int, map: Map) -> bool:
        """
        Checks if tile (x1, y1) is visible from (x0, y0) considering walls.
        Uses Bresenham's line algorithm for line-of-sight.
        """
        # Check distance
        distance = math.sqrt((x1 - x0) ** 2 + (y1 - y0) ** 2)
        if distance > self.vision_radius:
            return False

        # Bresenham's line algorithm
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        x, y = x0, y0
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy

        while True:
            # If we reached the target tile, it's visible
            if x == x1 and y == y1:
                return True

            # Check if current tile is a wall (but not the target tile)
            if 0 <= y < map.height and 0 <= x < map.width and map.tiles[y][x] == map.wall_char and (x != x1 or y != y1):
                return False

            # Move to next tile
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

            # Check bounds
            if x < 0 or x >= map.width or y < 0 or y >= map.height:
                return False

    def get_visible_entities(self, hero: Hero, map: Map, enemies: List[Enemy], items: List[Tuple[int, int, Items]]) -> Dict[str, List]:
        """
        Returns lists of visible enemies and items.
        """
        visible_enemies = []
        visible_items = []

        for enemy in enemies:
            if (enemy.x, enemy.y) in self.visible_tiles and enemy.current_health > 0:
                visible_enemies.append(enemy)

        for x, y, item in items:
            if (x, y) in self.visible_tiles:
                visible_items.append((x, y, item))

        print(f"Visible enemies: {len(visible_enemies)}, Visible items: {len(visible_items)}")
        return {
            'enemies': visible_enemies,
            'items': visible_items
        }

    def is_visible(self, x: int, y: int) -> bool:
        return (x, y) in self.visible_tiles

    def is_explored(self, x: int, y: int) -> bool:
        return (x, y) in self.explored_tiles