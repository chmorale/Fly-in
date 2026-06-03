#!/usr/bin/env python3

class Zone():
    def __init__(self, zone_name:str, coordinates:tuple[int, int], zone_type:str, zone_color:str, max_drones:int):
        self.zone_name=zone_name
        self.coordinates=coordinates
        self.zone_type=zone_type
        self.zone_color=zone_color
        self.max_drones=max_drones

"""nombre
coordenadas (x, y)
tipo (normal, restricted, blocked, priority)
color
max_drones"""