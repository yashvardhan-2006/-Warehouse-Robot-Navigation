import sys
import os
import numpy as np
import pygame
from warehouse.grid import WarehouseGrid, CellType
from warehouse.presets import WarehousePresets
from algorithms import DijkstraSolver, AStarSolver, BFSSolver
from visualization.pygame_renderer import PygameGridRenderer

def main():
    # Remove dummy video driver for standalone desktop mode
    if "SDL_VIDEODRIVER" in os.environ:
        del os.environ["SDL_VIDEODRIVER"]

    pygame.init()
    pygame.font.init()

    grid = WarehousePresets.amazon_fulfillment(25, 30)
    renderer = PygameGridRenderer(cell_size=28)

    width = grid.cols * renderer.cell_size
    hud_height = 90
    height = grid.rows * renderer.cell_size + hud_height

    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Warehouse Robot Pathfinding Visualizer (A*, Dijkstra, BFS)")
    clock = pygame.time.Clock()

    solvers = {
        "A* Search": AStarSolver(),
        "Dijkstra": DijkstraSolver(),
        "BFS": BFSSolver()
    }
    
    current_algo_name = "A* Search"
    result = solvers[current_algo_name].solve(grid, grid.start, grid.goal)

    anim_step = 0
    anim_speed = 3 # Steps per frame
    is_animating = False
    draw_mode = CellType.OBSTACLE
    show_values = False

    font_hud = pygame.font.SysFont("sans-serif", 14, bold=True)
    font_title = pygame.font.SysFont("sans-serif", 16, bold=True)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    is_animating = not is_animating
                elif event.key == pygame.K_r:
                    result = solvers[current_algo_name].solve(grid, grid.start, grid.goal)
                    anim_step = 0
                    is_animating = True
                elif event.key == pygame.K_c:
                    grid.clear()
                    result = solvers[current_algo_name].solve(grid, grid.start, grid.goal)
                    anim_step = 0
                    is_animating = False
                elif event.key == pygame.K_v:
                    show_values = not show_values
                elif event.key == pygame.K_1:
                    current_algo_name = "A* Search"
                    result = solvers[current_algo_name].solve(grid, grid.start, grid.goal)
                    anim_step = 0
                    is_animating = True
                elif event.key == pygame.K_2:
                    current_algo_name = "Dijkstra"
                    result = solvers[current_algo_name].solve(grid, grid.start, grid.goal)
                    anim_step = 0
                    is_animating = True
                elif event.key == pygame.K_3:
                    current_algo_name = "BFS"
                    result = solvers[current_algo_name].solve(grid, grid.start, grid.goal)
                    anim_step = 0
                    is_animating = True
                elif event.key == pygame.K_F1:
                    grid = WarehousePresets.amazon_fulfillment(grid.rows, grid.cols)
                    result = solvers[current_algo_name].solve(grid, grid.start, grid.goal)
                    anim_step = 0
                elif event.key == pygame.K_F2:
                    grid = WarehousePresets.bottleneck_maze(grid.rows, grid.cols)
                    result = solvers[current_algo_name].solve(grid, grid.start, grid.goal)
                    anim_step = 0
                elif event.key == pygame.K_F3:
                    grid = WarehousePresets.weighted_traffic_depot(grid.rows, grid.cols)
                    result = solvers[current_algo_name].solve(grid, grid.start, grid.goal)
                    anim_step = 0

            elif pygame.mouse.get_pressed()[0]: # Left click draw
                mx, my = pygame.mouse.get_pos()
                if my < grid.rows * renderer.cell_size:
                    c = mx // renderer.cell_size
                    r = my // renderer.cell_size
                    if grid.is_valid(r, c):
                        grid.set_cell(r, c, draw_mode)
                        result = solvers[current_algo_name].solve(grid, grid.start, grid.goal)
                        anim_step = len(result.steps) - 1

        # Advance animation
        if is_animating and result and result.steps:
            anim_step = min(len(result.steps) - 1, anim_step + anim_speed)
            if anim_step >= len(result.steps) - 1:
                is_animating = False

        # Render frame
        current_step_obj = result.steps[anim_step] if result and result.steps and anim_step < len(result.steps) else None
        final_path_render = result.path if (anim_step >= len(result.steps) - 1 if result and result.steps else True) else None

        frame_rgb = renderer.render_frame(
            grid=grid,
            current_step=current_step_obj,
            final_path=final_path_render,
            algo_name=current_algo_name,
            show_values=show_values,
            value_mode="f_score" if "A*" in current_algo_name else "g_score"
        )

        # Draw frame to screen
        surf = pygame.surfarray.make_surface(np.transpose(frame_rgb, (1, 0, 2)))
        screen.blit(surf, (0, 0))

        # Render HUD Banner at bottom
        hud_rect = pygame.Rect(0, grid.rows * renderer.cell_size, width, hud_height)
        pygame.draw.rect(screen, (15, 23, 42), hud_rect)
        pygame.draw.line(screen, (51, 65, 85), (0, hud_rect.top), (width, hud_rect.top), 2)

        title_txt = font_title.render(f"Algorithm: {current_algo_name} | State: {'ANIMATING' if is_animating else 'COMPLETE'}", True, (248, 250, 252))
        screen.blit(title_txt, (15, hud_rect.top + 10))

        dist_str = f"{result.distance:.1f}" if result.found else "No Path"
        exp_count = len(result.explored_cells) if result else 0
        stats_txt = font_hud.render(f"Distance Cost: {dist_str}  |  Cells Explored: {exp_count}  |  Execution Time: {result.execution_time_ms:.2f} ms", True, (56, 189, 248))
        screen.blit(stats_txt, (15, hud_rect.top + 35))

        controls_txt = font_hud.render("[1: A*] [2: Dijkstra] [3: BFS]  |  [SPACE: Play/Pause] [R: Reset] [C: Clear] [V: Toggle Cost Values] [F1-F3: Presets]", True, (148, 163, 184))
        screen.blit(controls_txt, (15, hud_rect.top + 60))

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main()
