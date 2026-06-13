#!/usr/bin/env python3

from parser import parser


map_obj = parser("my_map.txt")

if map_obj and map_obj.start_zone and map_obj.end_zone:

    optimal_route = map_obj.find_shortest_route(map_obj.start_zone,
                                                map_obj.end_zone)

    if not list(optimal_route):
        print("ERROR: The map does not have a viable physical connection "
              "between start and end hubs.")
    else:
        print("Optimal route calculated for drones: "
              f"{' -> '.join(optimal_route)}")

        # 2. Assign the computed path and final destination to each drone in
        # the map
        for drone in map_obj.drones.values():
            drone.set_route(optimal_route)
            drone.status = "waiting"

        print("\n--- Starting Simulation ---")
        tick = 0
        total_drones = len(map_obj.drones)

        while True:
            # Contamos cuántos drones han llegado ya al final
            arrived_count = sum(
                1 for d in map_obj.drones.values() if d.status == "arrived"
            )
            # Si todos los drones han llegado, la simulación ha terminado OK
            if arrived_count == total_drones:
                print(f"\nSimulation finished successfully in {tick} ticks!")
                break

            tick += 1
            print(f"\n[Tick {tick}]")

            # Procesamos el movimiento de cada dron en este turno
            for drone in map_obj.drones.values():
                if drone.status == "arrived":
                    continue  # Este dron ya terminó, no hace nada

                # Averiguamos a qué zona le toca ir ahora
                next_zone = drone.get_next_target_zone()

                if next_zone:
                    # Buscamos el objeto Connection que une zona actual
                    #  y la siguiente
                    # (Buscamos en las conexiones de la zona actual del dron)
                    current_connection = None
                    for conn in map_obj.connections[drone.current_zone]:
                        dest_zone = conn.get_destination_from(
                            drone.current_zone
                        )
                        if dest_zone == next_zone:
                            current_connection = conn
                            break

                    # Verificamos si la conexión física
                    # tiene espacio disponible
                    if current_connection and current_connection.has_space():
                        # Si venía de estar en tránsito, liberamos
                        # la conexión anterior
                        # (Nota: Para el primer movimiento desde
                        # start_hub no hace falta liberar)

                        # El dron entra en la nueva conexión (ocupa capacidad)
                        current_connection.enter_connection()

                        # Movemos al dron físicamente a la siguiente zona
                        drone.move_to(next_zone)

                        # Si el dron ha llegado a una zona intermedia
                        # pero aún tiene que seguir,
                        # liberamos la conexión inmediatamente
                        #  si consideramos movimientos instantáneos por turno
                        current_connection.exit_connection()

                        print(f"  -> Drone {drone.id_dron} moved to"
                              f"{next_zone} (Status: {drone.status})")
                    else:
                        # Si la conexión está saturada,
                        # el dron se queda esperando
                        drone.status = "waiting"
                        print(f"  .. Drone {drone.id_dron} is waiting"
                              f" at {drone.current_zone} (Traffic congestion)")
                else:
                    print(f"  .. Drone {drone.id_dron} "
                          "has no next target zone.")
