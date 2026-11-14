"""
Alternative Routes and Road Management Module for Smart Campus Navigator
Fundamentals of AI (CF321) - Project 1

Features:
1. Smart Multi-Alternative Route Generator:
   Calculates the primary optimal A* path, then discovers up to 3 distinct, high-quality
   alternative routes using repeated A* searches (Yen's K-shortest paths with edge avoidance).
   All pathfinding is performed strictly via A* Search.
   Compares distance, cost, and steps transparently.

2. Road Closure Management:
   Allows simulating campus maintenance, construction, or temporary closures.
   Dynamically enables/disables graph edges and reroutes immediately using A*.

3. Route Query History:
   Maintains a recent history of user queries with distance, cost, and timestamps.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Set
import datetime

from campus_map import CampusGraph, Walkway
from astar import astar_search, SearchResult, euclidean_distance_heuristic


@dataclass
class RouteComparison:
    """Stores side-by-side comparison between the optimal A* route and alternative routes."""
    best_route: SearchResult
    alternative_routes: List[SearchResult] = field(default_factory=list)
    alternative_route: Optional[SearchResult] = None
    has_alternative: bool = False
    distance_difference_m: int = 0
    cost_difference: int = 0
    percentage_difference: float = 0.0

    @property
    def all_routes(self) -> List[SearchResult]:
        """Returns the optimal route followed by all discovered alternative routes."""
        if self.best_route and self.best_route.found:
            return [self.best_route] + [r for r in self.alternative_routes if r.found]
        return []


@dataclass
class HistoryEntry:
    """Stores a record in the route planning history."""
    start_id: str
    goal_id: str
    start_name: str
    goal_name: str
    distance_m: int
    cost: int
    found: bool
    timestamp: str


class RouteManager:
    """Coordinates route calculation, multi-alternative generation, road closures, and history."""

    def __init__(self, graph: CampusGraph):
        self.graph = graph
        self.history: List[HistoryEntry] = []

    def find_best_and_alternatives(
        self,
        start_id: str,
        goal_id: str,
        cost_metric: str = "distance",
        max_alternatives: int = 3
    ) -> RouteComparison:
        """
        Calculates the primary optimal A* route and finds up to 3 distinct valid alternative routes.
        All candidate paths are derived exclusively through repeated A* searches.
        """
        heuristic_fn = euclidean_distance_heuristic

        # Step 1: Calculate the primary optimal A* route
        best_res = astar_search(
            self.graph,
            start_id,
            goal_id,
            heuristic_fn=heuristic_fn,
            cost_metric=cost_metric
        )

        # Record this search in history
        self._record_history(start_id, goal_id, best_res)

        # If no path found or trivial 1-node path, no alternatives can exist
        if not best_res.found or len(best_res.path) <= 2:
            return RouteComparison(
                best_route=best_res,
                alternative_routes=[],
                alternative_route=None,
                has_alternative=False,
                distance_difference_m=0,
                cost_difference=0,
                percentage_difference=0.0
            )

        # Helper to compute exact distance and cost along a path from graph edges
        def compute_path_metrics(path: List[str]) -> Optional[Tuple[int, int]]:
            total_dist = 0
            total_cost_val = 0
            for i in range(len(path) - 1):
                edge = self.graph.get_edge(path[i], path[i + 1])
                if not edge or not edge.is_open:
                    return None
                total_dist += edge.distance_m
                total_cost_val += edge.cost
            return total_dist, total_cost_val

        # Step 2: Discover alternative routes using repeated A* searches
        # A contains selected shortest simple paths starting with best_res
        A: List[SearchResult] = [best_res]
        seen_paths: Set[Tuple[str, ...]] = {tuple(best_res.path)}
        candidate_pool: List[SearchResult] = []

        # Target total routes = 1 optimal + max_alternatives (e.g. 1 + 3 = 4)
        target_total = 1 + max_alternatives

        for k in range(1, target_total):
            prev_res = A[k - 1]
            prev_path = prev_res.path

            for i in range(len(prev_path) - 1):
                spur_node = prev_path[i]
                root_path = prev_path[:i + 1]

                # Identify edges to avoid for this spur search
                edges_to_avoid: List[Tuple[str, str]] = []

                # Avoid edges used by any known path in A sharing root_path up to spur_node
                for p_obj in A:
                    p = p_obj.path
                    if len(p) > i + 1 and p[:i + 1] == root_path:
                        edges_to_avoid.append((p[i], p[i + 1]))

                # Avoid earlier nodes in root_path (prevent loops in spur search)
                for prev_node in root_path[:-1]:
                    for nbr, _ in self.graph.get_neighbors(prev_node, include_closed=True):
                        edges_to_avoid.append((prev_node, nbr))

                # Execute A* search from spur node to goal
                spur_res = astar_search(
                    self.graph,
                    spur_node,
                    goal_id,
                    heuristic_fn=heuristic_fn,
                    cost_metric=cost_metric,
                    avoid_edges=edges_to_avoid
                )

                if spur_res.found and len(spur_res.path) > 1:
                    total_candidate_path = root_path[:-1] + spur_res.path
                    # Ensure candidate is simple (no cycles)
                    if len(total_candidate_path) == len(set(total_candidate_path)):
                        tup_path = tuple(total_candidate_path)
                        if tup_path not in seen_paths:
                            seen_paths.add(tup_path)
                            metrics = compute_path_metrics(total_candidate_path)
                            if metrics is not None:
                                c_dist, c_cost = metrics
                                c_res = SearchResult(
                                    path=total_candidate_path,
                                    total_distance_m=c_dist,
                                    total_cost=c_cost,
                                    nodes_explored=spur_res.nodes_explored,
                                    explored_order=spur_res.explored_order,
                                    found=True,
                                    execution_time_ms=spur_res.execution_time_ms,
                                    start_id=start_id,
                                    goal_id=goal_id,
                                    heuristic_name=heuristic_fn.__name__
                                )
                                candidate_pool.append(c_res)

            # Also perform edge-avoidance searches on all edges in discovered paths
            for p_obj in list(A):
                p = p_obj.path
                for seg_i in range(len(p) - 1):
                    seg_edge = (p[seg_i], p[seg_i + 1])
                    alt_edge_res = astar_search(
                        self.graph,
                        start_id,
                        goal_id,
                        heuristic_fn=heuristic_fn,
                        cost_metric=cost_metric,
                        avoid_edges=[seg_edge]
                    )
                    if alt_edge_res.found and len(alt_edge_res.path) > 1:
                        if len(alt_edge_res.path) == len(set(alt_edge_res.path)):
                            tup_p = tuple(alt_edge_res.path)
                            if tup_p not in seen_paths:
                                seen_paths.add(tup_p)
                                candidate_pool.append(alt_edge_res)

            if not candidate_pool:
                break

            # Sort candidates by cost metric
            if cost_metric == "distance":
                candidate_pool.sort(key=lambda r: (r.total_distance_m, r.total_cost, len(r.path)))
            else:
                candidate_pool.sort(key=lambda r: (r.total_cost, r.total_distance_m, len(r.path)))

            next_route = candidate_pool.pop(0)
            A.append(next_route)

        # Extract alternative routes (excluding best_res)
        alternative_routes: List[SearchResult] = A[1:1 + max_alternatives]
        has_alt = len(alternative_routes) > 0
        primary_alt = alternative_routes[0] if has_alt else None

        if primary_alt:
            dist_diff = primary_alt.total_distance_m - best_res.total_distance_m
            cost_diff = primary_alt.total_cost - best_res.total_cost
            pct_diff = (dist_diff / best_res.total_distance_m * 100.0) if best_res.total_distance_m > 0 else 0.0
        else:
            dist_diff = 0
            cost_diff = 0
            pct_diff = 0.0

        return RouteComparison(
            best_route=best_res,
            alternative_routes=alternative_routes,
            alternative_route=primary_alt,
            has_alternative=has_alt,
            distance_difference_m=dist_diff,
            cost_difference=cost_diff,
            percentage_difference=round(pct_diff, 1)
        )

    def find_best_and_alternative(
        self,
        start_id: str,
        goal_id: str,
        cost_metric: str = "distance"
    ) -> RouteComparison:
        """Backwards-compatible wrapper returning best route and up to 3 alternative routes."""
        return self.find_best_and_alternatives(start_id, goal_id, cost_metric=cost_metric, max_alternatives=3)

    def close_road(self, u: str, v: str) -> bool:
        """Temporarily close walkway between u and v."""
        return self.graph.close_walkway(u, v)

    def reopen_road(self, u: str, v: str) -> bool:
        """Reopen walkway between u and v."""
        return self.graph.reopen_walkway(u, v)

    def toggle_road(self, u: str, v: str) -> bool:
        """Toggle open/closed status of walkway between u and v."""
        return self.graph.toggle_walkway(u, v)

    def reopen_all_roads(self):
        """Reopen all roads on campus."""
        self.graph.reset_all_closures()

    def get_closed_roads(self) -> List[Walkway]:
        """Get list of closed roads."""
        return self.graph.get_closed_walkways()

    def _record_history(self, start_id: str, goal_id: str, result: SearchResult):
        """Append route calculation to user session history."""
        start_loc = self.graph.get_location(start_id)
        goal_loc = self.graph.get_location(goal_id)
        start_name = start_loc.name if start_loc else start_id
        goal_name = goal_loc.name if goal_loc else goal_id

        entry = HistoryEntry(
            start_id=start_id,
            goal_id=goal_id,
            start_name=start_name,
            goal_name=goal_name,
            distance_m=result.total_distance_m,
            cost=result.total_cost,
            found=result.found,
            timestamp=datetime.datetime.now().strftime("%I:%M %p")
        )

        # Prepend to history, keeping max 20 entries
        self.history.insert(0, entry)
        if len(self.history) > 20:
            self.history.pop()

    def get_recent_history(self) -> List[HistoryEntry]:
        """Retrieve recent query history."""
        return list(self.history)
