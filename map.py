#!/usr/bin/env python3

from typing import Optional, Dict, List, TYPE_CHECKING
from zones import Zone
from connections import Connection
import heapq

if TYPE_CHECKING:
    from drones import Drone


class Map:
    """Graph of zones and connections for the drone simulation."""

    def __init__(self) -> None:
        """Initialise an empty Map."""
        self.drones: Dict = {}
        self.zones: Dict[str, Zone] = {}
        self.connections: Dict[str, List[Connection]] = {}
        self.start_zone: Optional[str] = None
        self.end_zone: Optional[str] = None
        self.nb_drones: int = 0
        self.min_x: int = 0
        self.min_y: int = 0
        self.max_x: int = 0
        self.max_y: int = 0

    def add_zone(self, zone: Zone) -> None:
        """Register a zone and initialise its connection list.

        Args:
            zone: Zone object to add to the map.
        """
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
        """Register a connection in both endpoint adjacency lists.

        Args:
            connection: Connection object to add.
        """
        if connection.zone1 in self.connections:
            self.connections[connection.zone1].append(connection)
        if connection.zone2 in self.connections:
            self.connections[connection.zone2].append(connection)

    def get_zone(self, name: str) -> Zone:
        """Return the Zone with the given name.

        Args:
            name: Zone identifier.
        """
        return self.zones[name]

    def add_drone(self, drone: "Drone") -> None:
        """Register a drone in the simulation.

        Args:
            drone: Drone object to add.
        """
        self.drones[drone.id_dron] = drone

    def find_dynamic_route(self, start: str, end: str) -> List[str]:
        """Compute the minimum-cost path using Dijkstra.

        Weights: priority=0, normal=1, restricted=2.
        Congestion penalty: +1 per drone on each connection.
        Full connections and blocked zones are excluded.

        Args:
            start: Name of the origin zone.
            end:   Name of the destination zone.

        Returns:
            Ordered list of zone names from start to end,
            or [] if no path exists.
        """
        if start not in self.zones or end not in self.zones:
            return []

        heap = [(0, start, [start])]
        best_costs: Dict[str, float] = {start: 0}

        while heap:
            cost, curr_zone, path = heapq.heappop(heap)

            if curr_zone == end:
                return path

            if cost > best_costs.get(curr_zone, float('inf')):
                continue

            for conn in self.connections.get(curr_zone, []):
                if not conn.has_space():
                    continue

                neighbour = conn.get_destination_from(curr_zone)
                if not neighbour:
                    continue

                target_zone = self.zones[neighbour]
                if target_zone.zone_access == "blocked":
                    continue

                step_cost = 1
                if target_zone.zone_access == "restricted":
                    step_cost = 2
                elif target_zone.zone_access == "priority":
                    step_cost = 0

                step_cost += conn.current_drones
                next_cost = cost + step_cost

                if next_cost < best_costs.get(neighbour, float('inf')):
                    best_costs[neighbour] = next_cost
                    heapq.heappush(
                        heap,
                        (next_cost, neighbour, path + [neighbour])
                    )

        return []
