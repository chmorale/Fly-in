#!/usr/bin/env python3

from parser import parser
import os
import time


map_obj = parser("my_map.txt")

if map_obj and map_obj.start_zone and map_obj.end_zone:

    # 1. Verificación inicial de conectividad física en el mapa
    initial_route = map_obj.find_dynamic_route(
        map_obj.start_zone,
        map_obj.end_zone
    )

    if not initial_route:
        print("ERROR: The map does not have a viable physical connection "
              "between start and end hubs.")
    else:
        # Inicializamos los atributos dinámicos extendidos en los objetos drone
        for drone in map_obj.drones.values():
            drone.status = "waiting"
            drone.transit_ticks_left = 0
            drone.assigned_connection = None
            drone.target_zone_obj = None

        tick = 0
        total_drones = map_obj.nb_drones
        log_outputs = []

        while True:
            arrived_count = sum(
                1 for d in map_obj.drones.values() if d.status == "arrived"
            )
            if arrived_count == total_drones:
                os.system('clear' if os.name != 'nt' else 'cls')
                print("\n==================================================")
                print("            FLY-IN DRONE SIMULATION               ")
                print("==================================================")
                print(f"\nSimulation finished successfully in {tick} ticks!")
                print("\n[HISTORIAL DE LOGS EMITIDOS EN FORMATO ESTRICTO]:")
                for log in log_outputs:
                    print(log)
                break

            tick += 1
            os.system('clear' if os.name != 'nt' else 'cls')

            print("==================================================")
            print(f"  SIMULATION STATUS - TICK {tick}                 ")
            print("==================================================")
            print("\n[ZONES OCCUPATION]")

            for zone_name, zone in map_obj.zones.items():
                curr = zone.current_drones
                mx = zone.max_drones
                # Excepción del enunciado:
                # salida y meta tienen capacidad infinita
                if zone.zone_type in ("start_hub", "end_hub"):
                    mx = None

                if mx is None:
                    bar = "████████████████████"
                    cap_str = f"{curr}/∞"
                else:
                    filled_length = int(round(20 * curr / mx)) if mx > 0 else 0
                    filled_length = min(filled_length, 20)
                    bar = "█" * filled_length + "░" * (20 - filled_length)
                    cap_str = f"{curr}/{mx}"

                z_type = (
                    zone.zone_type
                    if zone.zone_type is not None
                    else "hub"
                )
                prefix = f"[{z_type.upper()}]"
                print(f"{prefix:<13} {zone_name:<12}: [{bar}] {cap_str}")

            print("\n[ACTIVE DRONES STATUS]")
            for drone_id, drone in map_obj.drones.items():
                print(f" -> Drone {drone_id:<3}: State = {drone.status:<11} | "
                      f"Loc = {drone.current_zone}")

            print("\n" + "-" * 50)
            print("[TURN MOVEMENTS LOG (STRICT FORMAT)]")

            authorized_movements = []
            any_movement_this_tick = False

            for drone in map_obj.drones.values():
                if drone.status == "arrived":
                    continue

                # Si el dron ya está volando dentro de un pasillo restringido
                if (drone.status == "in_transit" and
                        drone.transit_ticks_left > 0):
                    drone.transit_ticks_left -= 1
                    any_movement_this_tick = True
                    # Obligación de aterrizar de forma mandatoria
                    #  al vencer el tiempo
                    if drone.transit_ticks_left == 0:
                        # Libera la conexión física aérea de inmediato
                        if drone.assigned_connection:
                            drone.assigned_connection.exit_connection()

                        map_obj.zones[drone.current_zone].exit_zone()
                        drone.current_zone = drone.target_zone_obj.zone_name
                        drone.target_zone_obj.enter_zone()

                        if drone.current_zone == map_obj.end_zone:
                            drone.status = "arrived"
                        else:
                            drone.status = "waiting"

                        log_str = f"{drone.id_dron}-{drone.current_zone}"
                        print(log_str)
                        log_outputs.append(log_str)
                    continue

                # Cálculo de pathfinding dinámico individual
                # por saturación de nodos
                dynamic_path = map_obj.find_dynamic_route(
                    drone.current_zone,
                    map_obj.end_zone
                )
                if not dynamic_path or len(dynamic_path) < 2:
                    continue

                next_zone_name = dynamic_path[1]
                target_zone = map_obj.zones[next_zone_name]

                # Localizar la conexión correspondiente
                connection = None
                for conn in map_obj.connections[drone.current_zone]:
                    if (conn.get_destination_from(drone.current_zone) ==
                            next_zone_name):
                        connection = conn
                        break

                if not connection:
                    continue

                # Validar capacidades (meta/end_hub ignora el límite máximo)
                has_zone_space = (target_zone.zone_type == "end_hub" or
                                  target_zone.has_space())

                can_fly = connection.has_space() and has_zone_space

                if can_fly:
                    any_movement_this_tick = True
                    connection.enter_connection()

                    if target_zone.zone_access == "restricted":
                        drone.status = "in_transit"
                        drone.transit_ticks_left = 1
                        # 2 turnos totales (este turno + el de caída)
                        drone.assigned_connection = connection
                        drone.target_zone_obj = target_zone

                        # Formato de log especial para conexiones restringidas
                        conn_str = f"{drone.current_zone}-{next_zone_name}"
                        log_str = f"{drone.id_dron}-{conn_str}"
                        print(log_str)
                        log_outputs.append(log_str)
                    else:
                        # Movimiento normal instantáneo de 1 turno
                        connection.exit_connection()
                        map_obj.zones[drone.current_zone].exit_zone()
                        drone.current_zone = next_zone_name
                        target_zone.enter_zone()

                        if drone.current_zone == map_obj.end_zone:
                            drone.status = "arrived"
                        else:
                            drone.status = "waiting"

                        log_str = f"{drone.id_dron}-{drone.current_zone}"
                        print(log_str)
                        log_outputs.append(log_str)

            # Control de Deadlock estricto
            if not any_movement_this_tick and arrived_count < total_drones:
                print(f"\n[FATAL] Deadlock detectado en el Tick {tick}. "
                      "La simulación se ha colapsado.")
                break

            time.sleep(1.0)
