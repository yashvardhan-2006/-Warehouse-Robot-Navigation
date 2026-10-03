import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time
from typing import Dict, List, Tuple

from warehouse.grid import WarehouseGrid, CellType
from warehouse.presets import WarehousePresets
from algorithms import DijkstraSolver, AStarSolver, BFSSolver
from visualization.pygame_renderer import PygameGridRenderer
from visualization.chart_generator import PerformanceChartGenerator

# Streamlit Page Setup
st.set_page_config(
    page_title="Warehouse Robot Pathfinding Visualizer",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-End Dark UI CSS Styling
st.markdown("""
<style>
    /* Dark Theme Setup */
    .stApp {
        background-color: #0f172a;
        color: #f8fafc;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }
    .stSidebar {
        background-color: #1e293b !important;
        border-right: 1px solid #334155;
    }
    h1, h2, h3 {
        color: #f8fafc !important;
        font-weight: 700;
    }
    .metric-card {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 14px;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
    }
    .metric-val {
        font-size: 24px;
        font-weight: 800;
        margin-top: 4px;
    }
    .metric-lbl {
        font-size: 12px;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .highlight-astar { color: #c084fc; }
    .highlight-dijkstra { color: #38bdf8; }
    .highlight-bfs { color: #fb923c; }
    div.stButton > button {
        background-color: #2563eb;
        color: white;
        border-radius: 6px;
        border: none;
        font-weight: 600;
        padding: 6px 16px;
    }
    div.stButton > button:hover {
        background-color: #1d4ed8;
    }
</style>
""", unsafe_allow_html=True)


# Initialize Session State
if 'grid' not in st.session_state:
    st.session_state.grid = WarehousePresets.amazon_fulfillment(20, 25)
if 'results' not in st.session_state:
    st.session_state.results = {}
if 'step_index' not in st.session_state:
    st.session_state.step_index = 0
if 'is_playing' not in st.session_state:
    st.session_state.is_playing = False
if 'renderer' not in st.session_state:
    st.session_state.renderer = PygameGridRenderer(cell_size=24)


def run_all_solvers():
    """Runs Dijkstra, A*, and BFS solvers on the current grid."""
    grid = st.session_state.grid
    start = grid.start
    goal = grid.goal

    dijkstra = DijkstraSolver().solve(grid, start, goal)
    astar = AStarSolver().solve(grid, start, goal)
    bfs = BFSSolver().solve(grid, start, goal)

    st.session_state.results = {
        "A* Search": astar,
        "Dijkstra": dijkstra,
        "BFS": bfs
    }


# Initial solver run
if not st.session_state.results:
    run_all_solvers()


# Sidebar Configuration Panel
st.sidebar.title("🤖 AMR Warehouse Nav")
st.sidebar.caption("Pathfinding Benchmark (A*, Dijkstra, BFS)")

st.sidebar.markdown("---")
st.sidebar.subheader("📐 Warehouse Layout")

preset_name = st.sidebar.selectbox(
    "Select Layout Preset",
    ["Amazon Fulfillment Hub", "Dense Storage Racks", "Bottleneck Maze", "Weighted Traffic Depot", "Empty Arena", "Custom Layout"],
    index=0
)

col_r, col_c = st.sidebar.columns(2)
new_rows = col_r.slider("Rows", 10, 50, st.session_state.grid.rows)
new_cols = col_c.slider("Cols", 10, 50, st.session_state.grid.cols)

if st.sidebar.button("🔄 Load / Reset Preset"):
    if preset_name == "Amazon Fulfillment Hub":
        st.session_state.grid = WarehousePresets.amazon_fulfillment(new_rows, new_cols)
    elif preset_name == "Dense Storage Racks":
        st.session_state.grid = WarehousePresets.dense_storage_rack(new_rows, new_cols)
    elif preset_name == "Bottleneck Maze":
        st.session_state.grid = WarehousePresets.bottleneck_maze(new_rows, new_cols)
    elif preset_name == "Weighted Traffic Depot":
        st.session_state.grid = WarehousePresets.weighted_traffic_depot(new_rows, new_cols)
    elif preset_name == "Empty Arena":
        st.session_state.grid = WarehousePresets.empty_arena(new_rows, new_cols)
    else:
        st.session_state.grid = WarehouseGrid(new_rows, new_cols)
    
    st.session_state.step_index = 0
    run_all_solvers()
    st.rerun()


st.sidebar.markdown("---")
st.sidebar.subheader("✏️ Grid Cell Editor")

edit_tool = st.sidebar.radio(
    "Select Edit Tool",
    ["Obstacle (Wall)", "Shelf Rack", "Heavy Traffic (Cost: 3)", "Start Dock (S)", "Pickup Goal (G)", "Clear Floor"],
    index=0
)

col_er, col_ec = st.sidebar.columns(2)
edit_r = col_er.number_input("Row", 0, st.session_state.grid.rows - 1, 0)
edit_c = col_ec.number_input("Col", 0, st.session_state.grid.cols - 1, 0)

if st.sidebar.button("Apply Cell Edit"):
    tool_map = {
        "Obstacle (Wall)": CellType.OBSTACLE,
        "Shelf Rack": CellType.SHELF,
        "Heavy Traffic (Cost: 3)": CellType.HEAVY_TRAFFIC,
        "Start Dock (S)": CellType.START,
        "Pickup Goal (G)": CellType.GOAL,
        "Clear Floor": CellType.EMPTY
    }
    c_type = tool_map[edit_tool]
    st.session_state.grid.set_cell(edit_r, edit_c, c_type)
    st.session_state.step_index = 0
    run_all_solvers()
    st.rerun()


st.sidebar.markdown("---")
st.sidebar.subheader("👁️ Visual Overlay")
show_values = st.sidebar.checkbox("Show Cost Numbers on Grid", value=False)
value_mode = st.sidebar.selectbox("Value Overlay Type", ["g_score", "f_score", "h_score", "level"], index=0)

cell_scale = st.sidebar.slider("Cell Display Scale (px)", 12, 40, 24)
st.session_state.renderer.cell_size = cell_scale


# Header Banner
st.title("📦 Warehouse Robot Pathfinding Visualizer")
st.markdown(
    "Interactive benchmarking environment demonstrating **A* Search**, **Dijkstra's Algorithm**, and **Breadth-First Search (BFS)** "
    "for Autonomous Mobile Robots (AMRs) navigating warehouse floors."
)

# Navigation Tabs
tab_vis, tab_compare, tab_deepdive, tab_inspect = st.tabs([
    "🎬 Step-by-Step Visualizer",
    "📊 Algorithm Comparison & Overlay",
    "💡 Algorithm Educational Insights",
    "🔍 Cell Inspector"
])


# ==========================================
# TAB 1: STEP-BY-STEP VISUALIZER
# ==========================================
with tab_vis:
    results = st.session_state.results
    grid = st.session_state.grid

    # Find max step count across algorithms
    max_steps = max(len(res.steps) for res in results.values()) if results else 1

    # Playback Controls Bar
    c_ctrl1, c_ctrl2, c_ctrl3, c_ctrl4, c_ctrl5 = st.columns([1, 1, 1, 1, 4])
    
    if c_ctrl1.button("◀ Step Back"):
        st.session_state.step_index = max(0, st.session_state.step_index - 1)
        st.session_state.is_playing = False
    
    if c_ctrl2.button("Step Forward ▶"):
        st.session_state.step_index = min(max_steps - 1, st.session_state.step_index + 1)
        st.session_state.is_playing = False
    
    if c_ctrl3.button("⏪ Reset"):
        st.session_state.step_index = 0
        st.session_state.is_playing = False

    if c_ctrl4.button("⏩ Jump to End"):
        st.session_state.step_index = max_steps - 1
        st.session_state.is_playing = False

    st.session_state.step_index = c_ctrl5.slider(
        "Search Step Progress",
        0, max_steps - 1,
        st.session_state.step_index
    )

    st.markdown("---")

    # Side-by-Side 3-Column Display
    col_a, col_d, col_b = st.columns(3)

    for col, algo_name, accent_cls in [
        (col_a, "A* Search", "highlight-astar"),
        (col_d, "Dijkstra", "highlight-dijkstra"),
        (col_b, "BFS", "highlight-bfs")
    ]:
        res = results.get(algo_name)
        with col:
            st.markdown(f"<h3 class='{accent_cls}'>{algo_name}</h3>", unsafe_allow_html=True)
            
            if res and res.steps:
                cur_step_idx = min(st.session_state.step_index, len(res.steps) - 1)
                step_obj = res.steps[cur_step_idx]
                is_at_end = (cur_step_idx >= len(res.steps) - 1)

                frame = st.session_state.renderer.render_frame(
                    grid=grid,
                    current_step=step_obj,
                    final_path=res.path if is_at_end else None,
                    algo_name=algo_name,
                    show_values=show_values,
                    value_mode=value_mode
                )
                st.image(frame)

                # Metrics card
                dist_str = f"{res.distance:.1f}" if res.found else "No Path"
                exp_cnt = len(step_obj.explored)
                st.markdown(f"""
                <div class='metric-card'>
                    <div class='metric-lbl'>Path Distance / Explored Cells</div>
                    <div class='metric-val {accent_cls}'>{dist_str} / {exp_cnt}</div>
                    <div style='font-size: 11px; color: #94a3b8; margin-top:4px;'>Execution Time: {res.execution_time_ms:.2f} ms</div>
                </div>
                """, unsafe_allow_html=True)


# ==========================================
# TAB 2: ALGORITHM COMPARISON & OVERLAY
# ==========================================
with tab_compare:
    results = st.session_state.results
    grid = st.session_state.grid

    st.subheader("⚡ Performance Benchmarking Summary")

    # Construct Pandas DataFrame for side-by-side comparison
    table_data = []
    for name, res in results.items():
        efficiency = (len(res.path) / max(1, len(res.explored_cells))) * 100.0 if res.found and res.path else 0.0
        table_data.append({
            "Algorithm": name,
            "Path Found": "Yes" if res.found else "No",
            "Total Cost (Distance)": f"{res.distance:.1f}" if res.found else "N/A",
            "Path Hop Count": str(res.hop_count),
            "Cells Explored": str(len(res.explored_cells)),
            "Exploration Efficiency": f"{efficiency:.1f}%",
            "Execution Time (ms)": f"{res.execution_time_ms:.2f} ms"
        })

    df = pd.DataFrame(table_data)
    st.table(df)

    st.markdown("---")

    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.subheader("📊 Path Cost vs. Explored Cells")
        fig_bar = PerformanceChartGenerator.create_comparison_bar_chart(results)
        st.pyplot(fig_bar)

    with col_chart2:
        st.subheader("🗺️ Multi-Algorithm Path Overlay")
        fig_overlay = PerformanceChartGenerator.create_overlay_map(grid, results)
        st.pyplot(fig_overlay)

    # Key Performance Takeaways
    st.markdown("---")
    st.subheader("📌 Key Engineering Insights")
    
    astar_res = results.get("A* Search")
    dijk_res = results.get("Dijkstra")
    bfs_res = results.get("BFS")

    if astar_res and dijk_res and astar_res.found:
        cell_diff = len(dijk_res.explored_cells) - len(astar_res.explored_cells)
        savings = (cell_diff / max(1, len(dijk_res.explored_cells))) * 100.0
        st.info(
            f"💡 **A* Search Efficiency**: A* explored **{len(astar_res.explored_cells)}** cells compared to Dijkstra's "
            f"**{len(dijk_res.explored_cells)}** cells (**{savings:.1f}% fewer cells examined**), while achieving the exact "
            f"same optimal path cost of **{astar_res.distance:.1f}**. The Manhattan distance heuristic successfully directed the search tree straight towards the pickup goal."
        )


# ==========================================
# TAB 3: EDUCATIONAL ALGORITHM INSIGHTS
# ==========================================
with tab_deepdive:
    st.subheader("🎓 Deep Dive into Algorithm Mechanics")

    col_ed1, col_ed2, col_ed3 = st.columns(3)

    with col_ed1:
        st.markdown("""
        ### 🔵 Dijkstra's Algorithm
        - **Strategy**: Uniform Cost Search. Always expands the unexplored node with the lowest path cost $g(n)$ from the start node.
        - **Guarantees**: Optimal shortest path on non-negatively weighted graphs.
        - **Exploration Pattern**: Expands outward in concentric radial circles (blind wave).
        - **Warehouse Application**: Ideal when cell traversal costs vary (e.g. heavy traffic lanes), but explores unnecessary cells away from the goal.
        """)

    with col_ed2:
        st.markdown("""
        ### 🟣 A* (A-Star) Search
        - **Strategy**: Informed Heuristic Search. Uses evaluation function $f(n) = g(n) + h(n)$, combining exact cost $g(n)$ and estimated distance to goal $h(n)$.
        - **Heuristic Used**: **Manhattan Distance** ($|x_1 - x_2| + |y_1 - y_2|$), which is strictly admissible for 4-directional grid movement.
        - **Exploration Pattern**: Directed beam/cone towards the goal.
        - **Warehouse Application**: Highly efficient for AMR fleet routing, minimizing compute cycles while maintaining path optimality.
        """)

    with col_ed3:
        st.markdown("""
        ### 🟠 Breadth-First Search (BFS)
        - **Strategy**: Unweighted Level-by-Level Search using a FIFO queue.
        - **Guarantees**: Minimum-hop path on unweighted graphs (where all step costs = 1).
        - **Exploration Pattern**: Concentric level rings advancing one hop at a time.
        - **Warehouse Application**: Useful for simple unweighted grids, but ignores terrain weights (like heavy traffic lanes).
        """)


# ==========================================
# TAB 4: CELL INSPECTOR
# ==========================================
with tab_inspect:
    st.subheader("🔍 Grid Cell State Inspector")
    st.markdown("Inspect individual grid cell values ($g$-score, $h$-score, $f$-score, level) across all algorithms.")

    ic1, ic2 = st.columns(2)
    inspect_r = ic1.number_input("Inspect Row", 0, st.session_state.grid.rows - 1, 0, key="insp_r")
    inspect_c = ic2.number_input("Inspect Col", 0, st.session_state.grid.cols - 1, 0, key="insp_c")

    target_cell = (inspect_r, inspect_c)
    cell_type_val = st.session_state.grid.grid[inspect_r, inspect_c]
    cell_name = CellType.NAMES.get(cell_type_val, "Unknown")
    cell_cost = st.session_state.grid.get_cost(inspect_r, inspect_c)

    st.markdown(f"**Selected Cell:** `({inspect_r}, {inspect_c})` | **Type:** `{cell_name}` | **Cost:** `{cell_cost}`")

    inspect_data = []
    for name, res in st.session_state.results.items():
        g_val = res.g_scores.get(target_cell, None)
        h_val = res.h_scores.get(target_cell, None)
        f_val = res.f_scores.get(target_cell, None)
        lvl = res.level_map.get(target_cell, None)
        
        g_str = f"{g_val:.1f}" if isinstance(g_val, (int, float)) else "N/A"
        h_str = f"{h_val:.1f}" if isinstance(h_val, (int, float)) else "N/A"
        f_str = f"{f_val:.1f}" if isinstance(f_val, (int, float)) else "N/A"
        lvl_str = str(lvl) if lvl is not None else "N/A"
        
        was_exp = "Yes" if target_cell in res.explored_cells else "No"
        in_path = "Yes" if target_cell in res.path else "No"

        inspect_data.append({
            "Algorithm": str(name),
            "Explored": str(was_exp),
            "In Final Path": str(in_path),
            "g-Score (Cost from Start)": g_str,
            "h-Score (Heuristic to Goal)": h_str,
            "f-Score (g + h)": f_str,
            "BFS Level": lvl_str
        })

    st.table(pd.DataFrame(inspect_data))
