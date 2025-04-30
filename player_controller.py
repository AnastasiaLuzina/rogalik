class PlayerController:
    def __init__(self, game):
        self.game = game

    def move_hero(self, dx, dy):
        new_x, new_y = self.game.hero.x + dx, self.game.hero.y + dy
        if (new_x, new_y) in self.game.map.walkable:
            enemy = self.game.enemy_controller.get_enemy_at(new_x, new_y)
            if enemy:
                self.game.enemy_controller.handle_combat(enemy)
                return
            self.game.hero.x, self.game.hero.y = new_x, new_y
            self.check_item_interaction()
            self.game.display_manager.update_display()
            self.game.enemy_controller.move_enemies()

    def check_item_interaction(self):
        self.game.nearby_items = []
        hero_x, hero_y = self.game.hero.x, self.game.hero.y
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                x, y = hero_x + dx, hero_y + dy
                for item in self.game.items:
                    if item[0] == x and item[1] == y:
                        self.game.nearby_items.append(item)
                        break
        if self.game.nearby_items:
            self.game.interaction_panel.show_pickup_button()
        else:
            self.game.interaction_panel.hide_pickup_button()
        return len(self.game.nearby_items) > 0

    def handle_pickup(self):
       
        if not self.game.nearby_items:
            return
        picked_items = []
        for item in self.game.nearby_items[:]:
            x, y, item_obj = item
            if self.game.inventory.add_item(item_obj):
                self.game.items.remove(item)
                picked_items.append(item_obj.title)
        if picked_items:
            message = f"Подобрано: {', '.join(picked_items)}"
            self.game.interaction_panel.add_message(message)
            self.game.nearby_items.clear()
            self.game.updater._update_interface()