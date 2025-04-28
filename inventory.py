from items import Sword, Bow, IceStaff, Shield, HealthPotion, PoisonPotion, Weapon

class Inventory:
    def __init__(self, count_of_slots=8, game=None):
        self.items = {}
        self.active_slot = 1
        self.count_of_slots = count_of_slots
        self.game = game
        self.is_open = False
        self.equipped_weapon = None
        print("DEBUG: Inventory initialized")

    def toggle(self):
        self.is_open = not self.is_open
        print(f"DEBUG: Inventory toggled to {'open' if self.is_open else 'closed'}")
        if self.game:
            if not self.is_open:
                self.game.interaction_panel.messages.clear()  # Очищаем сообщения при закрытии
                self.game.interaction_panel.hide_pickup_button()  # Скрываем кнопку подбора
            self.game._update_interface()

    def add_item(self, item) -> bool:
        for slot in range(1, self.count_of_slots + 1):
            if slot not in self.items:
                self.items[slot] = item
                if self.game:
                    self.game.interaction_panel.add_message(f"Подобран предмет: {item.title}")
                print(f"DEBUG: Added item '{item.title}' to slot {slot}")
                return True
        if self.game:
            self.game.interaction_panel.add_message("Инвентарь полон!")
        print("DEBUG: Inventory full")
        return False

    def change_slot(self, direction: int):
        new_slot = (self.active_slot + direction - 1) % self.count_of_slots + 1
        self.active_slot = new_slot
        print(f"DEBUG: Changed active slot to {self.active_slot}")
        if self.game:
            self.game._update_interface()

    def use_active_item(self):
        item = self.items.get(self.active_slot)
        if not item:
            if self.game:
                self.game.interaction_panel.add_message("Слот пуст!")
            print("DEBUG: Active slot is empty")
            return

        print(f"DEBUG: Using item '{item.title}' in slot {self.active_slot}")
        if isinstance(item, HealthPotion):
            heal = item.use(self.game.hero, self)
            self.game._sync_health()
            self.game.interaction_panel.add_message(f"Использовано '{item.title}': +{heal} HP")
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
            print(f"DEBUG: Equipped weapon '{weapon.title}'")
        else:
            if self.game:
                self.game.interaction_panel.add_message("Это не оружие!")
            print("DEBUG: Attempted to equip non-weapon")

    def unequip_weapon(self):
        if self.equipped_weapon:
            self.game.interaction_panel.add_message(f"Оружие '{self.equipped_weapon.title}' снято")
            print(f"DEBUG: Unequipped weapon '{self.equipped_weapon.title}'")
            self.equipped_weapon = None
        else:
            self.game.interaction_panel.add_message("Нет экипированного оружия!")
            print("DEBUG: No equipped weapon to unequip")

    def remove_active_item(self):
        if self.active_slot in self.items:
            item = self.items[self.active_slot]
            if item == self.equipped_weapon:
                self.unequip_weapon()
            del self.items[self.active_slot]
            if self.game:
                self.game.interaction_panel.add_message(f"Предмет '{item.title}' выброшен из слота {self.active_slot}")
                self.game._update_interface()
            print(f"DEBUG: Removed item '{item.title}' from slot {self.active_slot}")

    def get_active_item(self):
        item = self.items.get(self.active_slot)
        print(f"DEBUG: Active item is {item.title if item else 'None'}")
        return item