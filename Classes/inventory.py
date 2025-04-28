from items import Sword, Bow, IceStaff, Shield, HealthPotion, PoisonPotion

class Inventory:
    def __init__(self, count_of_slots=8, game=None):
        self.items = {}
        self.active_slot = 1
        self.count_of_slots = count_of_slots
        self.game = game
        self.is_open = False  # Добавьте эту строку


    def toggle(self):
        """Переключает состояние инвентаря (открыт/закрыт)"""
        self.is_open = not self.is_open
        
        # Обновляем интерфейс через основной цикл игры
        if self.game:
            self.game._update_interface()
    
    def add_item(self, item) -> bool:
        """Добавляет предмет в первый свободный слот."""
        for slot in range(1, self.count_of_slots + 1):
            if slot not in self.items:
                self.items[slot] = item
                if self.game:
                    self.game.interaction_panel.add_message(f"Предмет добавлен в слот {slot}")
                return True
        if self.game:
            self.game.interaction_panel.add_message("Инвентарь полон!")
        return False
            
    def change_slot(self, direction: int):
        # Корректное зацикливание (1-8)
        new_slot = (self.active_slot + direction - 1) % self.count_of_slots + 1
        self.active_slot = new_slot  # Используйте сеттер для автоматического обновления
        print(f"DEBUG: Активный слот изменён на {self.active_slot}")  # Для отладки

    def use_active_item(self):
        """Использует предмет из активного слота"""
        item = self.items.get(self.active_slot)
        if not item:
            if self.game:
                self.game.interaction_panel.add_message("Слот пуст!")
            return

        # Пример логики для зелья
        if isinstance(item, HealthPotion):
            heal = item.use(self.game.hero, self)
            self.game.interaction_panel.add_message(f"Использовано: +{heal} HP")
            self.remove_active_item()


    def remove_active_item(self):
        """Удаляет предмет из активного слота"""
        if self.active_slot in self.items:
            del self.items[self.active_slot]
            if self.game:
                self.game.interaction_panel.add_message(f"Предмет удалён из слота {self.active_slot}")
                self.game._update_interface()
