import http.server
import socketserver
import json
import urllib.parse
import webbrowser
import os
import sys

from warehouse.grid import WarehouseGrid, CellType
from warehouse.presets import WarehousePresets
from algorithms import DijkstraSolver, AStarSolver, BFSSolver

PORT = 8000

# Global backend grid state
current_grid = WarehousePresets.amazon_fulfillment(20, 25)
solvers = {
    "A* Search": AStarSolver(),
    "Dijkstra": DijkstraSolver(),
    "BFS": BFSSolver()
}

def solve_grid(grid: WarehouseGrid):
    """Executes all Python solvers on current grid."""
    start = grid.start
    goal = grid.goal

    results = {}
    for name, solver in solvers.items():
        res = solver.solve(grid, start, goal)
        
        # Serialize step objects to JSON compatible dicts
        serializable_steps = []
        for s in res.steps:
            serializable_steps.append({
                "step": s.step_index,
                "current": list(s.current) if s.current else None,
                "frontier": [list(cell) for cell in s.frontier],
                "explored": [list(cell) for cell in s.explored],
                "gScores": {f"{r},{c}": val for (r, c), val in s.g_scores.items()},
                "fScores": {f"{r},{c}": val for (r, c), val in s.f_scores.items()},
                "hScores": {f"{r},{c}": val for (r, c), val in s.h_scores.items()},
                "levelMap": {f"{r},{c}": val for (r, c), val in s.level.items()}
            })

        results[name] = {
            "name": res.algorithm_name,
            "found": res.found,
            "path": [list(p) for p in res.path],
            "explored": [list(p) for p in res.explored_cells],
            "distance": float(res.distance) if res.found else float('inf'),
            "hopCount": res.hop_count,
            "executionTime": res.execution_time_ms,
            "steps": serializable_steps,
            "gScores": {f"{r},{c}": val for (r, c), val in res.g_scores.items()},
            "fScores": {f"{r},{c}": val for (r, c), val in res.f_scores.items()},
            "hScores": {f"{r},{c}": val for (r, c), val in res.h_scores.items()},
            "levelMap": {f"{r},{c}": val for (r, c), val in res.level_map.items()}
        }
    return results

class BackendAPIHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP Request Handler serving both static Web Frontend & Python REST API endpoints."""

    def log_message(self, format, *args):
        pass # Quiet logging

    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/api/status":
            self._send_json({"status": "connected", "backend": "Python 3.14 + Pygame Graph Engine"})
        
        elif path == "/api/grid":
            global current_grid
            self._send_json({
                "rows": current_grid.rows,
                "cols": current_grid.cols,
                "grid": current_grid.grid.tolist(),
                "start": list(current_grid.start),
                "goal": list(current_grid.goal),
                "solvers": solve_grid(current_grid)
            })

        else:
            # Fallback to serving static frontend files (index.html, styles.css, app.js)
            super().do_GET()

    def do_POST(self):
        global current_grid
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"
        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            payload = {}

        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/api/preset":
            preset = payload.get("preset", "amazon")
            rows = payload.get("rows", 20)
            cols = payload.get("cols", 25)

            if preset == "amazon":
                current_grid = WarehousePresets.amazon_fulfillment(rows, cols)
            elif preset == "bottleneck":
                current_grid = WarehousePresets.bottleneck_maze(rows, cols)
            elif preset == "dense":
                current_grid = WarehousePresets.dense_storage_rack(rows, cols)
            elif preset == "traffic":
                current_grid = WarehousePresets.weighted_traffic_depot(rows, cols)
            else:
                current_grid = WarehousePresets.empty_arena(rows, cols)

            self._send_json({
                "rows": current_grid.rows,
                "cols": current_grid.cols,
                "grid": current_grid.grid.tolist(),
                "start": list(current_grid.start),
                "goal": list(current_grid.goal),
                "solvers": solve_grid(current_grid)
            })

        elif path == "/api/cell":
            r = payload.get("row")
            c = payload.get("col")
            cell_type = payload.get("type", 0)

            if r is not None and c is not None and current_grid.is_valid(r, c):
                current_grid.set_cell(r, c, cell_type)

            self._send_json({
                "rows": current_grid.rows,
                "cols": current_grid.cols,
                "grid": current_grid.grid.tolist(),
                "start": list(current_grid.start),
                "goal": list(current_grid.goal),
                "solvers": solve_grid(current_grid)
            })

        elif path == "/api/solve":
            self._send_json({
                "rows": current_grid.rows,
                "cols": current_grid.cols,
                "grid": current_grid.grid.tolist(),
                "start": list(current_grid.start),
                "goal": list(current_grid.goal),
                "solvers": solve_grid(current_grid)
            })
        else:
            self._send_json({"error": "Unknown endpoint"}, 404)

def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    handler = BackendAPIHandler
    
    # Allow port re-use
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        url = f"http://localhost:{PORT}"
        print("==================================================================")
        print("FULL-STACK AMR Warehouse Robot Pathfinding Server")
        print("Python Backend Connected to Web Frontend")
        print("==================================================================")
        print(f"Backend Server listening at: {url}")
        print("REST API Endpoints:")
        print("  - GET  /api/status")
        print("  - GET  /api/grid")
        print("  - POST /api/preset")
        print("  - POST /api/cell")
        print("  - POST /api/solve")
        print("==================================================================")

        try:
            webbrowser.open(url)
        except Exception:
            pass

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server.")
            sys.exit(0)

if __name__ == "__main__":
    main()
