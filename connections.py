#!/usr/bin/env python3

from typing import Optional


class Connection():
    def __init__(self,
                 zone1: str,
                 zone2: str,
                 max_capacity: Optional[int] = None):
        self.zone1 = zone1
        self.zone2 = zone2
        self.max_capacity = max_capacity
