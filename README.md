*This project has been created as part of the 42 curriculum by chmorale.*

# Fly-in — Drone Routing Simulator

## Description

Fly-in is a drone traffic management simulator written in Python.
The goal is to route a fleet of drones from a start hub to an end hub
through a network of connected zones, minimising the total number of
simulation turns while respecting all movement, capacity, and
zone-type constraints.

Key features:

- Weighted Dijkstra pathfinding with dynamic congestion penalties
- Multi-drone movement scheduling, recomputed every turn
- Zone types: normal, restricted (2-turn transit), priority, blocked
- Per-turn capacity enforcement for zones and connections
- Look-ahead reservation system for restricted-zone transit
- Real-time Pygame graphical interface with orbital drone animation

## Instructions

### Requirements

- Python 3.10 or later
- pygame >= 2.5.0

### Installation

```
make install
```

Creates a virtual environment (`.venv`) and installs all dependencies.

### Running the simulator

```
make run
```

To use a custom map file:

```
.venv/bin/python3 fly-in.py path/to/map.txt
```

Defaults to `my_map.txt` in the current directory if no argument is
given.

### Debug mode

```
make debug
```

Launches the simulator under Python's built-in debugger (`pdb`).

### Linting

```
make lint
```

Runs `flake8` and `mypy` with the project's static-analysis
configuration.

### Cleanup

```
make clean
```

Removes Python caches (`__pycache__`, `.mypy_cache`).

### Map file format

```
nb_drones: 5
start_hub: hub 0 0 [color=green]
end_hub:   goal 10 10 [color=yellow]
hub: zoneA 3 4 [zone=restricted max_drones=2]
hub: zoneB 6 2 [zone=priority]
hub: zoneC 5 5 [zone=blocked]
connection: hub-zoneA [max_link_capacity=2]
connection: zoneA-goal
```

- First data line must be `nb_drones: <positive_integer>`.
- Zone types: `normal` (default), `restricted`, `priority`, `blocked`.
- `max_drones` default: 1 (unlimited for start/end hubs).
- `max_link_capacity` default: 1.
- Comments begin with `#`.
- Zone names must not contain dashes or spaces.

## Resources

### References

- Dijkstra's algorithm:
  <https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm>
- Python `heapq` module:
  <https://docs.python.org/3/library/heapq.html>
- Pygame documentation: <https://www.pygame.org/docs/>
- PEP 257 — Docstring Conventions:
  <https://peps.python.org/pep-0257/>
- mypy documentation: <https://mypy.readthedocs.io/>

### AI usage

Claude (Anthropic) was used throughout this project for:

- **Architecture design**: initial class structure (`Map`, `Zone`,
  `Connection`, `Drone`) and simulation loop design.
- **Bug identification**: systematic reviews that caught issues such as
  incorrect default capacities, missing `pygame.quit()` calls, and
  incorrect zone-release timing in restricted transit.
- **Algorithm refinement**: transitioning from BFS to weighted Dijkstra
  with congestion penalties, and implementing the look-ahead reservation
  system for restricted zones.
- **Type annotations and linting**: ensuring `mypy` and `flake8`
  compliance.
- **Documentation**: assistance with docstring wording and README
  structure.

All AI-generated suggestions were reviewed, understood, tested, and
adapted by the author. No code was accepted without full comprehension.

## Algorithm

### Pathfinding: weighted Dijkstra

The routing engine uses Dijkstra's algorithm (via Python's `heapq`) to
compute the minimum-cost path for each drone at every simulation turn.

**Node weights by zone type:**

| Zone type    | Dijkstra cost | Travel turns |
|--------------|:-------------:|:------------:|
| `priority`   | 0             | 1            |
| `normal`     | 1             | 1            |
| `restricted` | 2             | 2            |
| `blocked`    | skipped       | —            |

**Congestion penalty**: each drone currently on a connection adds +1
to that connection's cost, nudging subsequent drones towards
less-loaded paths automatically.

**Dynamic re-routing**: paths are recalculated every turn. Full
connections are excluded from the graph entirely for that turn,
allowing the algorithm to adapt to changing network conditions without
any pre-computation.

### Look-ahead reservation system

When a drone is approved to enter a restricted zone (2-turn transit),
a reservation is immediately placed via `Zone.reserve_space()`. Future
drones evaluating that zone see `current_drones + reserved_spaces`
against `max_drones`, preventing over-commitment. The reservation is
released on landing (`Zone.release_reservation()`).

### Turn resolution

Each turn, drones are processed one at a time (in drone-ID order).
For each drone still active, the simulator recomputes its shortest
path to the end hub and attempts to move it into the next zone on
that path, subject to zone and connection capacity at that exact
moment in the processing order.

### Deadlock detection

If a full turn passes with zero drone movements and not all drones
have arrived, the simulation reports a fatal deadlock and stops.

## Known limitations

- **Sequential move resolution.** Movements are decided and applied
  drone by drone within a turn, rather than computed as a single
  simultaneous batch. In most maps this has no visible effect, but it
  means capacity checks for a given drone reflect only the moves
  already applied earlier in that same turn's processing order, not
  the full set of moves that will happen this turn.
- **Consequence — false deadlock on same-turn zone swaps.** If two
  drones need to swap positions between two zones that are both at
  full capacity (e.g. two capacity-1 zones), neither can move first
  because, from a sequential point of view, the other hasn't left
  yet. This can trigger the deadlock detector even though the swap is
  physically valid if resolved simultaneously. This is a known,
  understood trade-off, not an unnoticed defect: a fully simultaneous
  resolution would require computing every drone's intended move
  against a fixed start-of-turn snapshot, then reconciling zone/
  connection capacity as a single batch (and detecting closed
  "trade" cycles as a special case) before applying anything — a
  meaningfully more complex scheduler that was deliberately left out
  of scope in favour of a simpler, fully-understood implementation.
- **Pathfinding cost ignores zone capacity.** `Map.find_dynamic_route`
  weighs and excludes edges based on connection capacity
  (`max_link_capacity`) and blocked zones, but does not check the
  destination zone's own `max_drones` when scoring a route. Zone
  capacity is only enforced at the moment a move is actually
  attempted, which can occasionally cause a drone to be routed toward
  a zone that turns out to be full, wasting a turn instead of
  proactively routing elsewhere.

## Visualization

The simulator provides two simultaneous output channels.

### Terminal output (strict format)

Each turn prints one line listing all movements:

- `D<ID>-<zone>`: drone moved to a zone in one turn.
- `D<ID>-<origin>-<dest>`: drone entered the connection toward a
  restricted zone (will land next turn).

Only drones that move are listed. The terminal panel also prints a
per-zone occupancy bar and a per-drone status table every tick.

### Pygame graphical interface

The live GUI renders:

- **Connections**: grey lines that turn orange while at least one
  drone is currently traversing them.
- **Zone circles**: coloured by access type — blue (normal), red
  (restricted), purple (priority), grey (blocked) — with a capacity
  ring around each zone that turns red once it reaches `max_drones`.
- **Waiting drones**: orbit their zone in cyan using a cosine/sine
  animation — the "fun touch".
- **In-transit drones**: shown as a gold dot at the midpoint of the
  connection they are travelling through.
- **Arrived drones**: shown as small green dots clustered at the end
  hub.
- **HUD**: top-left counter showing the current tick and how many
  drones have been delivered out of the total.

### Layout scaling

The canvas uses independent horizontal and vertical scales so that the
full coordinate range of the map always fills the window on both axes.
This prevents very wide, shallow maps (large X range, small Y range)
from compressing zone rows to the point where labels overlap.