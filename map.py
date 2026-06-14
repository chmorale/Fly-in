#!/usr/bin/env python3


from typing import Optional, Dict, List  # , Set, Tuple
from zones import Zone
from connections import Connection
from collections import deque


class Map:
    def __init__(self) -> None:
        self.drones: Dict = {}
        self.zones: Dict[str, Zone] = {}
        self.connections: Dict[str, List[Connection]] = {}
        self.start_zone: Optional[str] = None
        self.end_zone: Optional[str] = None
        self.nb_drones: int = 0

    def add_zone(self, zone: Zone) -> None:
        if zone.zone_type == "start_hub":
            if self.start_zone is not None:
                raise ValueError("Se ha detectado más de un 'start_hub' "
                                 "definido en el mapa.")
            self.start_zone = zone.zone_name
        elif zone.zone_type == "end_hub":
            if self.end_zone is not None:
                raise ValueError("Se ha detectado más de un 'end_hub' "
                                 "definido en el mapa.")
            self.end_zone = zone.zone_name

        self.zones[zone.zone_name] = zone
        self.connections[zone.zone_name] = []

    def add_connection(self, connection: Connection) -> None:
        if connection.zone1 in self.connections:
            self.connections[connection.zone1].append(connection)
        if connection.zone2 in self.connections:
            self.connections[connection.zone2].append(connection)

    def get_zone(self, name: str) -> Zone:
        return self.zones[name]

    def add_drone(self, drone) -> None:
        self.drones[drone.id_dron] = drone

    def get_neighbours(self, zone_name: str) -> list[str]:
        """Returns the name of the zones directly connected"""
        neighbours: List[str] = []
        if zone_name not in self.connections:
            return neighbours

        for conn in self.connections[zone_name]:
            dest = conn.get_destination_from(zone_name)
            if dest and self.zones[dest].zone_access != "blocked":
                neighbours.append(dest)
        return neighbours

    def get_available_routes(self, zone_name: str) -> list:
        """
        Returns a list of tuples (neighbour_name, connection_object)
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
        Calculates the better path with less steps from origin to goal
        using BFS clasical algorithm (Breadth-First Search).
        Returns a list with zones names to follow."""
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

    def find_dynamic_route(self, start: str, end: str) -> List[str]:
        """
        Calcula de forma dinámica la ruta óptima desde un nodo actual
        respetando las restricciones de zonas 'blocked' y priorizando
        los caminos con nodos 'priority'.
        """
        if start not in self.zones or end not in self.zones:
            return []

        # Cola almacena: (nodo_actual, camino_recorrido, coste_acumulado)
        queue = deque([(start, [start], 0)])
        best_costs: Dict[str, int] = {start: 0}
        optimal_path: List[str] = []
        min_cost = float('inf')

        while queue:
            curr_zone, path, cost = queue.popleft()

            if curr_zone == end:
                if cost < min_cost:
                    min_cost = cost
                    optimal_path = path
                continue

            for conn in self.connections.get(curr_zone, []):
                neighbour = conn.get_destination_from(curr_zone)
                if not neighbour:
                    continue

                target_zone = self.zones[neighbour]
                if target_zone.zone_access == "blocked":
                    continue

                # Cálculo de pesos dinámicos según el tipo de acceso
                step_cost = 1
                if target_zone.zone_access == "restricted":
                    step_cost = 2
                elif target_zone.zone_access == "priority":
                    step_cost = 0
                    # Peso mínimo para incentivar el flujo masivo

                next_cost = cost + step_cost

                if (neighbour not in best_costs or
                        next_cost < best_costs[neighbour]):
                    best_costs[neighbour] = next_cost
                    queue.append((neighbour, path + [neighbour], next_cost))

        return optimal_path
