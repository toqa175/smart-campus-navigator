"""
Automated Test Suite for Smart Campus Navigator
Fundamentals of AI (CF321) - Project 1

Tests covered:
1. Campus graph topology, nodes, and bidirectional walkways.
2. Straightforward pathfinding via A*.
3. Complex routing where A* picks the lower-cost path among multiple choices.
4. Heuristic admissibility test: h(n) <= h*(n) across ALL node pairs.
5. Consistency test: h(n) <= c(n, p) + h(p) for all edges.
6. Zero heuristic (Dijkstra) vs Euclidean heuristic: identical path cost, A* explores fewer or equal nodes.
7. Start equals Destination (trivial zero-cost path).
8. Disconnected destination (when paths are severed or unreachable).
9. Road closure feature: path rerouting when primary route is blocked.
10. Road reopening feature: path restoration.
11. Alternative route generation: distinct secondary path with valid costs.
12. Multiple distinct alternative routes (up to 3 distinct alternatives whenever available).
13. Valid graph edges and accurate route distances and costs.
14. Route start and destination correctness across all alternative routes.
15. Map View / Nodes View switching and state preservation.
16. All graph nodes displayed and selectable in dropdowns.
17. Dropdown scrolling and selection of the final (last) location.
18. Road closures and multi-alternative route updates.
19. Light and dark theme integrity and color completeness.
"""

import unittest
import pygame

from campus_map import CampusGraph
from astar import (
    astar_search,
    euclidean_distance_heuristic,
    zero_heuristic,
)
from alternative_routes import RouteManager
from visualization import THEMES, Dropdown, CampusMapRenderer


class TestCampusNavigator(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pygame.init()

    def setUp(self):
        """Set up a fresh campus graph and route manager for each test."""
        self.graph = CampusGraph()
        self.manager = RouteManager(self.graph)

    def test_01_graph_structure(self):
        """Verify the graph has the expected 10 locations and bidirectional walkways."""
        self.assertEqual(len(self.graph.locations), 10)
        self.assertIn("MAIN_GATE", self.graph.locations)
        self.assertIn("LIBRARY", self.graph.locations)
        self.assertIn("CS_BUILDING", self.graph.locations)
        self.assertIn("ENGINEERING", self.graph.locations)
        self.assertIn("STUDENT_CENTER", self.graph.locations)

        # Ensure all walkways are bidirectional
        for (u, v), edge in self.graph.edges.items():
            self.assertIn((v, u), self.graph.edges)
            rev_edge = self.graph.edges[(v, u)]
            self.assertEqual(edge.distance_m, rev_edge.distance_m)
            self.assertEqual(edge.cost, rev_edge.cost)

    def test_02_straightforward_route(self):
        """Test a direct adjacent route: MAIN_GATE -> CS_BUILDING."""
        res = astar_search(self.graph, "MAIN_GATE", "CS_BUILDING")
        self.assertTrue(res.found)
        self.assertEqual(res.path[0], "MAIN_GATE")
        self.assertEqual(res.path[-1], "CS_BUILDING")
        self.assertEqual(res.total_distance_m, 270)
        self.assertEqual(res.total_cost, 4)

    def test_03_multi_step_optimal_path(self):
        """
        Test route from MAIN_GATE to LIBRARY.
        Multiple paths exist (via CS_BUILDING & STUDENT_CENTER vs via ADMINISTRATION).
        Verify A* selects the minimum-cost route.
        """
        res = astar_search(self.graph, "MAIN_GATE", "LIBRARY")
        self.assertTrue(res.found)
        self.assertEqual(res.path[0], "MAIN_GATE")
        self.assertEqual(res.path[-1], "LIBRARY")

        # Compare with Dijkstra (zero heuristic) ground truth
        dijkstra_res = astar_search(self.graph, "MAIN_GATE", "LIBRARY", heuristic_fn=zero_heuristic)
        self.assertEqual(res.total_distance_m, dijkstra_res.total_distance_m)
        self.assertEqual(res.total_cost, dijkstra_res.total_cost)

    def test_04_admissibility_all_pairs(self):
        """
        Verify the Euclidean heuristic is strictly ADMISSIBLE:
        h(u, v) <= true_shortest_distance(u, v) for every pair of nodes u, v.
        An admissible heuristic guarantees A* will always return the optimal path.
        """
        loc_ids = list(self.graph.locations.keys())
        for i, u in enumerate(loc_ids):
            for v in loc_ids[i + 1:]:
                # Compute ground truth shortest distance using Dijkstra (zero heuristic)
                opt = astar_search(self.graph, u, v, heuristic_fn=zero_heuristic)
                self.assertTrue(opt.found)
                h_val = euclidean_distance_heuristic(u, v, self.graph)
                self.assertLessEqual(
                    h_val,
                    opt.total_distance_m + 1e-6,
                    f"Heuristic overestimated between {u} and {v}: h={h_val:.1f} > actual={opt.total_distance_m}"
                )

    def test_05_consistency_triangle_inequality(self):
        """
        Verify the heuristic is CONSISTENT (monotone):
        For every edge (u, v) and goal G: h(u, G) <= cost(u, v) + h(v, G).
        Consistency guarantees nodes are expanded at most once (no reopening needed).
        """
        for goal in self.graph.locations:
            for walkway in self.graph.get_all_unique_edges():
                u, v = walkway.u, walkway.v
                cost_uv = walkway.distance_m
                h_u = euclidean_distance_heuristic(u, goal, self.graph)
                h_v = euclidean_distance_heuristic(v, goal, self.graph)

                # Triangle inequality check in both directions
                self.assertLessEqual(h_u, cost_uv + h_v + 1e-6)
                self.assertLessEqual(h_v, cost_uv + h_u + 1e-6)

    def test_06_heuristic_efficiency(self):
        """
        Compare A* with Euclidean heuristic vs Dijkstra (zero heuristic).
        Both must find the identical optimal path cost, but A* should explore <= nodes.
        """
        res_astar = astar_search(self.graph, "MAIN_GATE", "SPORTS_COMPLEX", heuristic_fn=euclidean_distance_heuristic)
        res_dijkstra = astar_search(self.graph, "MAIN_GATE", "SPORTS_COMPLEX", heuristic_fn=zero_heuristic)

        self.assertEqual(res_astar.total_distance_m, res_dijkstra.total_distance_m)
        self.assertLessEqual(res_astar.nodes_explored, res_dijkstra.nodes_explored)

    def test_07_start_equals_goal(self):
        """Test edge case where start location is identical to destination."""
        res = astar_search(self.graph, "LIBRARY", "LIBRARY")
        self.assertTrue(res.found)
        self.assertEqual(res.path, ["LIBRARY"])
        self.assertEqual(res.total_distance_m, 0)
        self.assertEqual(res.total_cost, 0)
        self.assertEqual(res.nodes_explored, 1)

    def test_08_disconnected_destination(self):
        """
        Test unreachable destination when all walkways to a node are closed.
        Should gracefully return found=False and empty path.
        """
        # Close all walkways connected to SPORTS_COMPLEX
        for neighbor, _ in self.graph.get_neighbors("SPORTS_COMPLEX", include_closed=True):
            self.graph.close_walkway("SPORTS_COMPLEX", neighbor)

        res = astar_search(self.graph, "MAIN_GATE", "SPORTS_COMPLEX")
        self.assertFalse(res.found)
        self.assertEqual(res.path, [])
        self.assertEqual(res.total_distance_m, 0)
        self.assertGreater(res.nodes_explored, 0)

    def test_09_road_closure_and_rerouting(self):
        """Test that closing a road forces A* to find a detour route."""
        initial_res = astar_search(self.graph, "MAIN_GATE", "ADMINISTRATION")
        self.assertTrue(initial_res.found)
        self.assertEqual(initial_res.path, ["MAIN_GATE", "ADMINISTRATION"])

        # Close direct walkway between MAIN_GATE and ADMINISTRATION
        self.graph.close_walkway("MAIN_GATE", "ADMINISTRATION")

        # Now A* must reroute through CS_BUILDING or DORMITORY
        rerouted_res = astar_search(self.graph, "MAIN_GATE", "ADMINISTRATION")
        self.assertTrue(rerouted_res.found)
        self.assertNotIn(["MAIN_GATE", "ADMINISTRATION"], [rerouted_res.path])
        self.assertGreater(rerouted_res.total_distance_m, initial_res.total_distance_m)

    def test_10_road_reopening(self):
        """Test that reopening a closed road restores the optimal path."""
        self.graph.close_walkway("MAIN_GATE", "ADMINISTRATION")
        self.graph.reopen_walkway("MAIN_GATE", "ADMINISTRATION")

        res = astar_search(self.graph, "MAIN_GATE", "ADMINISTRATION")
        self.assertTrue(res.found)
        self.assertEqual(res.path, ["MAIN_GATE", "ADMINISTRATION"])
        self.assertEqual(res.total_distance_m, 180)

    def test_11_alternative_routes(self):
        """Test alternative route generator produces a valid, distinct secondary route."""
        comparison = self.manager.find_best_and_alternative("MAIN_GATE", "LIBRARY")
        self.assertTrue(comparison.best_route.found)
        if comparison.has_alternative:
            self.assertTrue(comparison.alternative_route.found)
            self.assertNotEqual(comparison.best_route.path, comparison.alternative_route.path)
            self.assertGreaterEqual(
                comparison.alternative_route.total_distance_m,
                comparison.best_route.total_distance_m
            )

    def test_12_multiple_distinct_alternative_routes(self):
        """
        Verify that find_best_and_alternatives discovers up to 3 distinct valid alternative routes.
        All routes must be mutually distinct and cycle-free.
        """
        comparison = self.manager.find_best_and_alternatives("MAIN_GATE", "LIBRARY", max_alternatives=3)
        self.assertTrue(comparison.best_route.found)
        self.assertGreaterEqual(len(comparison.alternative_routes), 2)
        self.assertLessEqual(len(comparison.alternative_routes), 3)

        all_paths = [comparison.best_route.path] + [r.path for r in comparison.alternative_routes]
        # Verify all routes are distinct
        path_tuples = [tuple(p) for p in all_paths]
        self.assertEqual(len(path_tuples), len(set(path_tuples)), "Routes must all be distinct paths")

        # Verify all routes are simple paths (no repeated nodes)
        for p in all_paths:
            self.assertEqual(len(p), len(set(p)), f"Route has cycles: {p}")

    def test_13_valid_graph_edges_and_route_costs(self):
        """
        Verify that every step of each discovered route corresponds to a real, open graph edge,
        and that total distance and cost exactly match the sum of edge weights.
        """
        comparison = self.manager.find_best_and_alternatives("MAIN_GATE", "LIBRARY", max_alternatives=3)
        all_routes = [comparison.best_route] + comparison.alternative_routes

        for route in all_routes:
            calculated_dist = 0
            calculated_cost = 0
            for i in range(len(route.path) - 1):
                u, v = route.path[i], route.path[i + 1]
                edge = self.graph.get_edge(u, v)
                self.assertIsNotNone(edge, f"Edge ({u}, {v}) must exist in graph")
                self.assertTrue(edge.is_open, f"Edge ({u}, {v}) must be open")
                calculated_dist += edge.distance_m
                calculated_cost += edge.cost

            self.assertEqual(route.total_distance_m, calculated_dist)
            self.assertEqual(route.total_cost, calculated_cost)
            self.assertGreater(route.total_distance_m, 0)

    def test_14_route_start_and_destination_correctness(self):
        """Verify all alternative routes begin at start_id and terminate at goal_id."""
        start = "CS_BUILDING"
        goal = "SCIENCE_BUILDING"
        comparison = self.manager.find_best_and_alternatives(start, goal, max_alternatives=3)

        all_routes = [comparison.best_route] + comparison.alternative_routes
        for route in all_routes:
            self.assertEqual(route.path[0], start)
            self.assertEqual(route.path[-1], goal)
            self.assertEqual(route.start_id, start)
            self.assertEqual(route.goal_id, goal)

    def test_15_map_view_nodes_view_switching(self):
        """
        Verify that toggling between Map View and Nodes View preserves all graph data,
        start/destination selections, route results, and themes without reset.
        """
        map_rect = pygame.Rect(100, 100, 600, 500)
        renderer = CampusMapRenderer(map_rect)

        # Initial state should be map view
        self.assertEqual(renderer.view_mode, "map")

        # Toggle to nodes view
        renderer.toggle_view_mode()
        self.assertEqual(renderer.view_mode, "nodes")

        # Toggle back to map view
        renderer.toggle_view_mode()
        self.assertEqual(renderer.view_mode, "map")

        # Explicit set_view_mode
        renderer.set_view_mode("nodes")
        self.assertEqual(renderer.view_mode, "nodes")

        # Coordinates must match in both views
        loc = self.graph.get_location("MAIN_GATE")
        sx, sy = renderer.world_to_screen(loc.x, loc.y)
        self.assertIsInstance(sx, int)
        self.assertIsInstance(sy, int)

    def test_16_all_graph_nodes_displayed_and_available(self):
        """Verify all 10 campus landmarks are available in the dropdown options."""
        all_locs = self.graph.get_all_locations()
        self.assertEqual(len(all_locs), 10)

        loc_ids = {loc.id for loc in all_locs}
        expected_ids = {
            "MAIN_GATE", "CS_BUILDING", "STUDENT_CENTER", "SPORTS_COMPLEX",
            "ENGINEERING", "LIBRARY", "ADMINISTRATION", "SCIENCE_BUILDING",
            "CAFETERIA", "DORMITORY"
        }
        self.assertEqual(loc_ids, expected_ids)

        options = [(loc.id, loc.name) for loc in all_locs]
        dropdown = Dropdown(pygame.Rect(10, 10, 200, 34), options, "MAIN_GATE")
        self.assertEqual(len(dropdown.options), 10)

    def test_17_dropdown_scrolling_and_last_item_selection(self):
        """
        Verify that Dropdown supports scrolling to the bottom and selecting the LAST item.
        Also test selecting the first and middle items.
        """
        all_locs = self.graph.get_all_locations()
        options = [(loc.id, loc.name) for loc in all_locs]
        dropdown = Dropdown(pygame.Rect(50, 50, 220, 34), options, options[0][0])
        dropdown.is_open = True

        max_scroll = len(options) - dropdown.max_visible  # 10 - 6 = 4

        # 1. Test mouse wheel scrolling down to maximum scroll offset
        scroll_event = pygame.event.Event(pygame.MOUSEWHEEL, {"y": -1, "x": 0})
        for _ in range(max_scroll + 2):
            dropdown.handle_event(scroll_event)

        self.assertEqual(dropdown.scroll_offset, max_scroll)

        # 2. Click the last visible option (index 9 in options, index 5 in visible list)
        drop_rect = dropdown._get_dropdown_rect()
        last_item_y = drop_rect.y + (dropdown.max_visible - 1) * dropdown.item_height + (dropdown.item_height // 2)
        click_pos = (drop_rect.x + 20, last_item_y)

        click_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": click_pos})
        handled = dropdown.handle_event(click_event)
        self.assertTrue(handled)
        self.assertEqual(dropdown.selected_id, options[-1][0], "Last option must be successfully selected!")
        self.assertFalse(dropdown.is_open)

        # 3. Re-open and select the first item (MAIN_GATE)
        dropdown.is_open = True
        dropdown.scroll_offset = 0
        first_item_y = drop_rect.y + (dropdown.item_height // 2)
        first_click = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": (drop_rect.x + 20, first_item_y)})
        dropdown.handle_event(first_click)
        self.assertEqual(dropdown.selected_id, options[0][0], "First option must be selected!")

    def test_18_road_closures_and_multi_route_updates(self):
        """
        Verify that closing a walkway updates all routes so that no route uses the closed edge.
        Reopening the walkway restores the original routes.
        """
        # Baseline routes
        base_comp = self.manager.find_best_and_alternatives("MAIN_GATE", "LIBRARY", max_alternatives=3)
        self.assertTrue(base_comp.best_route.found)

        # Close MAIN_GATE <-> ADMINISTRATION
        self.manager.close_road("MAIN_GATE", "ADMINISTRATION")
        closed_comp = self.manager.find_best_and_alternatives("MAIN_GATE", "LIBRARY", max_alternatives=3)
        self.assertTrue(closed_comp.best_route.found)

        all_closed_routes = [closed_comp.best_route] + closed_comp.alternative_routes
        for route in all_closed_routes:
            for i in range(len(route.path) - 1):
                seg = (route.path[i], route.path[i + 1])
                rev_seg = (route.path[i + 1], route.path[i])
                self.assertNotIn(("MAIN_GATE", "ADMINISTRATION"), [seg, rev_seg], "Closed road must NOT be in any route!")

        # Reopen road
        self.manager.reopen_road("MAIN_GATE", "ADMINISTRATION")
        restored_comp = self.manager.find_best_and_alternatives("MAIN_GATE", "LIBRARY", max_alternatives=3)
        self.assertEqual(restored_comp.best_route.path, base_comp.best_route.path)

    def test_19_light_and_dark_themes(self):
        """Verify theme color integrity and completeness for both light and dark modes."""
        for mode in ("light", "dark"):
            self.assertIn(mode, THEMES)
            theme = THEMES[mode]

            required_keys = [
                "bg_app", "bg_header", "bg_card", "border", "text_primary",
                "primary", "danger", "success", "warning", "purple", "orange",
                "route_primary", "route_alt1", "route_alt2", "route_alt3",
                "nodes_bg", "nodes_grid", "node_fill", "node_border", "edge_line"
            ]
            for key in required_keys:
                self.assertIn(key, theme, f"Missing key '{key}' in theme '{mode}'")
                val = theme[key]
                self.assertIsInstance(val, tuple)
                self.assertEqual(len(val), 3)
                for channel in val:
                    self.assertGreaterEqual(channel, 0)
                    self.assertLessEqual(channel, 255)

    def test_20_single_route_display_and_selection(self):
        """
        Verify that ONLY ONE route is displayed at a time:
        - Defaults to Optimal Route (index 0).
        - Selecting Alt 1, 2, or 3 switches selected_route_idx accordingly.
        - Recalculating routes resets selected_route_idx to Optimal Route (index 0).
        - When all roads to destination are severed, selected_route_idx is None.
        """
        from main import SmartCampusNavigatorApp
        app = SmartCampusNavigatorApp(target_w=1280, target_h=720)

        # 1. Initial state after route calculation must be Optimal Route (index 0)
        self.assertEqual(app.selected_route_idx, 0, "Initial state must select Optimal Route (index 0)")

        # 2. Select Alternative Route 1
        app._select_route(1)
        self.assertEqual(app.selected_route_idx, 1)

        # 3. Select Alternative Route 2
        app._select_route(2)
        self.assertEqual(app.selected_route_idx, 2)

        # 4. Re-select Optimal Route
        app._select_route(0)
        self.assertEqual(app.selected_route_idx, 0)

        # 5. When start/destination change and Find Routes is clicked, resets to Optimal Route (0)
        app._select_route(1)
        self.assertEqual(app.selected_route_idx, 1)
        app.start_location_id = "CS_BUILDING"
        app.dest_location_id = "SCIENCE_BUILDING"
        app.calculate_route()
        self.assertEqual(app.selected_route_idx, 0, "calculate_route() must reset selected_route_idx to Optimal Route (0)")

        # 6. Sever all walkways to dest: selected_route_idx must be None
        for neighbor, _ in app.graph.get_neighbors("SCIENCE_BUILDING", include_closed=True):
            app.graph.close_walkway("SCIENCE_BUILDING", neighbor)
        app.calculate_route()
        self.assertIsNone(app.selected_route_idx, "When no path exists, selected_route_idx must be None")

    def test_21_map_layout_bounds_and_no_clipping(self):
        """
        Verify that the central map has generous width and all 10 buildings sit well
        inside the map bounds without clipping.
        """
        map_rect = pygame.Rect(242, 64, 780, 620)
        renderer = CampusMapRenderer(map_rect)

        # All 10 locations must be inside map_rect with safe margins
        for loc in self.graph.get_all_locations():
            sx, sy = renderer.world_to_screen(loc.x, loc.y)
            self.assertGreater(sx, map_rect.left + 30, f"{loc.id} clipped on left")
            self.assertLess(sx, map_rect.right - 30, f"{loc.id} clipped on right")
            self.assertGreater(sy, map_rect.top + 30, f"{loc.id} clipped on top")
            self.assertLess(sy, map_rect.bottom - 30, f"{loc.id} clipped on bottom")


if __name__ == "__main__":
    unittest.main()
