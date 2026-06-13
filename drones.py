#!/usr/bin/env python3

from typing import Optional, List


class Drone():
    def __init__(
        self,
        id_dron: str,
        start_zone: Optional[str] = None
    ):
        self.id_drone = id_dron
        self.start_zone = start_zone
        self.current_zone = start_zone
        self.final_destination: Optional[str] = None
        self.history: List[str] = [start_zone] if start_zone else []
        self.status = "waiting"
        self.route: List[str] = []
        self.arrived = False

    def set_destination(self, destination_zone: str):
        """Defines the final destination for the dron"""
        self.final_destination = destination_zone

    def set_route(self, route_list: list):
        """Asign the calculated route by the algorithm"""
        self.route = route_list

    def get_movement_options(self, map_obj) -> list:
        """Ask the maps for available neighbor zones"""
        if not self.current_zone:
            return []
        return map_obj.get_neighbours(self.current_zone)

    def move_to(self, next_zone: str):
        """Moves the dron to the next zone and records trace"""
        self.current_zone = next_zone
        self.history.append(next_zone)

        if next_zone == self.final_destination:
            self.status = "arrived"
        else:
            self.status = "in_transit"








"""
posición actual (una Zone)
estado (idle, moving, delivering…)
destino
ruta
capacidad de movimiento
historial de zonas visitadas"""
