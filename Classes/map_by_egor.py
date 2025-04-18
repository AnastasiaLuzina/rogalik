import random
import os
from typing import List, Dict, Set, Tuple
from colorama import init, Fore

init(autoreset=True)

# Размеры карты
MAP_WIDTH, MAP_HEIGHT = 80, 30

# Размеры панелей
PANEL_WIDTH = 20
HEALTH_HEIGHT = 5
INTERACTION_HEIGHT = 20

class Map:
    def __init__(self, width: int, height: int, max_rooms: int = 12, 
                 wall_char: str = '▓', empty_char: str = ' '):
        self.width = width
        self.height = height
        self.max_rooms = max_rooms
        self.wall_char = wall_char
        self.empty_char = empty_char
        self.rooms: List[Dict] = []
        self.walkable: Set[Tuple[int, int]] = set()
        self.tiles = self._generate_map()

    def _generate_map(self) -> List[List[str]]:
        tiles = [[self.wall_char for _ in range(self.width)] 
                for _ in range(self.height)]
        
        room_count = 0
        attempts = 0
        while room_count < self.max_rooms and attempts < 200:
            room = self._generate_room()
            if not self._rooms_intersect(room):
                self._create_room(tiles, room)
                self.rooms.append(room)
                room_count += 1
            attempts += 1
        
        self._connect_all_rooms(tiles)
        return tiles
        
    def _generate_room(self) -> Dict:
        w, h = random.randint(5, 12), random.randint(4, 8)
        x = random.randint(1, self.width - w - 2)
        y = random.randint(1, self.height - h - 2)
        x = max(1, min(x, self.width - w - 2))
        y = max(1, min(y, self.height - h - 2))
        return {
            'x1': x, 'y1': y, 
            'x2': x + w - 1, 
            'y2': y + h - 1, 
            'tiles': set(),
            'connections': 0
        }

    def _rooms_intersect(self, room: Dict) -> bool:
        for r in self.rooms:
            if (room['x1'] <= r['x2']+1 and room['x2'] >= r['x1']-1 and
                room['y1'] <= r['y2']+1 and room['y2'] >= r['y1']-1):
                return True
        return False

    def _create_room(self, tiles: List[List[str]], room: Dict):
        for y in range(room['y1'], room['y2']+1):
            for x in range(room['x1'], room['x2']+1):
                tiles[y][x] = self.empty_char
                room['tiles'].add((x, y))
                self.walkable.add((x, y))

    def _connect_all_rooms(self, tiles: List[List[str]]):
        self._connect_mst(tiles)
        
        rooms_with_3_connections = 0
        max_3_connections = 3
        
        center_x, center_y = self.width//2, self.height//2
        self.rooms.sort(key=lambda r: abs((r['x1']+r['x2'])/2 - center_x) + abs((r['y1']+r['y2'])/2 - center_y))
        
        for i, room in enumerate(self.rooms):
            if room['connections'] >= 3:
                continue
                
            possible_connections = min(3 - room['connections'], 2)
            
            if i < 3 and rooms_with_3_connections < max_3_connections:
                desired_connections = random.choices(
                    [1, 2, 3-room['connections']],
                    weights=[30, 50, 20],
                    k=1
                )[0]
                extra_connections = min(desired_connections, possible_connections)
            else:
                extra_connections = random.choices(
                    [0, 1, min(2, possible_connections)],
                    weights=[40, 40, 20],
                    k=1
                )[0]
            
            connections_made = 0
            attempts = 0
            
            while connections_made < extra_connections and attempts < 20:
                attempts += 1
                other_idx = random.randint(0, len(self.rooms)-1)
                if other_idx == i:
                    continue
                    
                other_room = self.rooms[other_idx]
                
                if other_room['connections'] >= 3:
                    continue
                
                self._connect_two_rooms(tiles, room, other_room)
                room['connections'] += 1
                other_room['connections'] += 1
                connections_made += 1
                
                if room['connections'] == 3:
                    rooms_with_3_connections += 1
                if other_room['connections'] == 3:
                    rooms_with_3_connections += 1
                
                if rooms_with_3_connections >= max_3_connections:
                    break

    def _connect_mst(self, tiles: List[List[str]]):
        if len(self.rooms) <= 1:
            return
            
        connected = set([0])
        connections_needed = len(self.rooms) - 1
        
        while len(connected) < len(self.rooms):
            best_dist = float('inf')
            best_pair = None
            
            for i in connected:
                for j in range(len(self.rooms)):
                    if j not in connected:
                        dist = self._room_distance(self.rooms[i], self.rooms[j])
                        if dist < best_dist:
                            best_dist = dist
                            best_pair = (i, j)
            
            if best_pair:
                i, j = best_pair
                self._connect_two_rooms(tiles, self.rooms[i], self.rooms[j])
                self.rooms[i]['connections'] += 1
                self.rooms[j]['connections'] += 1
                connected.add(j)

    def _room_distance(self, room1: Dict, room2: Dict) -> float:
        x1 = (room1['x1'] + room1['x2']) // 2
        y1 = (room1['y1'] + room1['y2']) // 2
        x2 = (room2['x1'] + room2['x2']) // 2
        y2 = (room2['y1'] + room2['y2']) // 2
        return ((x1-x2)**2 + (y1-y2)**2)**0.5

    def _connect_two_rooms(self, tiles: List[List[str]], room1: Dict, room2: Dict):
        x1, y1 = (room1['x1'] + room1['x2']) // 2, (room1['y1'] + room1['y2']) // 2
        x2, y2 = (room2['x1'] + room2['x2']) // 2, (room2['y1'] + room2['y2']) // 2
        
        if random.random() < 0.7:
            if random.random() < 0.5:
                mid_x, mid_y = x2, y1
            else:
                mid_x, mid_y = x1, y2
            
            self._create_h_tunnel(tiles, x1, mid_x, y1)
            self._create_v_tunnel(tiles, y1, mid_y, mid_x)
            self._create_h_tunnel(tiles, mid_x, x2, y2)
            self._create_v_tunnel(tiles, mid_y, y2, x2)
        else:
            if random.random() < 0.5:
                self._create_h_tunnel(tiles, x1, x2, y1)
                self._create_v_tunnel(tiles, y1, y2, x2)
            else:
                self._create_v_tunnel(tiles, y1, y2, x1)
                self._create_h_tunnel(tiles, x1, x2, y2)

    def _create_h_tunnel(self, tiles: List[List[str]], x1: int, x2: int, y: int):
        for x in range(min(x1, x2), max(x1, x2)+1):
            if 0 <= x < self.width and 0 <= y < self.height:
                tiles[y][x] = self.empty_char
                self.walkable.add((x, y))

    def _create_v_tunnel(self, tiles: List[List[str]], y1: int, y2: int, x: int):
        for y in range(min(y1, y2), max(y1, y2)+1):
            if 0 <= x < self.width and 0 <= y < self.height:
                tiles[y][x] = self.empty_char
                self.walkable.add((x, y))

    def render(self, hero=None, enemies=[], items=[]):
        for y in range(self.height):
            line = []
            for x in range(self.width):
                cell_content = self.empty_char  # Один символ
                # Стены
                if self.tiles[y][x] == self.wall_char:
                    cell_content = f"{Fore.BLACK}{self.wall_char}"
                # Герой
                if hero and x == hero.x and y == hero.y:
                    cell_content = f"{hero.color}{hero.char}"
                # Предметы
                for item_x, item_y, item in items:
                    if item_x == x and item_y == y:
                        cell_content = f"{Fore.GREEN}{item.symbol}"
                # Враги
                for enemy in enemies:
                    if enemy.x == x and enemy.y == y and enemy.current_health > 0:
                        cell_content = f"{enemy.color}{enemy.char}"
                line.append(cell_content)
            # Добавляем правую границу карты
            line.append(Fore.BLACK + self.wall_char)  # <-- Добавлено
            print(''.join(line))
            
class HealthPanel:
    def __init__(self, x: int, y: int, width: int, height: int, 
                 current_hp: int, max_hp: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.current_hp = current_hp
        self.max_hp = max_hp

    def render(self):
        # Отрисовка рамки
        print(f"\033[{self.y+1};{self.x+1}H╔{'═'*(self.width-2)}╗")
        for dy in range(1, self.height-1):
            print(f"\033[{self.y+1+dy};{self.x+1}H║{' '*(self.width-2)}║")
        print(f"\033[{self.y+self.height};{self.x+1}H╚{'═'*(self.width-2)}╝")
        
        # Текст здоровья
        hp_text = f"HP: {self.current_hp}/{self.max_hp}"
        hp_percent = self.current_hp / self.max_hp
        bar_width = self.width - 4
        filled = int(bar_width * hp_percent)
        health_bar = f"{Fore.RED}{'█'*filled}{Fore.WHITE}{'░'*(bar_width-filled)}"
        
        # Центрируем текст и прогресс-бар
        print(f"\033[{self.y+2};{self.x+2}H{hp_text.center(self.width-2)}")
        print(f"\033[{self.y+3};{self.x+2}H{health_bar}")


class InteractionPanel:
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.messages = []

    def add_message(self, message: str):
        self.messages.append(message)
        if len(self.messages) > self.height - 2:
            self.messages.pop(0)

    def render(self):
        # Отрисовка рамки
        print(f"\033[{self.y+1};{self.x+1}H╔{'═'*(self.width-2)}╗")
        for dy in range(1, self.height-1):
            print(f"\033[{self.y+1+dy};{self.x+1}H║{' '*(self.width-2)}║")
        print(f"\033[{self.y+self.height};{self.x+1}H╚{'═'*(self.width-2)}╝")
        
        # Отображение сообщений
        for i, msg in enumerate(self.messages):
            print(f"\033[{self.y+1+i};{self.x+2}H{msg[:self.width-2]}")

if __name__ == "__main__":
    # Установка размера консоли
    os.system(f'mode con: cols={MAP_WIDTH + PANEL_WIDTH} lines={MAP_HEIGHT + 3}')
    os.system('cls')  # Очистка экрана

    # Инициализация и отрисовка карты
    map_instance = Map(MAP_WIDTH, MAP_HEIGHT, max_rooms=12)
    map_instance.render()

    # Отрисовка панелей
    health_panel = HealthPanel(
        x=MAP_WIDTH + 1, y=1, 
        width=PANEL_WIDTH, height=HEALTH_HEIGHT,
        current_hp=85, max_hp=100
    )
    health_panel.render()

    interaction_panel = InteractionPanel(
        x=MAP_WIDTH + 1, y=HEALTH_HEIGHT + 1,
        width=PANEL_WIDTH, height=INTERACTION_HEIGHT
    )
    interaction_panel.add_message("Добро пожаловать!")
    interaction_panel.add_message("Используйте WASD для движения.")
    interaction_panel.add_message("Нажмите Q для выхода.")
    interaction_panel.render()