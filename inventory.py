from items import Sword, Bow, IceStaff, HealthPotion, PoisonPotion, Weapon

class Inventory:
    def __init__(self, count_of_slots=8, game=None):
        self.items = {}
        self.active_slot = 1
        self.count_of_slots = count_of_slots
        self.game = game
        self.is_open = False
        self.equipped_weapon = None

    def toggle(self):
        self.is_open = not self.is_open
        if self.game:
            if not self.is_open:
                self.game.interaction_panel.messages.clear()  
                self.game.interaction_panel.hide_pickup_button() 
            self.game._update_interface()

    def add_item(self, item) -> bool:
        for slot in range(1, self.count_of_slots + 1):
            if slot not in self.items:
                self.items[slot] = item
                return True
        return False

    def change_slot(self, direction: int):
        new_slot = self.active_slot
        if direction == -1: 
            new_slot = self.active_slot - 1 if self.active_slot > 1 else self.count_of_slots
        elif direction == 1:  
            new_slot = self.active_slot + 1 if self.active_slot < self.count_of_slots else 1
            
        self.active_slot = new_slot
        if self.game:
            self.game._update_interface()

    def use_active_item(self):
        item = self.items.get(self.active_slot)
        if not item:
            if self.game:
                self.game.interaction_panel.add_message("Слот пуст!")
            return

        if isinstance(item, HealthPotion):
            heal = item.use(self.game.hero, self)
            self.game._sync_health()
            self.game.interaction_panel.add_message(f"Использовано '{item.title}': +{heal} HP")
            item._break_and_remove(self) 
        elif isinstance(item, Weapon):
            self.equip_weapon(item)
            self.game.interaction_panel.add_message(f"Экипировано: {item.title}")
        else:
            self.game.interaction_panel.add_message(f"Нельзя использовать '{item.title}'!")

    def equip_weapon(self, weapon):
        if isinstance(weapon, Weapon):
            self.equipped_weapon = weapon
            if self.game:
                self.game.interaction_panel.add_message(f"Оружие '{weapon.title}' экипировано")
        else:
            if self.game:
                self.game.interaction_panel.add_message("Это не оружие!")

    def unequip_weapon(self):
        if self.equipped_weapon:
            self.game.interaction_panel.add_message(f"Оружие '{self.equipped_weapon.title}' снято")

            self.equipped_weapon = None
        else:
            self.game.interaction_panel.add_message("Нет экипированного оружия!")

    def remove_active_item(self):
        if self.active_slot in self.items:
            item = self.items[self.active_slot]
            if item == self.equipped_weapon:
                self.unequip_weapon()
            del self.items[self.active_slot]
            if self.game:
                self.game.interaction_panel.add_message(f"Предмет '{item.title}' выброшен из слота {self.active_slot}")
                self.game._update_interface()

    def get_active_item(self):
        item = self.items.get(self.active_slot)
        return item