#!/usr/bin/env python3

from zones.py import Zone

class Connection():
    def __init__(self, zona_a:Zone, zona_b:Zone, max_capacity: int):
        self.zona_a=zona_a
        self.zona_b=zona_b
        self.max_capacity=max_capacity

