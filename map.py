#!/usr/bin/env python3

from zones import Zone
from connections import Connection


class Map:
    def __init__(self):
        self.drones = {}
        self.zones = {}
        self.connections = {}
        self.start_zone = None
        self.end_zone = None
        self.nb_drones = 0

    def add_zone(self, zone: Zone):
        self.zones[zone.zone_name] = zone
        self.connections[zone.zone_name] = []

        if zone.zone_type == "start_hub":
            self.start_zone = zone.zone_name
        elif zone.zone_type == "end_hub":
            self.end_zone = zone.zone_name

    def add_connection(self, connection: Connection):
        self.connections[connection.zone1].append(connection)
        self.connections[connection.zone2].append(connection)

    def get_zone(self, name: str) -> Zone:
        return self.zones[name]

    def add_drone(self, drone):
        self.drones[drone.id_dron] = drone

    def get_neighbours(self, zone_name: str) -> list:
        return self.connections.get(zone_name, [])
