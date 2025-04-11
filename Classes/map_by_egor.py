import random
import sys
import msvcrt  # Для Windows
from typing import List, Dict
from colorama import init, Back, Fore

init(autoreset=True)

class Entity:
    def __init__(self, x: int, y: int, char: str, color: str):
        self.x = x
        self.y = y
        self.char = char
        self.color = color

class Map:
    def __init__(self, width: int, height: int, max_rooms: int = 7):
        self.width = width
        self.height = height
        self.max_rooms = max_rooms
        self.rooms = []
        self.tiles = self._generate_tiles()
        self.player = Entity(0, 0, '@', Fore.RED)
        self._place_player()

    def _generate_tiles(self) -> List[List[str]]:
        tiles = [[Back.BLACK + ' ' for _ in range(self.width)] for _ in range(self.height)]
        
        for _ in range(self.max_rooms):
            room_width = random.randint(4, 8)
            room_height = random.randint(4, 8)
            
            x = random.randint(1, self.width - room_width - 2)
            y = random.randint(1, self.height - room_height - 2)
            
            new_room = {
                'x1': x,
                'y1': y,
                'x2': x + room_width - 1,
                'y2': y + room_height - 1
            }
            
            if not self._rooms_intersect(new_room, self.rooms):
                self._create_room(tiles, new_room)
                
                if self.rooms:
                    self._connect_rooms(tiles, self.rooms[-1], new_room)
                
                self.rooms.append(new_room)
        
        return tiles

    def _rooms_intersect(self, room: Dict, rooms: List[Dict]) -> bool:
        for r in rooms:
            if (room['x1'] <= r['x2'] + 1 and
                room['x2'] >= r['x1'] - 1 and
                room['y1'] <= r['y2'] + 1 and
                room['y2'] >= r['y1'] - 1):
                return True
        return False

    def _create_room(self, tiles: List[List[str]], room: Dict):
        for y in range(room['y1'], room['y2'] + 1):
            for x in range(room['x1'], room['x2'] + 1):
                if 0 <= x < self.width and 0 <= y < self.height:
                    tiles[y][x] = Back.WHITE + ' '

    def _connect_rooms(self, tiles: List[List[str]], room1: Dict, room2: Dict):
        x1, y1 = (room1['x1'] + room1['x2']) // 2, (room1['y1'] + room1['y2']) // 2
        x2, y2 = (room2['x1'] + room2['x2']) // 2, (room2['y1'] + room2['y2']) // 2
        
        if random.random() < 0.5:
            self._create_h_tunnel(tiles, x1, x2, y1)
            self._create_v_tunnel(tiles, y1, y2, x2)
        else:
            self._create_v_tunnel(tiles, y1, y2, x1)
            self._create_h_tunnel(tiles, x1, x2, y2)

    def _create_h_tunnel(self, tiles: List[List[str]], x1: int, x2: int, y: int):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            if 0 <= x < self.width and 0 <= y < self.height:
                tiles[y][x] = Back.WHITE + ' '

    def _create_v_tunnel(self, tiles: List[List[str]], y1: int, y2: int, x: int):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            if 0 <= x < self.width and 0 <= y < self.height:
                tiles[y][x] = Back.WHITE + ' '

    def _place_player(self):
        if self.rooms:
            first_room = self.rooms[0]
            self.player.x = (first_room['x1'] + first_room['x2']) // 2
            self.player.y = (first_room['y1'] + first_room['y2']) // 2

    def render(self):
        display = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                if Back.BLACK in self.tiles[y][x]:
                    row.append(Back.BLACK + ' ')
                else:
                    row.append(Back.WHITE + ' ')
            display.append(row)
        
        if 0 <= self.player.y < self.height and 0 <= self.player.x < self.width:
            bg = Back.BLACK if Back.BLACK in self.tiles[self.player.y][self.player.x] else Back.WHITE
            display[self.player.y][self.player.x] = bg + self.player.color + self.player.char
        
        print("\033[H\033[J")  # Очистка терминала
        for row in display:
            print(''.join(row))
        print("WASD - движение, Q - выход (без Enter)")

    def move_player(self, dx: int, dy: int):
        new_x, new_y = self.player.x + dx, self.player.y + dy
        
        if (0 <= new_x < self.width and 
            0 <= new_y < self.height and 
            self.tiles[new_y][new_x] != Back.BLACK + ' '):
            self.player.x = new_x
            self.player.y = new_y

def get_key():
    """Функция для получения нажатой клавиши без Enter"""
    while True:
        if msvcrt.kbhit():
            key = msvcrt.getch().decode('utf-8').lower()
            if key in ['w', 'a', 's', 'd', 'q']:
                return key

def main():
    game_map = Map(40, 20)
    
    while True:
        game_map.render()
        key = get_key()
        
        if key == 'q':
            break
        elif key == 'w':
            game_map.move_player(0, -1)
        elif key == 'a':
            game_map.move_player(-1, 0)
        elif key == 's':
            game_map.move_player(0, 1)
        elif key == 'd':
            game_map.move_player(1, 0)

if __name__ == "__main__":
    main()