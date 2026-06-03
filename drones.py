#!/usr/bin/env python3

from zones.py import Zone

class Drone():
    def __init__(self, start_zone:Zone):
        self.position=start_zone
        self.state="iddle"
        self.destination=None
        self.route=[]

    def state(self, state):
        self.state=state

    def destination():


    def route():







"""
posición actual (una Zone)
estado (idle, moving, delivering…)
destino
ruta
capacidad de movimiento
historial de zonas visitadas"""
