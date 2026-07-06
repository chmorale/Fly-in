#!/usr/bin/env python3

import os
import sys
import math
import pygame
from parser import Parser
from map import Map


# ============================================================================
# CONSTANTES GRÁFICAS (COLORES RGB)
# ============================================================================
COLOR_FONDO = pygame.Color("gray12")  # Gris muy oscuro evita fatiga visual
COLOR_LINEA = pygame.Color("gray59")  # Gris claro para los caminos/conexiones
COLOR_TEXTO = pygame.Color("white")   # Blanco para las etiquetas de texto

# Colores de las zonas según el enunciado o su estado
COLOR_VERDE = pygame.Color("green")  # Hubs de inicio/fin o alta capacidad
COLOR_ROJO = pygame.Color("red")  # Para zonas saturadas o bloqueadas
COLOR_AMARILLO = pygame.Color("yellow")  # Para zonas con restricciones
COLOR_AZUL = pygame.Color("blue")  # Para los drones y rutas prioritarias
COLOR_PURPURA = pygame.Color("purple")  # Para zonas priority
COLOR_GRIS = pygame.Color("gray31")  # Para zonas blocked
COLOR_CYAN = pygame.Color("cyan")  # Color de los drones en espera

ACCESS_COLORS = {
    "normal":     COLOR_AZUL,
    "restricted": COLOR_ROJO,
    "priority":   COLOR_PURPURA,
    "blocked":    COLOR_GRIS,
}


class Draw_simul:

    def __init__(self) -> None:
        pass

    @staticmethod
    def draw_simulation(
        surface: pygame.Surface,
        map_obj: Map,
        font: pygame.font.Font,
        fontg: pygame.font.Font,
        escala_x: float,
        escala_y: float,
        frame_count: int,
        tick: int,
        paused: bool = False,
        sim_speed: int = 1000
    ) -> None:
        """Draw zones, connections, drones and HUD each frame."""
        MARGIN = 150
        ZONE_RADIUS = 22

        def to_screen(coords: tuple) -> tuple:
            """Convert grid coordinates to screen pixel position."""
            x = int((coords[0] - map_obj.min_x) * escala_x) + MARGIN
            y = int((coords[1] - map_obj.min_y) * escala_y) + MARGIN
            return (x, y)

        # --- Connections ---
        drawn: set = set()
        for conns in map_obj.connections.values():
            for conn in conns:
                key = frozenset({conn.zone1, conn.zone2})
                if key in drawn:
                    continue
                drawn.add(key)
                z1 = map_obj.zones[conn.zone1]
                z2 = map_obj.zones[conn.zone2]
                p1 = to_screen(z1.coordinates)
                p2 = to_screen(z2.coordinates)
                width = max(2, conn.max_capacity * 2)
                color = (
                    pygame.Color("orange")
                    if conn.current_drones > 0
                    else COLOR_LINEA)
                pygame.draw.line(surface, color, p1, p2, width)

        # --- Zones ---
        for zone_name, zone in map_obj.zones.items():
            pos = to_screen(zone.coordinates)

            if zone.zone_color is not None:
                try:
                    color_zona = pygame.Color(zone.zone_color)
                except ValueError:
                    print(f"ERROR: color '{zone.zone_color}' ivalido.")
                    color_zona = ACCESS_COLORS.get(
                        zone.zone_access, COLOR_GRIS)
            else:
                color_zona = ACCESS_COLORS.get(zone.zone_access, COLOR_GRIS)
            pygame.draw.circle(surface, color_zona, pos, ZONE_RADIUS)
            pygame.draw.circle(surface, COLOR_TEXTO, pos, ZONE_RADIUS, 2)

            # Capacity ring: green → red as zone fills up
            if zone.zone_type not in (
                "start_hub",
                "end_hub"
            ) and zone.max_drones:
                ring_color = (
                    pygame.Color("red")
                    if zone.current_drones >= zone.max_drones
                    else pygame.Color("green"))
                pygame.draw.circle(
                    surface,
                    ring_color,
                    pos, ZONE_RADIUS + 5, 3)

            # Zone name y ocupación
            lbl = font.render(zone_name, True, COLOR_TEXTO)
            lbl_x = pos[0] - lbl.get_width() // 2
            surface.blit(lbl, (lbl_x, pos[1] + ZONE_RADIUS + 4))

        # --- Drones (orbiting their zone — the fun part) ---
        zone_drone_index: dict = {}

        for drone in map_obj.drones.values():
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
                drone_color = pygame.Color("gold")
            else:
                # Waiting: orbit around zone center — the fun touch!
                n = max(zone.current_drones + zone.reserved_spaces, 1)
                phase = idx * (2 * math.pi / n)
                angle = frame_count * 0.04 + phase
                orbit_r = ZONE_RADIUS + 14
                bounce = abs(math.sin(frame_count * 0.08 + phase)) * 8
                drone_pos = (
                    int(center[0] + orbit_r * math.cos(angle)),
                    int(center[1] + orbit_r * math.sin(angle) - bounce),
                )
                drone_color = pygame.Color("cyan")

            pygame.draw.circle(surface, drone_color, drone_pos, 5)
            pygame.draw.circle(surface, COLOR_TEXTO, drone_pos, 5, 1)
            id_lbl = font.render(drone.id_dron, True, drone_color)
            surface.blit(id_lbl, (drone_pos[0] + 7, drone_pos[1] - 5))

        # --- HUD ---
        arrived = sum(
            1 for d in map_obj.drones.values()
            if d.status == "arrived"
        )
        nb = map_obj.nb_drones
        hud = fontg.render(
            f"Tick: {tick}   Delivered: {arrived}/{nb}",
            True, COLOR_TEXTO
        )
        surface.blit(hud, (10, 10))

        estado = "⏸ PAUSED" if paused else f"▶ {sim_speed}ms/tick"
        hud2 = fontg.render(
            f"{estado}   [SPACE]=pausa  [→]=step  (clic aqui primero)",
            True, (200, 200, 100)
        )
        # surface.blit(hud2, (10, 26))
        surface.blit(hud2, (10, 10 + fontg.get_height() + 4))


class DroneSimulation:
    """Orchestrates the fly-in drone routing simulation."""

    def __init__(self, map_obj: Map) -> None:
        """Initialise simulation state, window and scaling.

        Args:
            map_obj: The parsed and validated map.
        """
        self.map_obj = map_obj
        self.clock = pygame.time.Clock()

        rango_x = map_obj.max_x - map_obj.min_x
        rango_y = map_obj.max_y - map_obj.min_y

        self.ancho_ventana = 1400
        self.alto_ventana = 800

        self.escala_x = min(
            (self.ancho_ventana - 300) / max(rango_x, 1), 250
        )
        self.escala_y = min(
            (self.alto_ventana - 300) / max(rango_y, 1), 250
        )

        pygame.init()
        self.pantalla = pygame.display.set_mode(
            (self.ancho_ventana, self.alto_ventana)
        )
        pygame.display.set_caption("Fly-in Drone Simulator")
        self.font = pygame.font.SysFont("monospace", 8)
        self.fontg = pygame.font.SysFont("Arial", 24)
        self.frame_count = 0

        # --- CONTROL DE SIMULACIÓN ---
        self.paused = False
        self.step_once = False

        self.tick = 0
        self.total_drones = map_obj.nb_drones
        self.log_outputs: list[str] = []
        self.ejecutando = True

    def handle_events(self) -> None:
        """Process pygame events: quit, pause, and manual step."""
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.ejecutando = False
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE:
                    self.paused = not self.paused
                elif evento.key == pygame.K_RIGHT:
                    self.step_once = True
                    self.paused = True

    def process_tick(self) -> None:
        """Advance the simulation by exactly one turn."""
        arrived_count = sum(
            1 for d in self.map_obj.drones.values()
            if d.status == "arrived"
        )
        if arrived_count == self.total_drones:
            os.system('clear' if os.name != 'nt' else 'cls')
            print("\n==================================================")
            print("            FLY-IN DRONE SIMULATION               ")
            print("==================================================")
            print(
                f"\nSimulation finished successfully in "
                f"{self.tick} ticks!"
            )
            print("\n[HISTORIAL DE LOGS EMITIDOS EN FORMATO ESTRICTO]:")
            for log in self.log_outputs:
                print(log)
            self.paused = True
            return  # antes era "continue"; acá cortamos el método

        self.tick += 1
        print("\033[2J\033[H", end="")

        print("==================================================")
        print(f"  SIMULATION STATUS - TICK {self.tick}                 ")
        print("==================================================")
        print("\n[ZONES OCCUPATION]")

        for zone_name, zone in self.map_obj.zones.items():
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

        print("\n[CONNECTIONS OCCUPATION]")
        con_set = set()
        for conns in self.map_obj.connections.values():
            for conn in conns:
                key = frozenset({conn.zone1, conn.zone2})
                if key in con_set:
                    continue
                con_set.add(key)

                curr = conn.current_drones
                mx = conn.max_capacity
                cap_str = f"{curr}/{mx}"
                print(f" -> {conn.zone1}-{conn.zone2}: {cap_str}")

        print("\n[ACTIVE DRONES STATUS]")
        for drone_id, drone in self.map_obj.drones.items():
            print(
                f" -> Drone {drone_id:<3}: State = {drone.status:<11} | "
                f"Loc = {drone.current_zone}"
            )

        print("\n" + "-" * 50)
        print("[TURN MOVEMENTS LOG (STRICT FORMAT)]")

        any_movement_this_tick = False
        tick_movements: list = []
        connections_to_release: list = []

        for drone in self.map_obj.drones.values():
            if drone.status == "arrived":
                continue

            if (drone.status == "in_transit" and
                    drone.transit_ticks_left > 0):
                drone.transit_ticks_left -= 1
                any_movement_this_tick = True
                if drone.transit_ticks_left == 0:
                    if drone.assigned_connection:
                        drone.assigned_connection.exit_connection()
                    if drone.target_zone_obj:
                        drone.target_zone_obj.release_reservation()
                        drone.current_zone = drone.target_zone_obj.zone_name
                        drone.target_zone_obj.enter_zone()

                    if drone.current_zone == self.map_obj.end_zone:
                        drone.status = "arrived"
                    else:
                        drone.status = "waiting"

                    log_str = f"{drone.id_dron}-{drone.current_zone}"
                    tick_movements.append(log_str)
                continue

            if drone.current_zone and self.map_obj.end_zone:
                dynamic_path = self.map_obj.find_dynamic_route(
                    drone.current_zone,
                    self.map_obj.end_zone
                )
            else:
                dynamic_path = []

            if not dynamic_path or len(dynamic_path) < 2:
                continue

            next_zone_name = dynamic_path[1]
            target_zone = self.map_obj.zones[next_zone_name]

            connection = None
            for conn in self.map_obj.connections[drone.current_zone]:
                if (conn.get_destination_from(drone.current_zone) ==
                        next_zone_name):
                    connection = conn
                    break

            if not connection:
                continue

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
                    self.map_obj.zones[drone.current_zone].exit_zone()
                    target_zone.reserve_space()
                    drone.status = "in_transit"
                    drone.transit_ticks_left = 1
                    drone.assigned_connection = connection
                    drone.target_zone_obj = target_zone

                    conn_str = f"{drone.current_zone}-{next_zone_name}"
                    log_str = f"{drone.id_dron}-{conn_str}"
                    tick_movements.append(log_str)
                else:
                    connections_to_release.append(connection)
                    self.map_obj.zones[drone.current_zone].exit_zone()
                    drone.current_zone = next_zone_name
                    target_zone.enter_zone()

                    if drone.current_zone == self.map_obj.end_zone:
                        drone.status = "arrived"
                    else:
                        drone.status = "waiting"

                    log_str = f"{drone.id_dron}-{drone.current_zone}"
                    tick_movements.append(log_str)

        if tick_movements:
            tick_line = " ".join(tick_movements)
            print(tick_line)
            self.log_outputs.append(tick_line)

        for conn in connections_to_release:
            conn.exit_connection()

        if not any_movement_this_tick and arrived_count < self.total_drones:
            print(
                f"\n[FATAL] Deadlock detectado en el Tick {self.tick}. "
                "La simulación se ha colapsado."
            )
            self.ejecutando = False

        sys.stdout.flush()

    def render(self) -> None:
        """Draw the current simulation state to the screen."""
        self.frame_count += 1
        self.pantalla.fill(COLOR_FONDO)
        Draw_simul.draw_simulation(
            self.pantalla,
            self.map_obj,
            self.font,
            self.fontg,
            self.escala_x,
            self.escala_y,
            self.frame_count,
            self.tick,
            self.paused
        )
        pygame.display.flip()

    def run(self) -> None:
        """Main simulation loop."""
        while self.ejecutando:
            self.handle_events()

            should_tick = not self.paused or self.step_once
            self.step_once = False
            if should_tick:
                self.process_tick()

            self.render()
            self.clock.tick(2)
        pygame.quit()


def main() -> None:
    """Entry point: parse the map and run the simulation."""
    filepath = sys.argv[1] if len(sys.argv) > 1 else "my_map.txt"
    map_parser = Parser(filepath)
    map_obj = map_parser.parser()

    if map_obj and map_obj.start_zone and map_obj.end_zone:
        initial_route = map_obj.find_dynamic_route(
            map_obj.start_zone,
            map_obj.end_zone
        )

        if not initial_route:
            print(
                "ERROR: The map does not have a viable physical "
                "connection between start and end hubs."
            )
            sys.exit(1)

        sim = DroneSimulation(map_obj)
        sim.run()
    else:
        print("ERROR: No se pudo cargar el mapa o faltan zonas start/end.")


if __name__ == "__main__":
    main()
