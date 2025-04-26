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
        """Переключает активный слот с учетом занятых слотов"""
        occupied = sorted([slot for slot in self.items if self.items.get(slot)])
        if not occupied:
            return
        
        try:
            current_idx = occupied.index(self.active_slot)
            new_idx = (current_idx + direction) % len(occupied)
        except ValueError:
            new_idx = 0
        
        self.active_slot = occupied[new_idx]
        if self.game:
            self.game._update_interface()

    def use_active_item(self):
        """Использует предмет из активного слота"""
        item = self.items.get(self.active_slot)
        if not item:
            if self.game:
                self.game.interaction_panel.add_message("Слот пуст!")
            return

        # Использование предмета на герое
        if isinstance(item, HealthPotion):
            heal_amount = item.use(self.game.hero, self)
            if self.game:
                self.game.interaction_panel.add_message(f"Использовано зелье: +{heal_amount} HP")
            self.remove_item(item)

        # Другие типы предметов...

    def remove_item(self, item):
        """Удаляет предмет из инвентаря"""
        for slot, slot_item in list(self.items.items()):
            if slot_item == item:
                del self.items[slot]
                return True
        return False