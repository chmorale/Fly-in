#!/usr/bin/env python3

from map import Map
from zones import Zone
from drones import Drone
from connections import Connection


VALID_ZONE_TYPES = {"normal", "blocked", "restricted", "priority"}


def options(text: str) -> dict[str, str]:
    """Parse a bracket options block into a key/value dict.

    Args:
        text: Content inside the bracket block, e.g.
            'color=green max_drones=2'.

    Returns:
        Dict mapping option names to their string values.
    """
    values: dict[str, str] = {}
    blocks = text.replace(",", " ").split()

    for block in blocks:
        if "=" in block:
            key_b, _, value_b = block.partition("=")
            values[key_b.strip()] = value_b.strip()
    return values


def parser(filepath: str) -> Map | None:
    """Read and validate a map file and return a Map object.

    Args:
        filepath: Path to the map configuration file.

    Returns:
        A fully initialised Map, or None if parsing failed.
    """
    map_obj: Map = Map()
    nb_drones = 0
    line_num = 0
    seen_connections: set = set()
    first_data_line = True
    try:
        with open(filepath) as f:
            for idx, line in enumerate(f, start=1):
                line_num = idx
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                if ":" in line:
                    key, _, text_value = line.partition(":")
                    key = key.strip()
                    text_value = text_value.strip()

                    # Verificar primera línea de datos obligatoria
                    if first_data_line:
                        first_data_line = False
                        if key != "nb_drones":
                            raise ValueError(
                                "La primera línea de datos debe especificar "
                                f"'nb_drones'. Encontrado: '{key}'"
                            )

                    if key == "connection":
                        max_link_capacity = 1
                        zone1 = zone2 = ""
                        before, _, after = text_value.partition("[")
                        before = before.strip()
                        text_values = before.split("-")
                        if len(text_values) == 2:
                            zone1 = text_values[0].strip()
                            zone2 = text_values[1].strip()
                            if (
                                zone1 not in map_obj.zones or
                                zone2 not in map_obj.zones
                            ):
                                raise ValueError("Una o ambas zonas de la "
                                                 f"conexión '{zone1} - "
                                                 f"{zone2}'"
                                                 " no han sido declaradas.")
                            pair = frozenset({zone1, zone2})
                            if pair in seen_connections:
                                raise ValueError(
                                    f"Conexión duplicada: '{zone1}-{zone2}'"
                                )
                            seen_connections.add(pair)
                        else:
                            raise ValueError("Formato de conexión inválido. "
                                             f"Encontrado: '{before}'")

                        if after:
                            inside = after.replace("]", "").strip()
                            optional_values = options(inside)
                            if "max_link_capacity" in optional_values:
                                max_link_capacity = int(
                                    optional_values["max_link_capacity"])
                                if max_link_capacity <= 0:
                                    raise ValueError(
                                        "max_link_capacity debe ser un "
                                        "entero positivo, encontrado: "
                                        f"'{max_link_capacity}'"
                                    )

                        conn = Connection(zone1, zone2, max_link_capacity)
                        map_obj.add_connection(conn)

                    elif key == "nb_drones":
                        nb_drones = int(text_value)

                    elif key in ("start_hub", "hub", "end_hub"):
                        color = None
                        zone_type = key
                        zone_access = "normal"
                        # start/end hubs have unlimited capacity
                        if zone_type in ("start_hub", "end_hub"):
                            max_drones = None
                        else:
                            max_drones = 1
                        before, _, after = text_value.partition("[")
                        before = before.strip()
                        text_values = before.split()

                        if len(text_values) < 3:
                            raise ValueError("Faltan argumentos en la "
                                             f"zona: '{before}'")
                        zone_name = text_values[0]

                        # Validar restricciones de caracteres en nombres
                        if "-" in zone_name:
                            raise ValueError("El nombre de la zona no puede "
                                             f"contener guiones: '"
                                             f"{zone_name}'")
                        if " " in zone_name:
                            raise ValueError("El nombre de la zona no puede "
                                             f"contener espacios: '"
                                             f"{zone_name}'")
                        try:
                            start_x = int(text_values[1])
                            start_y = int(text_values[2])
                        except ValueError:
                            raise ValueError("Coordenadas no enteras en "
                                             f"'{zone_name}'")

                        if zone_name in map_obj.zones:
                            raise ValueError("Nombres duplicados no "
                                             "permitidos:"
                                             f" '{zone_name}'")

                        if after:
                            inside = after.replace("]", "").strip()
                            optional_values = options(inside)
                            if "color" in optional_values:
                                color = optional_values["color"]
                            if "zone" in optional_values:
                                zone_access = optional_values["zone"]
                                if zone_access not in VALID_ZONE_TYPES:
                                    raise ValueError(
                                        f"Tipo de zona inválido: "
                                        f"'{zone_access}'. Permitidos: "
                                        f"{VALID_ZONE_TYPES}"
                                    )
                            if ("max_drones" in optional_values and
                                    zone_type not in ("start_hub", "end_hub")):
                                max_drones = int(optional_values["max_drones"])
                                if max_drones <= 0:
                                    raise ValueError(
                                        "max_drones debe ser un entero "
                                        "positivo, encontrado: "
                                        f"'{max_drones}'"
                                    )

                        zona = Zone(zone_name,
                                    (start_x, start_y),
                                    zone_type,
                                    color,
                                    max_drones,
                                    zone_access
                                    )
                        map_obj.add_zone(zona)

        if nb_drones <= 0:
            raise ValueError("El número de drones debe ser mayor que cero.")
        if not map_obj.start_zone:
            raise ValueError("Falta definir la zona 'start_hub'.")
        if not map_obj.end_zone:
            raise ValueError("Falta definir la zona 'end_hub'.")

        for i in range(1, nb_drones + 1):
            nuevo_dron = Drone(f"D{i}", map_obj.start_zone)
            map_obj.add_drone(nuevo_dron)

        start_zone_obj = map_obj.get_zone(map_obj.start_zone)
        start_zone_obj.current_drones = nb_drones
        map_obj.nb_drones = nb_drones

        map_obj.min_x = min(z.coordinates[0] for z in map_obj.zones.values())

        map_obj.max_x = max(z.coordinates[0] for z in map_obj.zones.values())

        map_obj.min_y = min(z.coordinates[1] for z in map_obj.zones.values())

        map_obj.max_y = max(z.coordinates[1] for z in map_obj.zones.values())

    except FileNotFoundError:
        print(f"ERROR: El archivo '{filepath}' no existe.")
        return None
    except PermissionError:
        print(f"ERROR: Sin permisos para leer '{filepath}'.")
        return None
    except (ValueError, IndexError, KeyError) as e:
        print(f"ERROR: [Línea {line_num}] Formato incorrecto del mapa. "
              f"Detalle: {e}")
        return None
    except Exception as e:
        print(f"ERROR: Error inesperado en línea {line_num}: {e}")
        return None

    return map_obj
