from interface import StartScreen, DeathScreen, WinScreen

class ScreenManager:
    def __init__(self, game, screen):
        self.game = game
        self.screen = screen
        self.start_screen = StartScreen(screen)
        self.death_screen = DeathScreen(screen)
        self.win_screen = WinScreen(screen)

    def show_start_screen(self):
        self.start_screen.show()
        while True:
            key = self.screen.getch()
            if key == ord('s') or key == ord('S'):
                self.game.game_state = "playing"
                self.game.vision_system.reset()
                self.game.entity_placer.place_hero_and_entities()
                self.game.display_manager.draw_initial_map()
                break
            elif key == ord('q') or key == ord('Q'):
                exit()

    def show_death_screen(self):
        self.death_screen.show()
        self.screen.refresh()
        while True:
            key = self.screen.getch()
            if key == ord('r') or key == ord('R'):
                self.game.reset_game()
                self.game.game_state = "playing"
                return
            elif key == ord('q') or key == ord('Q'):
                exit()

    def show_win_screen(self):
        self.win_screen.show()
        self.screen.refresh()
        while True:
            key = self.screen.getch()
            if key == ord('r') or key == ord('R'):
                self.game.reset_game()
                self.game.game_state = "playing"
                return
            elif key == ord('q') or key == ord('Q'):
                exit()