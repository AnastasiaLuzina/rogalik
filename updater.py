from interface import HealthPanel, InteractionPanel
from display import DisplayManager
from inventory import Inventory

class Updater:
    def __init__(self, game):
        self.game = game  # Ссылка на основной объект игры

    def update_killed_counter(self):
        self.game.killed_enemies += 1
        self.game.health_panel.killed_enemies = self.game.killed_enemies
        self.game.health_panel.render(self.game.renderer.screen)
        self.game.renderer.screen.refresh()

    def _sync_health(self):
        self.game.health_panel.current_hp = self.game.hero.current_health

    def _update_interface(self):
        self._sync_health()
        has_items = self.game.check_item_interaction()
        if self.game.inventory.is_open:
            self._draw_inventory()
        else:
            self.game.display_manager.update_display()
        self.game.display_manager._draw_panels()  # ✅ Теперь вызываем через display_manager
        self.game.renderer.screen.refresh()
        self.game.display_manager._draw_panels()
        self.game.renderer.screen.refresh()

    def _draw_inventory(self):
        self.game.interaction_panel.show_inventory(
            self.game.inventory.items,
            self.game.inventory.active_slot,
            self.game.inventory.equipped_weapon
        )
        self.game.display_manager.update_display()