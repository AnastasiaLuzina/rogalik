import curses
from map import Map, MAP_WIDTH, MAP_HEIGHT
from persons import Hero
from interface import HealthPanel, InteractionPanel, PANEL_WIDTH, HEALTH_HEIGHT, INTERACTION_HEIGHT
from map_render import Renderer
from display import DisplayManager
from combat import CombatSystem
from vision import VisionSystem
from updater import Updater
from inventory import Inventory
from player_controller import PlayerController
from enemy_controller import EnemyController
from entity_placement import EntityPlacer
from colorama import init
from input_handler import InputHandler
from screen_manager import ScreenManager  

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
        self.killed_enemies = 0
        self.total_enemies = 0
        self.nearby_items = []
        self.game_state = "start"
        self.health_panel = HealthPanel(
            x=MAP_WIDTH + 1, y=1,
            width=PANEL_WIDTH, height=HEALTH_HEIGHT,
            current_hp=self.hero.current_health,
            max_hp=self.hero.max_health,
            game=self,
            killed_enemies=self.killed_enemies,
            total_enemies=self.total_enemies
        )
        self.interaction_panel = InteractionPanel(
            x=MAP_WIDTH + 1, y=HEALTH_HEIGHT + 1,
            width=PANEL_WIDTH, height=INTERACTION_HEIGHT
        )
        self.screen_manager = ScreenManager(self, self.renderer.screen)

        self.display_manager = DisplayManager(self)
        self.updater = Updater(self)
        self.player_controller = PlayerController(self)
        self.enemy_controller = EnemyController(self)
        self.entity_placer = EntityPlacer(self)
        self.combat_system = CombatSystem
        self.input_handler = InputHandler(self)

        self.entity_placer.place_hero_and_entities()
        self.display_manager.draw_initial_map()

    def play_game(self):
        self.game_over = False
        while not self.game_over:
            try:
                key = self.renderer.screen.getch()
                if key != -1:
                    self.input_handler.handle_key_press(key)
                if self.killed_enemies >= self.total_enemies and self.total_enemies > 0:
                    self.game_state = "win"
                    self.display_manager.update_display()
                    break
            except curses.error:
                pass
        if self.game_state == "win":
            self.screen_manager.show_win_screen()
        else:
            self.game_state = "death"

    def reset_game(self):
        renderer = self.renderer
        screen = renderer.screen
        self.__init__()
        self.renderer = renderer
        self.renderer.screen = screen
        self.screen_manager = ScreenManager(self, screen) 
        self.game_state = "playing"
        self.entity_placer.place_hero_and_entities()
        self.vision_system.update_vision(self.hero, self.map, self.enemies, self.items)
        self.display_manager.draw_initial_map()
        self.updater._update_interface()

    def run(self):
        try:
            while True:
                if self.game_state == "start":
                    self.screen_manager.show_start_screen()
                elif self.game_state == "playing":
                    self.play_game()
                elif self.game_state == "death":
                    self.screen_manager.show_death_screen()
                elif self.game_state == "win":
                    self.screen_manager.show_win_screen()
        finally:
            self.renderer.close_screen()

if __name__ == "__main__":
    game = Game()
    game.run()