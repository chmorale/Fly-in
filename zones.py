#!/usr/bin/env python3

from typing import Optional


class Zone():
    def __init__(
        self,
        zone_name: str,
        coordinates: tuple[int, int],
        zone_type: Optional[str] = None,
        zone_color: Optional[str] = None,
        max_drones: Optional[int] = None,
        zone_access: str = "normal"
    ):
        self.zone_name = zone_name
        self.coordinates = coordinates
        self.zone_type = zone_type
        self.zone_color = zone_color
        self.max_drones = max_drones
        self.zone_access = zone_access
