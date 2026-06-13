#!/usr/bin/env python3

from typing import Optional


class Zone:
    def __init__(
        self,
        zone_name: str,
        coordinates: tuple[int, int],
        zone_type: Optional[str] = None,
        zone_color: Optional[str] = None,
        max_drones: Optional[int] = None,
        zone_access: str = "normal",
        current_drones: int = 0
    ):
        self.zone_name = zone_name
        self.coordinates = coordinates
        self.zone_type = zone_type
        self.zone_color = zone_color
        self.max_drones = max_drones
        self.zone_access = zone_access
        self.current_drones = current_drones

    def has_space(self) -> bool:
        """Verify if zone has capacity enough for more drones"""
        if self.max_drones is None:
            return True
        return self.current_drones < self.max_drones

    def enter_zone(self):
        """Adds a new drone to the zone"""
        self.current_drones += 1

    def exit_zone(self):
        """Delete a drone from the zone"""
        if self.current_drones > 0:
            self.current_drones -= 1
