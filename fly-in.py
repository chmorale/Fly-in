#!/usr/bin/env python3

import os
import sys
import math
import pygame
from parser import parser


# ==============================================================================
# CONSTANTES GRÁFICAS (COLORES RGB)
# ==============================================================================
COLOR_FONDO = (30, 30, 30)      # Gris muy oscuro para evitar fatiga visual
COLOR_LINEA = (150, 150, 150)   # Gris claro para los caminos/conexiones
COLOR_TEXTO = (255, 255, 255)   # Blanco para las etiquetas de texto

# Colores de las zonas según el enunciado o su estado
COLOR_VERDE = (46, 204, 113)    # Para hubs de inicio/fin o alta capacidad
COLOR_ROJO = (231, 76, 60)      # Para zonas saturadas o bloqueadas
COLOR_AMARILLO = (241, 196, 15)  # Para zonas con restricciones
COLOR_AZUL = (52, 152, 219)     # Para los drones y rutas prioritarias
COLOR_PURPURA = (155, 89, 182)  # Para zonas priority
COLOR_GRIS = (80, 80, 80)       # Para zonas blocked
COLOR_CYAN = (0, 220, 255)      # Color de los drones en espera

ACCESS_COLORS = {
    "normal":     COLOR_AZUL,
    "restricted": COLOR_ROJO,
    "priority":   COLOR_PURPURA,
    "blocked":    COLOR_GRIS,
}


def draw_simulation(
    surface: pygame.Surface,
    map_obj: object,
    font: pygame.font.Font,
    escala: float,
    frame_count: int,
    tick: int
) -> None:
    """Draw zones, connections, drones and HUD each frame."""
    MARGIN = 100
    ZONE_RADIUS = 22

    def to_screen(coords: tuple) -> tuple:
        """Convert grid coordinates to screen pixel position."""
        x = int((coords[0] - map_obj.min_x) * escala) + MARGIN  # type: ignore
        y = int((coords[1] - map_obj.min_y) * escala) + MARGIN  # type: ignore
        return (x, y)

    # --- Connections ---
    drawn: set = set()
    for conns in map_obj.connections.values():  # type: ignore
        for conn in conns:
            key = frozenset({conn.zone1, conn.zone2})
            if key in drawn:
                continue
            drawn.add(key)
            z1 = map_obj.zones[conn.zone1]  # type: ignore
            z2 = map_obj.zones[conn.zone2]  # type: ignore
            p1 = to_screen(z1.coordinates)
            p2 = to_screen(z2.coordinates)
            width = max(2, conn.max_capacity * 2)
            color = (220, 130, 40) if conn.current_drones > 0 else COLOR_LINEA
            pygame.draw.line(surface, color, p1, p2, width)

    # --- Zones ---
    for zone_name, zone in map_obj.zones.items():  # type: ignore
        pos = to_screen(zone.coordinates)

        if zone.zone_type == "start_hub":
            color = COLOR_VERDE
        elif zone.zone_type == "end_hub":
            color = COLOR_AMARILLO
        else:
            color = ACCESS_COLORS.get(zone.zone_access, COLOR_AZUL)

        pygame.draw.circle(surface, color, pos, ZONE_RADIUS)
        pygame.draw.circle(surface, COLOR_TEXTO, pos, ZONE_RADIUS, 2)

        # Capacity ring: green → red as zone fills up
        if zone.zone_type not in ("start_hub", "end_hub") and zone.max_drones:
            ratio = min(zone.current_drones / zone.max_drones, 1.0)
            ring_color = (int(255 * ratio), int(255 * (1.0 - ratio)), 0)
            pygame.draw.circle(surface, ring_color, pos, ZONE_RADIUS + 5, 3)

        # Zone name
        lbl = font.render(zone_name, True, COLOR_TEXTO)
        lbl_x = pos[0] - lbl.get_width() // 2
        surface.blit(lbl, (lbl_x, pos[1] + ZONE_RADIUS + 5))

        # Occupancy
        if zone.zone_type in ("start_hub", "end_hub"):
            occ_str = f"{zone.current_drones}/∞"
        else:
            occ_str = f"{zone.current_drones}/{zone.max_drones}"
        occ_lbl = font.render(occ_str, True, COLOR_TEXTO)
        surface.blit(occ_lbl, (
            pos[0] - occ_lbl.get_width() // 2,
            pos[1] + ZONE_RADIUS + 17
        ))

    # --- Drones (orbiting their zone — the fun part) ---
    zone_drone_index: dict = {}

    for drone in map_obj.drones.values():  # type: ignore
        if not drone.current_zone:
            continue

        zone = map_obj.zones.get(drone.current_zone)  # type: ignore
        if not zone:
            continue

        center = to_screen(zone.coordinates)
        idx = zone_drone_index.get(drone.current_zone, 0)
        zone_drone_index[drone.current_zone] = idx + 1

        if drone.status == "arrived":
            # Drones that arrived shown as small green dots at end hub
            offset_x = (idx % 5) * 10 - 20
            offset_y = (idx // 5) * 10
            dot_pos = (center[0] + offset_x, center[1] + offset_y)
            pygame.draw.circle(surface, COLOR_VERDE, dot_pos, 4)
            continue

        if drone.status == "in_transit" and drone.target_zone_obj:
            # In-transit: shown at midpoint of the connection
            t_pos = to_screen(drone.target_zone_obj.coordinates)
            drone_pos = (
                (center[0] + t_pos[0]) // 2,
                (center[1] + t_pos[1]) // 2,
            )
            drone_color = COLOR_AMARILLO
        else:
            # Waiting: orbit around zone center — the fun touch!
            n = max(zone.current_drones + zone.reserved_spaces, 1)
            phase = idx * (2 * math.pi / n)
            angle = frame_count * 0.04 + phase
            orbit_r = ZONE_RADIUS + 14
            drone_pos = (
                int(center[0] + orbit_r * math.cos(angle)),
                int(center[1] + orbit_r * math.sin(angle)),
            )
            drone_color = COLOR_CYAN

        pygame.draw.circle(surface, drone_color, drone_pos, 5)
        pygame.draw.circle(surface, COLOR_TEXTO, drone_pos, 5, 1)
        id_lbl = font.render(drone.id_dron, True, drone_color)
        surface.blit(id_lbl, (drone_pos[0] + 7, drone_pos[1] - 5))

    # --- HUD ---
    arrived = sum(
        1 for d in map_obj.drones.values()  # type: ignore
        if d.status == "arrived"
    )
    nb = map_obj.nb_drones  # type: ignore
    hud = font.render(
        f"Tick: {tick}   Delivered: {arrived}/{nb}",
        True, COLOR_TEXTO
    )
    surface.blit(hud, (10, 10))


filepath = sys.argv[1] if len(sys.argv) > 1 else "my_map.txt"
map_obj = parser(filepath)

if map_obj and map_obj.start_zone and map_obj.end_zone:

    rango_x = map_obj.max_x - map_obj.min_x
    rango_y = map_obj.max_y - map_obj.min_y

    escala_x = 600 / max(rango_x, 1)
    escala_y = 600 / max(rango_y, 1)
    escala = min(escala_x, escala_y)
    escala = min(escala, 120)

    ancho_ventana = int((rango_x * escala) + 200)
    alto_ventana = int((rango_y * escala) + 200)

    pygame.init()
    pantalla = pygame.display.set_mode((ancho_ventana, alto_ventana))
    pygame.display.set_caption("Fly-in Drone Simulator")
    reloj = pygame.time.Clock()
    tiempo_acumulado = 0.0
    font = pygame.font.SysFont("monospace", 11)
    frame_count = 0

    # Verificación inicial de conectividad física en el mapa
    initial_route = map_obj.find_dynamic_route(
        map_obj.start_zone,
        map_obj.end_zone
    )

    if not initial_route:
        print("ERROR: The map does not have a viable physical connection "
              "between start and end hubs.")
        pygame.quit()
        sys.exit(1)

    tick = 0
    total_drones = map_obj.nb_drones
    log_outputs: list[str] = []
    ejecutando = True

    while ejecutando:
        # 1. GESTIÓN DE EVENTOS (Para poder cerrar la ventana)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                ejecutando = False

        # 2. CONTROL DEL TIEMPO: Mide los milisegundos desde el último ciclo
        milisegundos_pasados = reloj.tick(60)
        tiempo_acumulado += milisegundos_pasados

        # 3. LÓGICA DE LA SIMULACIÓN: Se dispara solo cuando pasa 1 segundo
        if tiempo_acumulado >= 1000:

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
                tiempo_acumulado -= 1000
                continue  # evita que el tick extra borre el resumen

            tick += 1
            print("\033[2J\033[H", end="")

            print("==================================================")
            print(f"  SIMULATION STATUS - TICK {tick}                 ")
            print("==================================================")
            print("\n[ZONES OCCUPATION]")

            for zone_name, zone in map_obj.zones.items():
                curr = zone.current_drones
                mx = zone.max_drones

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

                z_type = zone.zone_type or "hub"
                prefix = f"[{z_type.upper()}]"
                print(f"{prefix:<13} {zone_name:<12}: [{bar}] {cap_str}")

            sys.stdout.flush()

            print("\n[ACTIVE DRONES STATUS]")
            for drone_id, drone in map_obj.drones.items():
                print(f" -> Drone {drone_id:<3}: State = {drone.status:<11} | "
                      f"Loc = {drone.current_zone}")

            print("\n" + "-" * 50)
            print("[TURN MOVEMENTS LOG (STRICT FORMAT)]")

            any_movement_this_tick = False
            tick_movements: list = []

            for drone in map_obj.drones.values():
                if drone.status == "arrived":
                    continue

                # Si el dron ya está volando dentro de un pasillo restringido
                if (drone.status == "in_transit" and
                        drone.transit_ticks_left > 0):
                    drone.transit_ticks_left -= 1
                    any_movement_this_tick = True
                    # Aterrizaje obligatorio al vencer el tiempo
                    if drone.transit_ticks_left == 0:
                        if drone.assigned_connection:
                            drone.assigned_connection.exit_connection()
                        drone.target_zone_obj.release_reservation()
                        drone.current_zone = drone.target_zone_obj.zone_name
                        drone.target_zone_obj.enter_zone()

                        if drone.current_zone == map_obj.end_zone:
                            drone.status = "arrived"
                        else:
                            drone.status = "waiting"

                        log_str = f"{drone.id_dron}-{drone.current_zone}"
                        tick_movements.append(log_str)
                    continue

                if drone.current_zone and map_obj.end_zone:
                    dynamic_path = map_obj.find_dynamic_route(
                        drone.current_zone,
                        map_obj.end_zone
                    )
                else:
                    dynamic_path = []

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
                    if (target_zone.zone_access == "restricted" and
                            not target_zone.has_space_with_reservation()):
                        continue

                    any_movement_this_tick = True
                    connection.enter_connection()

                    if target_zone.zone_access == "restricted":
                        map_obj.zones[drone.current_zone].exit_zone()
                        target_zone.reserve_space()
                        drone.status = "in_transit"
                        drone.transit_ticks_left = 1
                        drone.assigned_connection = connection
                        drone.target_zone_obj = target_zone

                        conn_str = f"{drone.current_zone}-{next_zone_name}"
                        log_str = f"{drone.id_dron}-{conn_str}"
                        tick_movements.append(log_str)
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
                        tick_movements.append(log_str)

            if tick_movements:
                tick_line = " ".join(tick_movements)
                print(tick_line)
                log_outputs.append(tick_line)

            # Control de Deadlock estricto
            if not any_movement_this_tick and arrived_count < total_drones:
                print(f"\n[FATAL] Deadlock detectado en el Tick {tick}. "
                      "La simulación se ha colapsado.")
                ejecutando = False

            sys.stdout.flush()
            tiempo_acumulado -= 1000

        # Renderizado (cada frame, independiente del tick de simulación)
        frame_count += 1
        pantalla.fill(COLOR_FONDO)
        draw_simulation(pantalla, map_obj, font, escala, frame_count, tick)
        pygame.display.flip()

    pygame.quit()

else:
    print("ERROR: No se pudo cargar el mapa o faltan zonas start/end.")
