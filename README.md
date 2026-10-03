# AMR Warehouse Robot Pathfinding Visualizer 🤖📦

A **Full-Stack Interactive System** connecting a high-performance **Python Pathfinding Engine** to a modern **Glassmorphic Web Frontend** via a REST API. Demonstrates **A* Search**, **Dijkstra's Algorithm**, and **Breadth-First Search (BFS)** applied to Autonomous Mobile Robot (AMR) warehouse navigation.

---

## 🌟 Key Features

1. **Full-Stack Connected Architecture**:
   - **Python Backend**: Runs `AStarSolver`, `DijkstraSolver`, `BFSSolver`, and `WarehouseGrid` graph models. Exposes REST API endpoints (`/api/status`, `/api/grid`, `/api/preset`, `/api/cell`, `/api/solve`).
   - **Web Frontend**: HTML5/CSS3/JS UI with HTML5 Canvas engine, real-time animation scrubber, interactive cell drawing, preset loader, and benchmarking matrix.

2. **Decoupled Solvers**:
   - **A* Search**: Uses an admissible Manhattan Distance heuristic ($f(n) = g(n) + h(n)$) to direct search towards the pickup goal, reducing explored cells by **up to 90%+** compared to Dijkstra.
   - **Dijkstra's Algorithm**: Uniform cost search that expands the node with the lowest tentative path cost $g(n)$, guaranteeing optimal paths on weighted grids.
   - **Breadth-First Search (BFS)**: Explores grid level-by-level in concentric waves, guaranteeing minimum-hop paths on unweighted graphs.

3. **Interactive Tools & Presets**:
   - **Paint Tools**: Steel Wall Barriers, Wooden Shelf Racks, Heavy Traffic Zones (Cost 3.0), Robot Start Dock, Pickup Goal Target, Eraser.
   - **Layout Presets**: Amazon Fulfillment Center, Bottleneck Maze, Dense Racks, Heavy Traffic Depot, Empty Arena.

---

## 🏗️ Repository Architecture

```
DAA HACKTHON/
├── backend_server.py            # Python REST API Server & Web Server (Port 8000)
├── algorithms/                  # Core Python Solvers
│   ├── base.py                  # BaseSolver interface & PathResult / AlgorithmStep classes
│   ├── dijkstra.py              # Dijkstra's Algorithm implementation
│   ├── astar.py                 # A* Search implementation with Manhattan distance
│   └── bfs.py                   # Breadth-First Search implementation
├── warehouse/                   # Warehouse Environment Grid Graph
│   ├── grid.py                  # WarehouseGrid model (4-directional adjacency & costs)
│   └── presets.py               # Pre-configured warehouse layout templates
├── visualization/               # Rendering & Analytics Modules
│   ├── pygame_renderer.py       # Pygame grid frame renderer & surface converter
│   └── chart_generator.py       # Matplotlib benchmarking charts & multi-path overlay
├── index.html                   # Web Frontend Structure & Navigation
├── styles.css                   # Glassmorphism Cyber-Dark Design System
├── app.js                       # Full-Stack Web Visualizer Engine (REST API Client)
├── app.py                       # Alternative Streamlit Web Dashboard
├── standalone_pygame.py         # Alternative Standalone Desktop Pygame Window
├── requirements.txt             # Project Dependencies
└── README.md                    # System Documentation
```

---

## 🚀 Getting Started

### 1. Installation
Install dependencies:
```bash
pip install -r requirements.txt
```

### 2. Run Full-Stack Web Application (Connected Frontend & Backend)
Start the connected Python REST API server and launch the Web Frontend:
```bash
python backend_server.py
```
Open `http://localhost:8000` in your web browser.

### 3. REST API Endpoints

| Endpoint | Method | Description |
| :--- | :---: | :--- |
| `/api/status` | `GET` | Health check & backend version status |
| `/api/grid` | `GET` | Returns current grid layout & Python solver calculations |
| `/api/preset` | `POST` | Loads layout preset (Amazon, Bottleneck, Dense, Traffic, Empty) |
| `/api/cell` | `POST` | Updates cell type at `(row, col)` and recalculates paths |
| `/api/solve` | `POST` | Executes A*, Dijkstra, and BFS solvers on active grid |

---

## 📊 Benchmark Results Summary

| Algorithm | Path Found | Path Cost (Distance) | Hop Count | Cells Explored | Exploration Efficiency |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **A* Search** | ✅ Yes | **34.0** | 35 | **35** | **100.0%** |
| **Dijkstra** | ✅ Yes | **34.0** | 35 | 353 | 9.9% |
| **BFS** | ✅ Yes | **34.0** | 35 | 356 | 9.8% |

> **Takeaway**: On an Amazon Fulfillment grid (20×25), **Python A* Search examined 90.1% fewer cells** than Dijkstra while achieving the exact same optimal path cost of 34.0.
