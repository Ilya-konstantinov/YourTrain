from datetime import time, timedelta

class Path:
    def __init__(self, path_id: int, dep_st_id: int, arr_sr_id: int, departure_time: timedelta, arrival_time: timedelta, cost: int, high_speed: bool) -> None:
        self.departure_time = departure_time
        
        if (departure_time > arrival_time) :
            arrival_time.days += 1
        
        self.arrival_time = arrival_time
        self.path_time = (arrival_time - departure_time)
        self.path_id = path_id
        self.cost = cost
        self.high_speed = high_speed
        self.dep_st_id = dep_st_id
        self.arr_st_id = arr_sr_id