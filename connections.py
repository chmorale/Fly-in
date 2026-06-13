#!/usr/bin/env python3

from typing import Optional


class Connection:
    def __init__(self,
                 zone1: str,
                 zone2: str,
                 max_capacity: Optional[int] = None):
        self.zone1 = zone1
        self.zone2 = zone2
        self.max_capacity = max_capacity
        self.current_drones = 0

    def has_space(self) -> bool:
        """Verify if connection admit more drones at this moment"""
        if self.max_capacity is None:
            return True
        return self.current_drones < self.max_capacity

    def enter_connection(self):
        """Increment drones' number when a drone enters"""
        self.current_drones += 1

    def exit_connection(self):
        """Decrement drones when a dron exits"""
        if self.current_drones > 0:
            self.current_drones -= 1

    def get_destination_from(self, origin_zone: str) -> Optional[str]:
        """Due an origin, returns the other side name"""
        if origin_zone == self.zone1:
            return self.zone2
        if origin_zone == self.zone2:
            return self.zone1
        return None
