_This project has been created as part of the 42 curriculum by bclairot._

# Fly-in

## Description

Fly-in is a graph-based drone flow simulation.
The goal is to route a fleet of drones from one `start_hub` to one `end_hub` through a network of hubs and directed connections while respecting:

- hub capacities (`max_drones`),
- connection capacities (`max_link_capacity`),
- and zone/color metadata validated as enums during parsing.

The project reads a map file, builds an internal graph, computes route priorities, and runs a turn-by-turn visual simulation with Pyglet.

---

## Features

- Map parsing and validation
- Enum-based validation for zones and colors
- Directed graph construction from hub/connection definitions
- Turn-based drone movement with capacity constraints
- Zone-aware behavior (including delayed movement through restricted zones)
- Fullscreen visual simulation (nodes, links, drone counters)
- Optional legend mode for dense maps

---

## Instructions

### Prerequisites

- Python 3.10+
- `uv` package manager (recommended by this project)

### Installation

From the project root:

- `make install`

This runs `uv sync` and installs dependencies from [pyproject.toml](pyproject.toml).

### Run

Default map:

- `make run`

Custom map:

- `make run ARGS="--map ./maps/medium/03_priority_puzzle.txt"`

Direct execution is also possible:

- `uv run python -m src --map ./maps/easy/01_linear_path.txt`

### Debug / Quality

- Debug: `make debug`
- Lint: `make lint`
- Strict lint: `make lint-strict`
- Cleanup cache/venv artifacts: `make clean`

---

## Map Format (Quick Overview)

Each map starts with the drone count, then hub declarations, then connections:

```txt
nb_drones: 5
start_hub: A 0 0 [color=green] [zone=priority]
hub: B 2 1 [max_drones=2]
end_hub: Z 5 1 [color=red]
connection: A-B [max_link_capacity=2]
connection: B-Z [max_link_capacity=1]
```

Main map packs are available in [maps](maps) (easy / medium / hard / challenger).

---

## Algorithm Choices and Implementation Strategy

### 1) Parsing and data model

The parser in [src/parsing.py](src/parsing.py) reads the map line-by-line and builds `Hub` + `Connection` objects defined in [src/hub.py](src/hub.py).
It also converts `zone` and `color` metadata into `ZoneEnum` and `ColorEnum` values so invalid metadata fails early.

Validation strategy includes:

- mandatory `nb_drones` first,
- exactly one start and one end hub,
- unique hub coordinates,
- existing hub names in connections,
- basic metadata extraction (`zone`, `color`, `max_drones`, `max_link_capacity`),
- enum validation for `zone` and `color` metadata.

### 2) Hub scoring (route priority)

Before simulation, [src/flyin.py](src/flyin.py) computes a score from the start hub to all reachable hubs.

Current scoring policy:

- `priority` transition cost = 1
- `normal` transition cost = 2
- `restricted` transition cost = 3

The recursive propagation updates a hub score when a cheaper value is found.
This score acts as a heuristic for movement decisions.

### 3) Turn-by-turn movement

At each turn, [src/display.py](src/display.py) performs:

1. collect hubs currently containing drones,
2. build possible outgoing moves,
3. sort destinations by score (lower score first),
4. move drones while enforcing:
	 - destination remaining capacity,
	 - link capacity,
	 - zone behavior.

Zone behavior detail:

- `normal` and `priority`: drones are added immediately to destination hub.
- `restricted`: drones are queued via `nb_drone_waiting_restricted` and become available on the next turn.

This gives a simple greedy strategy guided by precomputed costs and constrained by capacities.

### 4) Why this strategy

This implementation is intentionally straightforward and readable:

- easy to debug visually,
- deterministic turn logic,
- practical for iterative improvement and benchmarking.

It is a good baseline before moving to more advanced flow/path optimization approaches.

---

## Visual Representation and UX

The simulation UI is implemented in [src/display.py](src/display.py) with Pyglet.

### Visual elements

- **Hubs** rendered as circles with labels
- **Directed connections** rendered as arrows
- **Drone state** rendered as a drone sprite + numeric counter per hub
- **Color cues** through `ColorEnum` for quick identification
- **Adaptive layout** scaling map coordinates to fullscreen

### Interaction

- `ESC`: close the simulation
- `RIGHT`: advance one step manually
- `L`: toggle legend (when legend mode is active)

### UX enhancement notes

- Automatic coordinate normalization keeps any map readable on screen.
- Dense horizontal layers trigger legend mode to prevent label clutter.
- Numeric counters let users track congestion and flow bottlenecks in real time.

---

## Project Structure

- [src/__main__.py](src/__main__.py): entrypoint
- [src/flyin.py](src/flyin.py): app orchestration + score computation
- [src/parsing.py](src/parsing.py): map parsing and validation
- [src/hub.py](src/hub.py): graph model (`Hub`, `Connection`, `ZoneEnum`)
- [src/display.py](src/display.py): simulation and rendering
- [maps](maps): challenge maps by difficulty

---

## Resources

### Topic references

- Python documentation: https://docs.python.org/3/
- Pyglet documentation: https://pyglet.readthedocs.io/
- Graph theory basics (BFS/DFS/shortest paths):
	- https://en.wikipedia.org/wiki/Graph_theory
	- https://en.wikipedia.org/wiki/Shortest_path_problem

### AI usage disclosure

AI tools were used as an assistant during development, mainly for:

- README drafting and structuring,
- refactoring suggestions (readability, line length, small style improvements),
- quick review of wording and documentation clarity.

AI was **not** used as a blind generator for the whole project.
Final design choices, algorithm decisions, debugging, and validation were performed by the project author.

---

## Notes

This repository includes progressively harder benchmark maps, including a challenger scenario intended for stress-testing and optimization research.

