#!/usr/bin/env python3

from typing import Optional
import pygame


class Connection:
    """Bidirectional link between two zones in the network."""

    def __init__(
        self,
        zone1: str,
        zone2: str,
        max_capacity: int = 1
    ) -> None:
        """Initialise a Connection.

        Args:
            zone1: Name of the first zone endpoint.
            zone2: Name of the second zone endpoint.
            max_capacity: Max simultaneous drones (default 1).
        """
        self.zone1 = zone1
        self.zone2 = zone2
        self.max_capacity = max_capacity
        self.current_drones = 0

    @property
    def color(self) -> pygame.Color:
        """Return a dinamic color based on the ocupation"""
        if self.current_drones > 0:
            return pygame.Color("orange")
        return pygame.Color("gray59")

    def has_space(self) -> bool:
        """Return True if the connection can accept one more drone."""
        return self.current_drones < self.max_capacity

    def enter_connection(self) -> None:
        """Increment drone count when a drone enters."""
        self.current_drones += 1

    def exit_connection(self) -> None:
        """Decrement drone count when a drone exits."""
        if self.current_drones > 0:
            self.current_drones -= 1
        else:
            print(
                f"WARNING: exit_connection() called on empty connection "
                f"{self.zone1}-{self.zone2}"
            )

    def get_destination_from(
        self, origin_zone: str
    ) -> Optional[str]:
        """Return the opposite endpoint given one zone name.

        Args:
            origin_zone: The zone the drone is departing from.

        Returns:
            Name of the destination zone, or None if origin_zone
            is not an endpoint of this connection.
        """
        if origin_zone == self.zone1:
            return self.zone2
        if origin_zone == self.zone2:
            return self.zone1
        return None
