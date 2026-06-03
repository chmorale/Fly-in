#!/usr/bin/env python3

import Zone from zones.py


class map:
    def __init__(self):
        self.zones={}
        self.connections
        self.star_zone=None
        self.end_zone=None
        self.nb_drones=0

    def add_zone(self, zone:Zone):
        self.zones[zone.zone_name] = zone

    def add_connection(self, connection: Connection):
        self.connections.append(connection)

    def get_zone(self, name: str) -> Zone:
        return self.zones.get(name)