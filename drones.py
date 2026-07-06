#!/usr/bin/env python3

from typing import Optional
from connections import Connection
from zones import Zone


class Drone:
    """A drone agent navigating the routing network."""

    def __init__(
        self,
        id_dron: str,
        start_zone: Optional[str] = None
    ) -> None:
        """Initialise a Drone.

        Args:
            id_dron: Unique identifier (e.g. 'D1', 'D2').
            start_zone: Name of the zone where the drone begins.
        """
        self.id_dron = id_dron
        self.current_zone: Optional[str] = start_zone
        self.status: str = "waiting"
        self.transit_ticks_left: int = 0
        self.assigned_connection: Optional["Connection"] = None
        self.target_zone_obj: Optional["Zone"] = None
