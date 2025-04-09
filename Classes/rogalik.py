import random

class GenerateMap:

    def __init__ (self, height , width, array= None):
        self.height = height
        self.width = width
        self.array = array
        
    
    def set_map_area(self):
        self.array = [] # Всегда пишем self для обращения к переменным класса ат то плохо
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(' ')  
            self.array.append(row)
    
    


class GenerateRooms(GenerateMap):

    def __init__(self, height, width, coords_of_walls = {}, coords_of_rooms_area = []):
        super().__init__(height, width)
        self.coords_of_walls = coords_of_walls 
        self.coords_of_rooms_area = coords_of_rooms_area 

    def check_method(self, x, y):
        return (x < 0 or y < 0 or x >= self.height or y >= self.width) # если выход за границу карты то эту клетку скипаем

    def intersection_recognition(self, first_x, first_y, random_height_room, random_width_room):
        for i in range(random_height_room):
            for j in range(random_width_room):

                if self.check_method(first_x+i, first_y+j):
                    continue 

                if self.array[first_x + i][first_y +j] != ' ': 
                    return True
        return False

    def available_positions(self): #работаем с map
        self.coords_of_rooms_area = []
        for i in range(len(self.array)):
            for j in range(len(self.array[i])):
                if self.array[i][j] == '.':
                    self.coords_of_rooms_area.append((i, j))

        random_index = random.choice(self.coords_of_rooms_area) 
        
        return  random_index

    def generate_wall(self):

        count_of_wallss = random.randint(15, 20) 

        for n in range(count_of_wallss):

            self.coords_of_walls[n] = [] # создаем пустые ключи для словаря с тунелями

            random_height_room = random.randint(5, 20)
            random_width_room = random.randint(5, 20)

            if (random_height_room > self.height or random_width_room > self.width):
                continue

            first_x = random.randint(0, self.height - random_height_room)
            first_y = random.randint(0, self.width - random_width_room)

            if self.intersection_recognition(first_x, first_y, random_height_room, random_width_room):
                count_of_wallss +=1
                continue  # Если пересекается -> просто по новой запускаем цикл емае как я до этого не додумалась с первого раза епрст

            for i in range(random_height_room):
                self.array[first_x + i][first_y] = "║"
                self.array[first_x + i][first_y+ random_width_room - 1] = "║"

                self.coords_of_walls[n].append((first_x + i, first_y))
                self.coords_of_walls[n].append((first_x + i, first_y+ random_width_room - 1)) # словарик для туннелей



            for j in range(random_width_room):
                self.array[first_x][first_y +j] = "═"
                self.array[first_x + random_height_room - 1][first_y + j] = "═"

                self.coords_of_walls[n].append((first_x, first_y +j))
                self.coords_of_walls[n].append((first_x + random_height_room - 1, first_y + j)) # словарик координат для туннелей

            for i in range(1, random_height_room - 1):
                for j in range(1, random_width_room - 1):
                    self.array[first_x+ i][first_y + j] = "."


class Person:
    def __init__(self, health, position):
        self.health = health
        self.max_health = health
        self.position = position        

class Hero(Person):
    def __init__(self, health, position, symbol):
        super().__init__(health, position)
        self.symbol = symbol

class Enemy(Person):
    def __init__(self, health, position, symbol):
        super().__init__(health, position)
        self.symbol = symbol


class RenderNewFrame:
    def __init__(self, game_map):
        self.game_map = game_map

    def print_map(self):
        for row in self.game_map.array: #  надо писать в таком случае не self.array а  self.game_map.array
            print(' '.join(row))

    def place_person(self, person):
        x, y = person.position
        self.game_map.array[x][y] = person.symbol




map = GenerateRooms(70, 70)
map.set_map_area()
map.generate_wall()

frame = RenderNewFrame(map)

hero = Hero(100, map.available_positions(), "@")

frame.place_person(hero)

frame.print_map() 