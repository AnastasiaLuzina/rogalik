from map import MAP_WIDTH, MAP_HEIGHT
from interface import PANEL_WIDTH
import curses

class DisplayManager:
    def __init__(self, game):
        self.game = game
        self.renderer = game.renderer
        self.map = game.map
        self.vision_system = game.vision_system
        self.hero = game.hero
        self.health_panel = game.health_panel
        self.interaction_panel = game.interaction_panel

    def draw_initial_map(self):
        if self.game.game_state != "playing":
            return
        max_y, max_x = self.renderer.screen.getmaxyx()
        if max_y < MAP_HEIGHT + 2 or max_x < MAP_WIDTH + PANEL_WIDTH:
            self.renderer.screen.clear()
            self.renderer.screen.addstr(0, 0, "Увеличьте размер терминала!", curses.color_pair(3))
            self.renderer.screen.refresh()
            return
        self.vision_system.reset()
        self.vision_system.update_vision(self.hero, self.map, self.game.enemies, self.game.items)
        visible_entities = self.vision_system.get_visible_entities(self.hero, self.map, self.game.enemies, self.game.items)
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

    def _draw_panels(self):
        self.health_panel.render(self.renderer.screen)
        self.interaction_panel.render(self.renderer.screen)

    def update_display(self):
        self.vision_system.update_vision(self.hero, self.map, self.game.enemies, self.game.items)
        visible_entities = self.vision_system.get_visible_entities(
             self.hero, self.map, self.game.enemies, self.game.items
         )
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