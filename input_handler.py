class InputHandler:
    def __init__(self, game):
        self.game = game

    def handle_key_press(self, key):
        if self.game.inventory.is_open:
            if key == ord('w') or key == ord('W'):
                self.game.inventory.change_slot(-1)
            elif key == ord('s') or key == ord('S'):
                self.game.inventory.change_slot(1)
            elif key == ord('e') or key == ord('E'):
                self.game.inventory.use_active_item()
            elif key == ord('r') or key == ord('R'):
                self.game.inventory.remove_active_item()
            elif key == ord('u') or key == ord('U'):
                self.game.inventory.unequip_weapon()
            elif key == ord('\t'):
                self.game.inventory.toggle()
            self.game.updater._update_interface()
            return

        if key == ord('\t'):
            self.game.inventory.toggle()
        elif key == ord('f') or key == ord('F'):
            self.game.player_controller.handle_pickup()
        elif key in (ord('w'), ord('W'), ord('a'), ord('A'), ord('s'), ord('S'), ord('d'), ord('D')):
            dx = 1 if key in (ord('d'), ord('D')) else -1 if key in (ord('a'), ord('A')) else 0
            dy = 1 if key in (ord('s'), ord('S')) else -1 if key in (ord('w'), ord('W')) else 0
            self.game.player_controller.move_hero(dx, dy)
        elif key == ord('q') or key == ord('Q'):
            self.game.game_over = True