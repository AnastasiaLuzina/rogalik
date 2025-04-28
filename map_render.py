import curses
from map import Map
from persons import Hero
from items import Items

class Renderer:
    def __init__(self):
        self.screen = None
        self.color_pairs = {}
        self.last_positions = {}
        

    def init_colors(self):
        curses.start_color()
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_BLACK)   # Wall
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)   # Hero/Empty
        curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)     # Enemy
        curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)   # Item
        curses.init_pair(5, curses.COLOR_CYAN, curses.COLOR_BLACK)    # UI
        curses.init_pair(6, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # Для активного слота

    def init_screen(self):
        self.screen = curses.initscr()
        self.screen.keypad(True)
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        self.screen.keypad(True)
        self.screen.nodelay(True)
        self.init_colors()

    def close_screen(self):
        if self.screen:
            curses.nocbreak()
            self.screen.keypad(False)
            curses.echo()
            curses.endwin()

    def is_cell_changed(self, x: int, y: int, hero: Hero, enemies: list, items: list) -> bool:
        key = (x, y)
        current_state = self._get_cell_state(x, y, hero, enemies, items)
        if key not in self.last_positions or self.last_positions[key] != current_state:
            self.last_positions[key] = current_state
            return True
        return False

    def _get_cell_state(self, x: int, y: int, hero: Hero, enemies: list, items: list, map: Map = None) -> str:
        if x == hero.x and y == hero.y:
            return 'hero'
        for enemy in enemies:
            if enemy.x == x and enemy.y == y and enemy.current_health > 0:
                return 'enemy'
        for item_x, item_y, item in items:
            if item_x == x and item_y == y:
                return 'item'
        if map and 0 <= x < map.width and 0 <= y < map.height and map.tiles[y][x] == map.wall_char:
            return 'wall'
        return 'empty'

    def render_map(self, map: Map, hero: Hero, enemies: list, items: list, vision_system=None, force_redraw: bool = False) -> None:
        if not self.screen:
            self.init_screen()

        # Debug: print visible entities count
        visible_entities = vision_system.get_visible_entities(hero, map, enemies, items) if vision_system else {'enemies': enemies, 'items': items}
        print(f"Rendering: {len(visible_entities['enemies'])} enemies, {len(visible_entities['items'])} items")

        for y in range(map.height):
            for x in range(map.width):
                # Skip tiles that are neither visible nor explored
                if vision_system and not (vision_system.is_visible(x, y) or vision_system.is_explored(x, y)):
                    self.screen.addch(y, x, ord(' '))  # Clear non-visible/non-explored tiles
                    continue

                if force_redraw or self.is_cell_changed(x, y, hero, enemies, items):
                    self.draw_cell(map, x, y, hero, enemies, items, vision_system)

        # Draw inventory button
        inventory_button = "[Tab] Инвентарь"
        self.screen.addstr(map.height, 0, inventory_button, curses.color_pair(5))
        self.screen.refresh()

    def draw_cell(self, map: Map, x: int, y: int, hero: Hero, enemies: list, items: list, vision_system=None) -> None:
        if not self.screen:
            return

        is_visible = vision_system.is_visible(x, y) if vision_system else True
        color = curses.color_pair(2) if is_visible else curses.color_pair(2) | curses.A_DIM

        if x == hero.x and y == hero.y:
            self.screen.addch(y, x, ord(hero.char), curses.color_pair(2))
        else:
            for enemy in enemies:
                if enemy.x == x and enemy.y == y and enemy.current_health > 0 and is_visible:
                    self.screen.addch(y, x, ord(enemy.char), curses.color_pair(3))
                    return
            for item_x, item_y, item in items:
                if item_x == x and item_y == y and is_visible:
                    self.screen.addch(y, x, ord(item.symbol), curses.color_pair(4))
                    return
            if 0 <= y < map.height and 0 <= x < map.width and map.tiles[y][x] == map.wall_char:
                self.screen.addch(y, x, ord(map.wall_char), color)
            else:
                self.screen.addch(y, x, ord(' '), color)