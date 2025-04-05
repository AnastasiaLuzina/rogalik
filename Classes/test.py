





# бракованный вариант с очень душной логикой -> в мусорку


import random

class GenerateMap:

    def __init__ (self, height , width, array= None, point_coords = {}):
        self.height = height
        self.width = width
        self.array = array
        self.point_coords = point_coords
    
    
    def set_map_area(self):

        self.array = [] #нужно всегда писать при обращеннии адрес на класс self!!!!
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

 
    def check_method (self, x, y):
            return (x < 0 or y < 0 or x >= self.height or y >= self.width )

    def intersection_recognition (self, first_x, first_y, random_height_room, random_width_room):

        sides_of_clash = []

        stop_x = 0
        stop_y = 0

        for p in range(random_width_room):

            if self.check_method(first_x, first_y + p + 2): continue

            if self.array[first_x][first_y + p + 2] == "║" or self.array[first_x][first_y + p +2] == "═":
                stop_x = first_x
                stop_y = first_y + p
                sides_of_clash.append("vertically")

        for p in range(random_height_room):

            if self.check_method(first_x  + p + 2, first_y): continue

            if self.array[first_x + p + 2][first_y] == "║" or self.array[first_x  + p + 2][first_y] == "═":
                stop_x = first_x + p
                stop_y = first_y 
                sides_of_clash.append("horizontal")


        if not sides_of_clash:
            for i in range(random_height_room):
                for j in range(random_width_room):
   
                        self.array[first_x][first_y + j] = "═"
                        self.array[first_x + random_height_room - 1][first_y + j] = "═"

                        self.array[first_x +i][first_y] = "║"
                        self.array[first_x + i][first_y + random_width_room - 1] = "║"

        if "vertically" in sides_of_clash or "horizontal" in sides_of_clash:

                if "vertically" in sides_of_clash and "horizontal" in sides_of_clash:
                    for i in range(stop_x):
                        for j in range(stop_y):

                            self.array[first_x][first_y + j] = "═"
                            self.array[stop_x + random_height_room - 1][first_y + j] = "═"

                            self.array[first_x +i][first_y] = "║"
                            self.array[first_x + i][stop_y + random_width_room - 1] = "║"

                if "vertically" in sides_of_clash and not "horizontal" in sides_of_clash:
                    for i in range(random_height_room):
                        for j in range(stop_y):

                            self.array[first_x][first_y + j] = "═"
                            self.array[stop_x + random_height_room - 1][first_y + j] = "═"

                            self.array[first_x +i][first_y] = "║"
                            self.array[first_x + i][first_y + random_width_room - 1] = "║"

                if  "horizontal" in sides_of_clash and not "vertically" in sides_of_clash:
                    for i in range(stop_x):
                        for j in range(random_width_room):

                            self.array[first_x][first_y + j] = "═"
                            self.array[first_x + random_height_room - 1][first_y + j] = "═"

                            self.array[first_x +i][first_y] = "║"
                            self.array[first_x + i][stop_y + random_width_room - 1] = "║"
                




    def generate_wall (self):
    
        count_of_rooms = random.randint(1, 9) 

        for n in range(count_of_rooms):

            random_height_room = random.randint(5, 15)
            random_width_room = random.randint(5, 15)

            
            if (random_height_room > self.height or random_width_room > self.width):
                continue

            first_x = random.randint(0, self.height - random_height_room)
            first_y = random.randint(0, self.width - random_width_room)

            if self.array[first_x][first_y] == "." or self.array[first_x][first_y] == "║" or self.array[first_x][first_y] == "═" :
                continue

            self.intersection_recognition(first_x, first_y, random_height_room, random_width_room)

            for i in range(1, random_height_room - 1):  # Внутри вертикальных стенок
                for j in range(1, random_width_room - 1):  # Внутри горизонтальных стенок
                    self.array[first_x + i][first_y + j] = "."
                
                                
map = GenerateRooms(50, 50) #нужно инициализировать через наследника
map.set_map_area()
map.generate_wall()
map.print_map()