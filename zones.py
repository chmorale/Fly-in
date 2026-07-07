#!/usr/bin/env python3

from typing import Optional
import pygame


class Zone:
    """A node in the drone routing network."""

    def __init__(
        self,
        zone_name: str,
        coordinates: tuple[int, int],
        zone_type: Optional[str] = None,
        zone_color: Optional[str] = None,
        max_drones: Optional[int] = 1,
        zone_access: str = "normal",
        current_drones: int = 0
    ) -> None:
        """Initialise a Zone.

        Args:
            zone_name: Unique identifier for this zone.
            coordinates: (x, y) integer grid position.
            zone_type: 'start_hub', 'hub', 'end_hub', or None.
            zone_color: Optional colour hint for visualisation.
            max_drones: Capacity limit (None = unlimited).
            zone_access: 'normal', 'restricted', 'priority',
                or 'blocked'.
            current_drones: Initial drone count (default 0).
        """
        self.zone_name = zone_name
        self.coordinates = coordinates
        self.zone_type = zone_type
        self.zone_color = zone_color
        self.max_drones = max_drones
        self.zone_access = zone_access
        self.current_drones = current_drones
        self.reserved_spaces: int = 0

    @property
    def color(self) -> pygame.Color:
        """Return a dinamic color based on the zone type"""
        if self.zone_access == "normal":
            return pygame.Color("blue")
        elif self.zone_access == "restricted":
            return pygame.Color("red")
        elif self.zone_access == "priority":
            return pygame.Color("purple")
        elif self.zone_access == "blocked":
            return pygame.Color("gray31")
        return pygame.Color("blue")

    def has_space(self) -> bool:
        """Return True if the zone can accept one more drone."""
        if self.max_drones is None:
            return True
        return self.current_drones < self.max_drones

    def has_space_with_reservation(self) -> bool:
        """Check capacity including in-transit reservations."""
        if self.max_drones is None:
            return True
        return (
            self.current_drones + self.reserved_spaces
        ) < self.max_drones

    def reserve_space(self) -> None:
        """Mark a space as committed by an in-transit drone."""
        self.reserved_spaces += 1

    def release_reservation(self) -> None:
        """Free a reservation when a drone lands."""
        if self.reserved_spaces > 0:
            self.reserved_spaces -= 1

    def enter_zone(self) -> None:
        """Increment drone count when a drone enters."""
        self.current_drones += 1

    def exit_zone(self) -> None:
        """Decrement drone count when a drone exits."""
        if self.current_drones > 0:
            self.current_drones -= 1
