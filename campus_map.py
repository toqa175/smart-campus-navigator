"""
Campus Graph Module for Smart Campus Navigator
Fundamentals of AI (CF321) - Project 1

This module defines the campus locations, coordinates, and walkway connections.
The campus is modeled as a weighted undirected graph G = (V, E, w) where:
- Vertices V represent university buildings and key campus landmarks.
- Edges E represent pedestrian walkways.
- Edge weights w represent walking distances in meters and travel cost ratings.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import math


@dataclass
class Location:
    """Represents a campus building or landmark."""
    id: str
    name: str
    x: float  # Normalized campus coordinate X [0.0, 1.0]
    y: float  # Normalized campus coordinate Y [0.0, 1.0]
    category: str
    icon_name: str
    description: str


@dataclass
class Walkway:
    """Represents a pedestrian walkway connecting two campus locations."""
    u: str
    v: str
    distance_m: int      # Walking distance in meters
    cost: int            # Cost rating (proportional to distance and slope/terrain)
    name: str            # Walkway title / description
    is_open: bool = True # Can be closed for maintenance or construction


class CampusGraph:
    """
    Weighted graph representing the university campus.
    Maintains locations (nodes) and bidirectional walkways (edges).
    Supports dynamic road closures and reopenings.
    """

    # Scale factor: 1.0 normalized unit equals 680 meters across campus.
    # Calibrated so straight-line distance is strictly <= physical walkway walking distance (admissible).
    CAMPUS_SCALE_METERS = 680.0

    def __init__(self):
        self.locations: Dict[str, Location] = {}
        self.adjacency: Dict[str, List[Walkway]] = {}
        self.edges: Dict[Tuple[str, str], Walkway] = {}
        self._initialize_default_campus()

    def _initialize_default_campus(self):
        """Build the default campus layout matching the reference university map."""
        
        # 10 prominent university buildings/locations matching reference design
        locations_data = [
            Location("MAIN_GATE", "Main Gate", 0.50, 0.91, "Entrance", "gate", "Primary south entrance to campus"),
            Location("CS_BUILDING", "Computer Science Building", 0.25, 0.65, "Academic", "computer", "Faculty of Computers & Information Technology"),
            Location("STUDENT_CENTER", "Student Center", 0.28, 0.38, "Services", "users", "Clubs, student activities, and lounges"),
            Location("SPORTS_COMPLEX", "Sports Complex", 0.20, 0.18, "Athletics", "sports", "Olympic track, gymnasium, and fields"),
            Location("ENGINEERING", "Engineering Building", 0.50, 0.16, "Academic", "gear", "Engineering labs, workshops, and lecture halls"),
            Location("LIBRARY", "Library", 0.50, 0.42, "Academic", "book", "Central library, study spaces, and research archives"),
            Location("ADMINISTRATION", "Administration", 0.50, 0.72, "Administrative", "building", "Dean's office, registrar, and student affairs"),
            Location("SCIENCE_BUILDING", "Science Building", 0.78, 0.20, "Academic", "flask", "Physics, Chemistry, and Biology laboratories"),
            Location("CAFETERIA", "Cafeteria", 0.75, 0.44, "Dining", "utensils", "Campus dining hall, cafes, and food court"),
            Location("DORMITORY", "Dormitory", 0.78, 0.72, "Residential", "bed", "Student residences and campus living quarters"),
        ]

        for loc in locations_data:
            self.add_location(loc)

        # Realistic walkway network with physical distances (meters) and travel costs
        # Ground-truth distances calibrated to ensure Euclidean distance heuristic is strictly admissible (h <= h*)
        walkways_data = [
            # Main Gate connections
            ("MAIN_GATE", "ADMINISTRATION", 180, 3, "Memorial Avenue"),
            ("MAIN_GATE", "CS_BUILDING", 270, 4, "West Entrance Walkway"),
            ("MAIN_GATE", "DORMITORY", 280, 5, "South East Boulevard"),

            # Computer Science connections
            ("CS_BUILDING", "STUDENT_CENTER", 230, 4, "Innovation Way"),
            ("CS_BUILDING", "ADMINISTRATION", 210, 3, "Central Tech Path"),
            ("CS_BUILDING", "LIBRARY", 260, 4, "Academic Promenade"),

            # Student Center connections
            ("STUDENT_CENTER", "SPORTS_COMPLEX", 190, 3, "Athletic Passage"),
            ("STUDENT_CENTER", "ENGINEERING", 220, 4, "North-West Boulevard"),
            ("STUDENT_CENTER", "LIBRARY", 180, 3, "Central Plaza Walkway"),

            # Sports Complex connections
            ("SPORTS_COMPLEX", "ENGINEERING", 240, 4, "North Perimeter Walkway"),

            # Engineering Building connections
            ("ENGINEERING", "LIBRARY", 210, 3, "Chancellor's Walk"),
            ("ENGINEERING", "SCIENCE_BUILDING", 250, 4, "Science & Tech Corridor"),

            # Library (central hub) connections
            ("LIBRARY", "ADMINISTRATION", 210, 3, "Centennial Plaza"),
            ("LIBRARY", "CAFETERIA", 200, 3, "East Plaza Path"),
            ("LIBRARY", "SCIENCE_BUILDING", 290, 4, "Scholars Walk"),

            # Science Building connections
            ("SCIENCE_BUILDING", "CAFETERIA", 200, 3, "Research Link"),

            # Cafeteria connections
            ("CAFETERIA", "DORMITORY", 240, 4, "Lakeside Boardwalk"),
            ("CAFETERIA", "ADMINISTRATION", 280, 4, "Garden Avenue"),

            # Dormitory connections
            ("DORMITORY", "ADMINISTRATION", 260, 4, "South Quad Walk"),
        ]

        for u, v, dist, cost, name in walkways_data:
            self.add_walkway(u, v, dist, cost, name)

    def add_location(self, location: Location):
        """Add a location node to the campus graph."""
        self.locations[location.id] = location
        if location.id not in self.adjacency:
            self.adjacency[location.id] = []

    def add_walkway(self, u: str, v: str, distance_m: int, cost: int, name: str):
        """Add a bidirectional walkway between two locations."""
        if u not in self.locations or v not in self.locations:
            raise ValueError(f"Both endpoints must exist in campus locations: {u}, {v}")

        edge = Walkway(u=u, v=v, distance_m=distance_m, cost=cost, name=name, is_open=True)
        key_fwd = (u, v)
        key_rev = (v, u)

        self.edges[key_fwd] = edge
        self.edges[key_rev] = edge

        self.adjacency[u].append(edge)
        self.adjacency[v].append(edge)

    def get_location(self, loc_id: str) -> Optional[Location]:
        """Retrieve location object by ID."""
        return self.locations.get(loc_id)

    def get_all_locations(self) -> List[Location]:
        """Return list of all campus locations."""
        return list(self.locations.values())

    def get_location_names(self) -> Dict[str, str]:
        """Return mapping of ID -> readable Name."""
        return {loc.id: loc.name for loc in self.locations.values()}

    def get_neighbors(self, loc_id: str, include_closed: bool = False) -> List[Tuple[str, Walkway]]:
        """
        Get all neighboring locations and the connecting walkway.
        If include_closed is False (default), closed walkways are excluded.
        """
        neighbors = []
        if loc_id not in self.adjacency:
            return neighbors

        for edge in self.adjacency[loc_id]:
            if not include_closed and not edge.is_open:
                continue
            other_id = edge.v if edge.u == loc_id else edge.u
            neighbors.append((other_id, edge))

        return neighbors

    def get_edge(self, u: str, v: str) -> Optional[Walkway]:
        """Get the walkway connecting u and v, if it exists."""
        return self.edges.get((u, v))

    def get_all_unique_edges(self) -> List[Walkway]:
        """Return list of unique walkways (without bidirectional duplication)."""
        seen = set()
        unique = []
        for (u, v), edge in self.edges.items():
            canonical = tuple(sorted([u, v]))
            if canonical not in seen:
                seen.add(canonical)
                unique.append(edge)
        return unique

    def close_walkway(self, u: str, v: str) -> bool:
        """Temporarily close a walkway between u and v."""
        edge = self.get_edge(u, v)
        if edge:
            edge.is_open = False
            return True
        return False

    def reopen_walkway(self, u: str, v: str) -> bool:
        """Reopen a previously closed walkway."""
        edge = self.get_edge(u, v)
        if edge:
            edge.is_open = True
            return True
        return False

    def toggle_walkway(self, u: str, v: str) -> bool:
        """Toggle the open/closed status of a walkway."""
        edge = self.get_edge(u, v)
        if edge:
            edge.is_open = not edge.is_open
            return edge.is_open
        return False

    def reset_all_closures(self):
        """Reopen all closed walkways on campus."""
        for edge in self.edges.values():
            edge.is_open = True

    def get_closed_walkways(self) -> List[Walkway]:
        """Return list of currently closed walkways."""
        return [w for w in self.get_all_unique_edges() if not w.is_open]

    def straight_line_distance_m(self, u_id: str, v_id: str) -> float:
        """
        Calculate Euclidean straight-line distance in meters.
        """

        loc_u = self.locations.get(u_id)
        loc_v = self.locations.get(v_id)

        if not loc_u or not loc_v:
            return 0.0

        dx = (loc_u.x - loc_v.x) * self.CAMPUS_SCALE_METERS
        dy = (loc_u.y - loc_v.y) * self.CAMPUS_SCALE_METERS

        return math.hypot(dx, dy)