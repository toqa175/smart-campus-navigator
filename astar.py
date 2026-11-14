"""
A* Search Algorithm Module for Smart Campus Navigator
Fundamentals of AI (CF321) - Project 1

This module implements the custom A* Search algorithm from scratch.
f(n) = g(n) + h(n)
where:
- g(n): Actual cost from the start node to node n.
- h(n): Estimated cost from node n to the goal node (admissible heuristic).
- f(n): Estimated total cost of the cheapest solution path through node n.

Guarantees:
- Written purely using Python standard library (heapq, math, time, typing).
- Completely decoupled from the GUI for clean automated testing.
- Tracks nodes explored, expansion order, total distance, and path reconstruction.
"""

from dataclasses import dataclass
import heapq
import time
from typing import Callable, Dict, List, Optional, Tuple

# Import CampusGraph and Walkway
from campus_map import CampusGraph, Walkway


@dataclass
class SearchResult:
    """Encapsulates the complete outcome of an A* pathfinding query."""
    path: List[str]                  # Ordered list of node IDs from start to goal
    total_distance_m: int            # Total physical distance along the route in meters
    total_cost: int                  # Total cost metric along the route
    nodes_explored: int              # Number of unique nodes expanded from the priority queue
    explored_order: List[str]        # Sequence in which nodes were evaluated
    found: bool                      # True if valid path exists, False otherwise
    execution_time_ms: float         # Wall-clock search duration in milliseconds
    start_id: str                    # Starting location ID
    goal_id: str                     # Destination location ID
    heuristic_name: str              # Identifier of heuristic function applied


def euclidean_distance_heuristic(node_id: str, goal_id: str, graph: CampusGraph) -> float:
    """
    Admissible and consistent Euclidean distance heuristic.
    h(n) = straight_line_distance(node, goal) in meters.
    Since a straight line is the shortest possible path between two points in Euclidean space,
    h(n) <= h*(n) holds universally, guaranteeing admissibility and optimality.
    """
    return graph.straight_line_distance_m(node_id, goal_id)


def astar_search(
    graph: CampusGraph,
    start_id: str,
    goal_id: str,
    heuristic_fn: Callable[[str, str, CampusGraph], float] = euclidean_distance_heuristic,
    cost_metric: str = "distance",   # 'distance' (meters) or 'cost' (effort rating)
    avoid_edges: Optional[List[Tuple[str, str]]] = None,
) -> SearchResult:
    """
    Executes the A* pathfinding algorithm on the campus graph.

    Args:
        graph: The CampusGraph instance.
        start_id: ID of the starting location.
        goal_id: ID of the target destination.
        heuristic_fn: Function h(current, goal, graph) estimating remaining cost.
        cost_metric: 'distance' to optimize physical meters, 'cost' to optimize effort rating.
        avoid_edges: Optional list of (u, v) edge tuples to temporarily ignore (for alternative routes).

    Returns:
        SearchResult containing the optimal path, costs, and exploration metrics.
    """
    t_start = time.perf_counter()

    # Validate that start and destination nodes exist in the graph
    if start_id not in graph.locations or goal_id not in graph.locations:
        elapsed_ms = (time.perf_counter() - t_start) * 1000.0
        return SearchResult(
            path=[],
            total_distance_m=0,
            total_cost=0,
            nodes_explored=0,
            explored_order=[],
            found=False,
            execution_time_ms=elapsed_ms,
            start_id=start_id,
            goal_id=goal_id,
            heuristic_name=heuristic_fn.__name__,
        )

    # Edge Case: Start and Goal are identical
    if start_id == goal_id:
        elapsed_ms = (time.perf_counter() - t_start) * 1000.0
        return SearchResult(
            path=[start_id],
            total_distance_m=0,
            total_cost=0,
            nodes_explored=1,
            explored_order=[start_id],
            found=True,
            execution_time_ms=elapsed_ms,
            start_id=start_id,
            goal_id=goal_id,
            heuristic_name=heuristic_fn.__name__,
        )

    # Set of avoided edges (both directions)
    avoid_set = set()
    if avoid_edges:
        for u, v in avoid_edges:
            avoid_set.add((u, v))
            avoid_set.add((v, u))

    # Priority queue storing tuples: (f_score, counter, current_node_id)
    # A tie-breaker counter ensures stable FIFO ordering when f_scores match
    heap: List[Tuple[float, int, str]] = []
    counter = 0

    # g_score[node] stores the lowest known cost from start to node
    g_score: Dict[str, float] = {start_id: 0.0}

    # Track parent pointers for optimal path reconstruction: child -> parent
    came_from: Dict[str, str] = {}

    # Track walkway used to reach each node for accurate distance & cost summation
    edge_used: Dict[str, Walkway] = {}

    # Initialize start node
    h_start = heuristic_fn(start_id, goal_id, graph)
    heapq.heappush(heap, (h_start, counter, start_id))
    counter += 1

    # Keep track of closed (settled) nodes and exploration sequence
    closed_set = set()
    explored_order: List[str] = []

    goal_reached = False

    while heap:
        f_curr, _, current = heapq.heappop(heap)

        if current in closed_set:
            continue

        closed_set.add(current)
        explored_order.append(current)

        # Check if destination reached
        if current == goal_id:
            goal_reached = True
            break

        current_g = g_score[current]

        # Expand all accessible adjacent neighbors
        for neighbor, walkway in graph.get_neighbors(current, include_closed=False):
            # Check if this edge is in the temporary avoidance set
            if (current, neighbor) in avoid_set:
                continue

            # Determine transition cost
            step_cost = walkway.distance_m if cost_metric == "distance" else walkway.cost
            tentative_g = current_g + step_cost

            # If a shorter path to this neighbor is discovered
            if tentative_g < g_score.get(neighbor, float("inf")):
                came_from[neighbor] = current
                edge_used[neighbor] = walkway
                g_score[neighbor] = tentative_g

                # f(n) = g(n) + h(n)
                h_val = heuristic_fn(neighbor, goal_id, graph)
                f_val = tentative_g + h_val

                heapq.heappush(heap, (f_val, counter, neighbor))
                counter += 1

    elapsed_ms = (time.perf_counter() - t_start) * 1000.0

    if not goal_reached:
        return SearchResult(
            path=[],
            total_distance_m=0,
            total_cost=0,
            nodes_explored=len(closed_set),
            explored_order=explored_order,
            found=False,
            execution_time_ms=elapsed_ms,
            start_id=start_id,
            goal_id=goal_id,
            heuristic_name=heuristic_fn.__name__,
        )

    # Reconstruct the optimal path by walking backwards from goal to start
    path = []
    curr = goal_id
    total_dist = 0
    total_cost_val = 0

    while curr in came_from:
        path.append(curr)
        w = edge_used[curr]
        total_dist += w.distance_m
        total_cost_val += w.cost
        curr = came_from[curr]

    path.append(start_id)
    path.reverse()

    return SearchResult(
        path=path,
        total_distance_m=total_dist,
        total_cost=total_cost_val,
        nodes_explored=len(closed_set),
        explored_order=explored_order,
        found=True,
        execution_time_ms=elapsed_ms,
        start_id=start_id,
        goal_id=goal_id,
        heuristic_name=heuristic_fn.__name__,
    )
