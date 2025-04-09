import random

class GenerateMap:

    def __init__ (self, height , width, array= None, point_coords = {}):
        self.height = height
        self.width = width
        self.array = array
        self.point_coords = point_coords
    
    def set_map_area(self):
        self.array = [] # Всегда пишем self для обращения к переменным класса ат то плохо
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(' ')  
            self.array.append(row)
    
    def print_map(self):
        for row in self.array:
            print(' '.join(row))


class GenerateRooms(GenerateMap):

    def __init__(self, height, width):
        super().__init__(height, width) 

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

    def generate_wall(self):

        count_of_rooms = random.randint(15, 20) 

        for n in range(count_of_rooms):

            self.point_coords[n] = [] # создаем пустые ключи для словаря с тунелями

            random_height_room = random.randint(5, 20)
            random_width_room = random.randint(5, 20)

            if (random_height_room > self.height or random_width_room > self.width):
                continue

            first_x = random.randint(0, self.height - random_height_room)
            first_y = random.randint(0, self.width - random_width_room)

            if self.intersection_recognition(first_x, first_y, random_height_room, random_width_room):
                count_of_rooms +=1
                continue  # Если пересекается -> просто по новой запускаем цикл емае как я до этого не додумалась с первого раза епрст

            for i in range(random_height_room):
                self.array[first_x + i][first_y] = "║"
                self.array[first_x + i][first_y+ random_width_room - 1] = "║"

                self.point_coords[n].append((first_x + i, first_y))
                self.point_coords[n].append((first_x + i, first_y+ random_width_room - 1)) # словарик для туннелей



            for j in range(random_width_room):
                self.array[first_x][first_y +j] = "═"
                self.array[first_x + random_height_room - 1][first_y + j] = "═"

                self.point_coords[n].append((first_x, first_y +j))
                self.point_coords[n].append((first_x + random_height_room - 1, first_y + j)) # словарик координат для туннелей

            for i in range(1, random_height_room - 1):
                for j in range(1, random_width_room - 1):
                    self.array[first_x+ i][first_y + j] = "."

map = GenerateRooms(70, 70)
map.set_map_area()
map.generate_wall()
map.print_map()