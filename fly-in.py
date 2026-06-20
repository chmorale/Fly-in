#!/usr/bin/env python3

import os
import sys
import pygame
from parser import parser


# ==============================================================================
# CONSTANTES GRÁFICAS (COLORES RGB)
# ==============================================================================
COLOR_FONDO = (30, 30, 30)     # Gris muy oscuro para evitar fatiga visual
COLOR_LINEA = (150, 150, 150)  # Gris claro para los caminos/conexiones
COLOR_TEXTO = (255, 255, 255)  # Blanco para las etiquetas de texto

# Colores de las zonas según el enunciado o su estado
COLOR_VERDE = (46, 204, 113)   # Para hubs de inicio/fin o alta capacidad
COLOR_ROJO = (231, 76, 60)    # Para zonas saturadas o bloqueadas
COLOR_AMARILLO = (241, 196, 15)   # Para zonas con restricciones
COLOR_AZUL = (52, 152, 219)   # Para los drones y rutas prioritarias

map_obj = parser("my_map.txt")

if map_obj and map_obj.start_zone and map_obj.end_zone:

    assert map_obj is not None

    rango_x = map_obj.max_x - map_obj.min_x
    rango_y = map_obj.max_y - map_obj.min_y

    escala_x = 600 / max(rango_x, 1)
    escala_y = 600 / max(rango_y, 1)
    escala = min(escala_x, escala_y)
    escala = min(escala, 120)

    ancho_ventana = int((rango_x * escala) + 200)
    alto_ventana = int((rango_y * escala) + 200)

    # Inicializa formalmente los módulos internos de Pygame
    pygame.init()


# Herramienta para medir el paso del tiempo y limitar los fotogramas por
#  segundo (FPS)
reloj = pygame.time.Clock()

# Acumulador de milisegundos para saber cuándo ha transcurrido
# exactamente 1 segundo (tick de simulación)
tiempo_acumulado = 0.0

# Abre la ventana con el tamaño dinámico calculado
pantalla = pygame.display.set_mode((ancho_ventana, alto_ventana))

# Define el título que se verá en la barra superior de la ventana
pygame.display.set_caption("Fly-in Drone Simulator")

if map_obj and map_obj.start_zone and map_obj.end_zone:

    # 1. Verificación inicial de conectividad física en el mapa
    initial_route = map_obj.find_dynamic_route(
        map_obj.start_zone,
        map_obj.end_zone
    )

    if not initial_route:
        print("ERROR: The map does not have a viable physical connection "
              "between start and end hubs.")

    # Inicializamos los atributos dinámicos extendidos en los objetos drone
    for drone in map_obj.drones.values():
        drone.status = "waiting"
        drone.transit_ticks_left = 0
        drone.assigned_connection = None
        drone.target_zone_obj = None

    tick = 0
    total_drones = map_obj.nb_drones
    log_outputs = []

ejecutando = True

while ejecutando:
    # 1. GESTIÓN DE EVENTOS (Para poder cerrar la ventana)
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False

    # 2. CONTROL DEL TIEMPO: Mide los milisegundos que han pasado desde
    #  el último ciclo
    milisegundos_pasados = reloj.tick(60)
    tiempo_acumulado += milisegundos_pasados

    # 3. LÓGICA DE LA SIMULACIÓN: Se dispara solo cuando pasa 1 segundo entero
    if tiempo_acumulado >= 1000:
        # Aquí dentro es donde vas a mover tu código antiguo de los drones

        assert map_obj is not None
        # while True:
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
            ejecutando = False

        tick += 1
        print("\033[2J\033[H", end="")

        print("==================================================")
        print(f"  SIMULATION STATUS - TICK {tick}                 ")
        print("==================================================")
        print("\n[ZONES OCCUPATION]")

        for zone_name, zone in map_obj.zones.items():
            assert zone is not None
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
                ratio = curr / mx if mx else 0
                filled_length = min(int(round(20 * ratio)), 20)
                bar = (
                    f"{'█' * filled_length}"
                    f"{'░' * (20 - filled_length)}"
                )
                cap_str = f"{curr}/{mx}"

            z_type = (
                zone.zone_type
                if zone.zone_type is not None
                else "hub"
            )
            prefix = f"[{z_type.upper()}]"
            print(f"{prefix:<13} {zone_name:<12}: [{bar}] {cap_str}")

        sys.stdout.flush()

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

            assert map_obj is not None

            if drone.current_zone and map_obj.end_zone:
                # Si end_zone es un objeto, extraemos su nombre
                # (o dejamos map_obj.end_zone si ya es un str)
                destino = getattr(map_obj.end_zone, 'name', map_obj.end_zone)

                dynamic_path = map_obj.find_dynamic_route(
                    str(drone.current_zone),
                    str(destino)
                )

            if not dynamic_path or len(dynamic_path) < 2:
                continue

            next_zone_name = dynamic_path[1]
            target_zone = map_obj.zones[next_zone_name]

            assert target_zone is not None

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
            ejecutando = False

        sys.stdout.flush()

    # Una vez ejecutada la lógica, restamos los 1000 milisegundos para
    # el siguiente segundo
    tiempo_acumulado -= 1000

# Creación de la ventana y el reloj de control de FPS
    pantalla = pygame.display.set_mode((ancho_ventana, alto_ventana))
    pygame.display.set_caption("Fly-in Simulation")
    reloj = pygame.time.Clock()

    # Bucle principal de la interfaz gráfica
    ejecutando = True
    while ejecutando:
        # Gestión de eventos (para poder cerrar la ventana)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                ejecutando = False

        # Limpiar la pantalla con el color de fondo
        pantalla.fill(COLOR_FONDO)

        # Actualizar el contenido de la ventana
        pygame.display.flip()

        # Controlar la velocidad del bucle (60 FPS)
        reloj.tick(60)

    pygame.quit()
