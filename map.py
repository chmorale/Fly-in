#!/usr/bin/env python3


from typing import Optional, Dict, List
from zones import Zone
from connections import Connection


class Map:
    def __init__(self):
        self.drones: Dict = {}
        self.zones: Dict = {}
        self.connections: Dict[str, List[Connection]] = {}
        self.start_zone: Optional[str] = None
        self.end_zone: Optional[str] = None
        self.nb_drones: int = 0

    def add_zone(self, zone: Zone):
        self.zones[zone.zone_name] = zone
        self.connections[zone.zone_name] = []

        if zone.zone_type == "start_hub":
            self.start_zone = zone.zone_name
        elif zone.zone_type == "end_hub":
            self.end_zone = zone.zone_name

    def add_connection(self, connection: Connection):
        if connection.zone1 in self.connections:
            self.connections[connection.zone1].append(connection)
        if connection.zone2 in self.connections:
            self.connections[connection.zone2].append(connection)

    def get_zone(self, name: str) -> Zone:
        return self.zones[name]

    def add_drone(self, drone):
        self.drones[drone.id_dron] = drone

    def get_neighbours(self, zone_name: str) -> list:
        """Returns the name of the zones directly connected"""
        neighbours = []
        if zone_name not in self.connections:
            return []

        for conn in self.connections[zone_name]:
            dest = conn.get_destination_from(zone_name)
            if dest:
                neighbours.append(dest)
        return neighbours

    def get_available_routes(self, zone_name: str) -> list:
        """
        Returns a list of tuples (neighbour_name, objeto_connection_object)
        only if connection has free space at this moment.
        """
        available = []
        if zone_name not in self.connections:
            return []

        for conn in self.connections[zone_name]:
            if conn.has_space():
                dest = conn.get_destination_from(zone_name)
                if dest:
                    available.append((dest, conn))
        return available

    def find_shortest_route(self, start: str, end: str) -> list:
        """
        Calculates the better path with lesss steps from origin to goal
        using BFS clasical algorithm (Breadth-First Search).
        Returns a list with zones names to follow.
        """
        from collections import deque

        if start not in self.zones or end not in self.zones:
            return []

        queue = deque([(start, [start])])
        visited = {start}

        while queue:
            current_zone, current_path = queue.popleft()

            if current_zone == end:
                return current_path

            for neighbour in self.get_neighbours(current_zone):
                if neighbour not in visited:
                    visited.add(neighbour)
                    new_path = current_path + [neighbour]
                    queue.append((neighbour, new_path))

        return []
