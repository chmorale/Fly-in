#!/usr/bin/env python3

from map import Map
from zones import Zone
from drones import Drone
from connections import Connection


def options(text: str) -> dict:
    values = {}
    blocks = text.replace(",", " ").split()

    for block in blocks:
        if "=" in block:
            key_b, _, value_b = block.partition("=")
            values[key_b.strip()] = value_b.strip()
    return values


def parser(filepath: str) -> Map | None:
    map_obj: Map = Map()
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
                        text_values = before.split("-")
                        if len(text_values) == 2:
                            zone1 = text_values[0].strip()
                            zone2 = text_values[1].strip()
                            # Validación de existencia en el mapa actual
                            if (
                                zone1 not in map_obj.zones
                                or zone2 not in map_obj.zones
                            ):
                                raise ValueError("No se puede crear la "
                                                 "conexión: una o ambas "
                                                 "zonas no existen en el mapa "
                                                 f"('{zone1}' - '{zone2}'). "
                                                 "Asegúrate de definir las "
                                                 "zonas antes."
                                                 )
                        else:
                            continue
                        if after:
                            inside = after.replace("]", "").strip()
                            optional_values = options(inside)
                            if "max_link_capacity" in optional_values:
                                max_link_capacity = int(
                                    optional_values["max_link_capacity"])
                            # if max_link_capacity is not None:
                                # max_link_capacity = int(max_link_capacity)
                        text_value = Connection(zone1,
                                                zone2,
                                                max_link_capacity
                                                )
                        map_obj.add_connection(text_value)
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
                        # Validación longitud mínima antes de acceder a índices
                        if len(text_values) < 3:
                            raise ValueError("Faltan argumentos en la "
                                             "definición de la zona: "
                                             f"'{before}'")
                        zone_name = text_values[0]
                        start_x = int(text_values[1])
                        start_y = int(text_values[2])
                        if after:
                            inside = after.replace("]", "").strip()
                            optional_values = options(inside)
                            if "color" in optional_values:
                                color = optional_values["color"]
                            if "zone" in optional_values:
                                zone_type = optional_values["zone"]
                            if "max_drones" in optional_values:
                                max_drones = int(optional_values["max_drones"])

                        zona = Zone(zone_name,
                                    (start_x, start_y),
                                    zone_type,
                                    color,
                                    max_drones
                                    )
                        map_obj.add_zone(zona)
                        # instanciar zona
        # instanciar drones
        if nb_drones > 0 and not start_zone:
            raise ValueError("No se ha definido una zona de salida "
                             "('start_hub') para los drones.")

        if nb_drones <= 0:
            raise ValueError("El número de drones ('nb_drones')"
                             " debe ser mayor que cero.")

        assert start_zone is not None

        for i in range(1, nb_drones + 1):
            nuevo_dron = Drone(f"D{i}", start_zone) 
            # drones_lista.append(nuevo_dron)
            map_obj.add_drone(nuevo_dron)

    except FileNotFoundError:
        print(f"ERROR: El archivo '{filepath}' no existe.")
        return None

    except PermissionError:
        print(f"ERROR: No hay permisos para leer el archivo '{filepath}'.")
        return None

    except (ValueError, IndexError, KeyError) as e:
        print(f"ERROR: Formato incorrecto en el archivo de mapa. Detalle: {e}")
        return None

    except Exception as e:
        print(f"ERROR: Ocurrió un error inesperado durante el parseo: {e}")
        return None

    return map_obj

