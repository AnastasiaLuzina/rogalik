import curses
from map import Map
from persons import Hero
from items import Items

class Renderer:
    def __init__(self):
        self.screen = None
        self.color_pairs = {}
        self.last_positions = {}  # Для отслеживания изменений

    def init_colors(self):
        curses.start_color()
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_BLACK)   # Стены
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)   # Герой
        curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)     # Враги
        curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)   # Предметы
        curses.init_pair(5, curses.COLOR_CYAN, curses.COLOR_BLACK)    # Интерфейс

    def init_screen(self):
        self.screen = curses.initscr()
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
        if map and x < len(map.tiles) and y < len(map.tiles[0]) and map.tiles[y][x] == map.wall_char:
            return 'wall'
        return 'empty'

    def render_map(self, map: Map, hero: Hero, enemies: list, items: list, force_redraw: bool = False) -> None:
        if not self.screen:
            self.init_screen()

        for y in range(map.height):
            for x in range(map.width):
                if force_redraw or self.is_cell_changed(x, y, hero, enemies, items):
                    self.draw_cell(map, x, y, hero, enemies, items)

        inventory_button = "[I] Инвентарь"
        self.screen.addstr(map.height, 0, inventory_button, curses.color_pair(5))
        self.screen.refresh()

    def draw_cell(self, map: Map, x: int, y: int, hero: Hero, enemies: list, items: list) -> None:
        if not self.screen:
            return

        if x == hero.x and y == hero.y:
            self.screen.addch(y, x, ord(hero.char), curses.color_pair(2))
        else:
            for enemy in enemies:
                if enemy.x == x and enemy.y == y and enemy.current_health > 0:
                    self.screen.addch(y, x, ord(enemy.char), curses.color_pair(3))
                    return
            for item_x, item_y, item in items:
                if item_x == x and item_y == y:
                    self.screen.addch(y, x, ord(item.symbol), curses.color_pair(4))
                    return
            if map.tiles[y][x] == map.wall_char:
                self.screen.addch(y, x, map.wall_char, curses.color_pair(1))
            else:
                self.screen.addch(y, x, ord(' '))
        self.screen.refresh()