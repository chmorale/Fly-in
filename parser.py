#!/usr/bin/env python3

from map import Map
from zones import Zone
from drones import Drone
from connections import Connection


def options(text:str) -> dict:
    valores = {}
    options = text.split(" ")
    for o in options:
        options_detail = o.split("=")
        if len(options_detail) == 2:
            valores[options_detail[0]] = options_detail[1]
    return valores
            

def parser(filepath:str) -> Map:
    map = Map()
    nb_drones = 0
    start_zone = None
    try:
        with open(filepath) as f:
            for line in f:
                line = line.strip()
                if ":" in line:
                    key, _, text_value = line.partition(":") 
                    # procesar conexiones
                    if key == "connection":
                        max_link_capacity = None
                        before, _, after = text_value.partition("[")
                        before = before.strip()
                        key = key.strip()
                        text_values =before.split("-")
                        if len(text_values) == 2:
                            zone1=text_values[0].strip() 
                            zone2=text_values[1].strip()
                        else:
                            continue
                        if after:
                            inside = after.replace("]", "").strip()
                            optional_values = options(inside)
                            max_link_capacity=optional_values.get("max_link_capacity", max_link_capacity)
                            if max_link_capacity is not None:
                                max_link_capacity = int(max_link_capacity)
                        text_value = Connection(zone1, zone2, max_link_capacity)
                        map.add_connection(text_value)
                        # instanciar connection
                    # procesar drones
                    elif key == "nb_drones":
                        nb_drones = int(text_value)
                # procesar zonas
                    elif key in ("start_hub", "hub", "end_hub"):
                        color = None
                        zone_type = None
                        max_drones = None
                        before, _, after = text_value.partition("[")
                        before = before.strip()
                        text_values = before.split()
                        zone_name=text_values[0] 
                        start_x=int(text_values[1].strip())
                        start_y=int(text_values[2].strip())
                        if after:
                            inside = after.replace("]", "").strip()
                            optional_values = options(inside)
                            color=optional_values.get("color", color)
                            zone_type=optional_values.get("zone", zone_type)
                            max_drones=optional_values.get("max_drones", max_drones)
                            if max_drones is not None:
                                max_drones = int(max_drones)
                        zona = Zone(zone_name, (start_x, start_y), zone_type, color, max_drones)
                        map.zones[zone_name] = zona
                        if key == "start_hub":
                            start_zone = zone_name
                        # instanciar zona
        # instanciar drones
        if nb_drones > 0 and start_zone:
            for i in range(1, nb_drones + 1):
                id_dron = f"D{i}" 
                nuevo_dron = Drone(id_dron, start_zone) 
                # drones_lista.append(nuevo_dron)
                map.add_drone(nuevo_dron)

    except Exception as e:
        print("ERROR: Error en parseo")
        print(f"ERROR: Error en parseo: {e}")
        return None
            

    return map        

