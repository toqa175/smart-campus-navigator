# Smart Campus Navigator 🧭🎓

**Course:** Fundamentals of AI (CF321) – Project 1: Search Algorithms  
**University:** Innovation University  
**Faculty:** Faculty of Computers and Information Technology  
**Instructor Requirements:** Search Algorithms Project Specification (Week 9 Delivery)  

---

## 1. Project Overview

**Smart Campus Navigator** is an interactive university desktop navigation system built with **Python 3** and **Pygame**. The application represents a modern university campus as a weighted, undirected graph, where vertices represent campus landmarks and buildings, and edges represent pedestrian walkways with physical walking distances and travel costs.

Using a custom, from-scratch implementation of the **A* Search algorithm**, students and campus visitors can:
1. Select any starting location and destination.
2. Calculate and visualize the mathematically optimal, minimum-cost walking path.
3. Inspect search metrics including physical distance in meters, effort cost ratings, runtime duration in milliseconds, and the exact count and sequence of explored nodes.
4. Compare the optimal A* path against realistic alternative routes.
5. Simulate walkway maintenance or construction road closures with instant real-time traffic rerouting.
6. Seamlessly switch between **Light Mode** (default) and **Dark Mode** without losing state or re-computing routes.

---

## 2. Core Problem Formulation (AI Formulation)

In accordance with the official CF321 Fundamentals of AI rubric:

| AI Problem Component | Campus Navigation Definition |
| :--- | :--- |
| **States ($S$)** | The discrete campus buildings and landmarks: `Main Gate`, `Computer Science Building`, `Student Center`, `Sports Complex`, `Engineering Building`, `Library`, `Administration`, `Science Building`, `Cafeteria`, `Dormitory`. |
| **Initial State ($s_0$)** | The starting building selected by the user (default: `Main Gate`). |
| **Goal State ($G$)** | The target destination building selected by the user (default: `Library`). |
| **Available Actions ($A(s)$)** | Traverse any open, unobstructed pedestrian walkway connected to the current building. |
| **Transition Model ($Result(s, a)$)** | Arrive at the adjacent building connected by the walkway. |
| **Step Cost ($c(s, a, s')$)** | Physical walkway length in meters ($m$) or effort rating units. |
| **Path Cost ($g(n)$)** | Sum of individual walkway costs along the sequence from start to node $n$. |

---

## 3. How the A* Algorithm Works

A* is an **informed (heuristic) search algorithm** that evaluates nodes by combining the cost to reach the node $g(n)$ with the estimated cost to reach the goal $h(n)$:

$$f(n) = g(n) + h(n)$$

### Breakdown of Terms:
* **$g(n)$ (Actual Cost):**  
  The exact cumulative cost (physical meters or effort rating) incurred along the path from the starting state $s_0$ to node $n$. As the agent moves forward, $g(n)$ is tracked accurately via parent pointers and recorded edge lengths.
* **$h(n)$ (Heuristic Cost):**  
  The estimated remaining cost to travel from node $n$ to the goal destination $G$. To guarantee that A* finds the **optimal** (minimum-cost) solution, $h(n)$ must be **admissible** and **consistent**.
* **$f(n)$ (Total Estimated Cost):**  
  The estimated total cost of the cheapest complete solution passing through node $n$. The priority queue (`heapq`) orders nodes strictly by increasing $f(n)$ values.

### Heuristic Choice & Mathematical Admissibility Proof
In this project, the primary heuristic is the **straight-line Euclidean distance**:

$$h(n) = \sqrt{(\Delta x \cdot \text{scale})^2 + (\Delta y \cdot \text{scale})^2}$$

* **Why Euclidean Distance?**  
  In a physical 2D Euclidean plane, a straight line represents the absolute shortest continuous distance between any two coordinates. A pedestrian walkway can curve, turn around flowerbeds, or skirt lakes, but it can **never** be shorter than the straight-line air distance connecting its endpoints.
* **Admissibility ($h(n) \le h^*(n)$):**  
  By calibrating the coordinate space (`CAMPUS_SCALE_METERS = 680.0`), straight-line distance is guaranteed to be $\le$ the true shortest path distance for every single pair of nodes in the graph ($0 \le h(n) \le h^*(n)$).
* **Consistency / Monotonicity ($h(u) \le c(u, v) + h(v)$):**  
  Because Euclidean distance satisfies the triangle inequality in Euclidean space, the heuristic is also consistent (monotone). Consequently, when A* expands a node, the path to that node is guaranteed to be optimal; no closed node ever needs to be reopened.
* **Educational Comparison Modes:**  
  The application also implements:
  - **Zero Heuristic ($h(n) = 0$):** Transforms A* into Dijkstra's Algorithm (Uniform-Cost Search), demonstrating how heuristic guidance reduces explored nodes while maintaining identical optimal costs.
  - **Effort Cost Metric Heuristic:** Scaled cost heuristic evaluating effort rather than pure physical distance.

---

## 4. Implemented Features

### A. Core Requirements
- [x] **Weighted Campus Graph:** 10 realistic university buildings with bidirectional walkways, calibrated distances, and effort ratings.
- [x] **Custom A* Implementation:** Pure Python standard library implementation (`heapq`, `math`, `time`) without external black-box graph or pathfinding libraries.
- [x] **Decoupled Architecture:** Algorithm logic is isolated from GUI rendering and tested independently via automated unit tests.
- [x] **Interactive Route Planner:** Dropdown controls with color-coded start (Green) and destination (Red) pins, instant "Find Route", and "Reset" features.
- [x] **Illustrated Campus Map:** Custom vector rendering of buildings with department-specific 3D architectural roofs, badges, lawns, trees, running track, lake with ripples, central fountain, and compass rose.
- [x] **Route Visualization:** Bold Royal Blue highlighted optimal route, directional nodes, and route statistics.
- [x] **Route Results Panel:** Displays starting location, destination, physical distance ($m$), total cost score, number of explored nodes, execution time in milliseconds, and an ordered step-by-step path sequence.
- [x] **Graceful Boundary Handling:** Handled identical start/destination gracefully ($0\text{ m}$, 1 node) and clear notifications when destinations are unreachable due to severed paths.

### B. Creative Bonus Features
- [x] **Alternative Route Comparison:** Automatically identifies and visualizes a realistic secondary detour route, reporting distance, cost, and percentage difference alongside the primary A* route.
- [x] **Simulate Road Closures:** Dropdown and button controls allow closing any walkway on campus (e.g. maintenance or construction). The active graph disables the edge, draws a high-contrast Red "X" badge on the map, and immediately recalculates the rerouted A* path.
- [x] **Road Reopening:** Reopen individual walkways or use "Reopen All" to restore full campus access.
- [x] **Session Query History:** Automatically tracks recent searches with route endpoints, distance, cost, timestamps, and status badges. Clicking any history entry instantly restores and displays that route.
- [x] **Light Mode & Dark Mode:** Centralized WCAG-compliant color palettes with instant, lossless toggle via header button or hotkey `T`. Preserves active search, selected nodes, closed walkways, and zoom level.
- [x] **Map Controls & Zoom:** Toggle building labels, toggle walkways, and zoom in/out (`+` / `-`).

---

## 5. Technology Stack & Installation

### Requirements
* Python 3.9 or higher
* Pygame 2.5.0 or higher
* Python Standard Library (`heapq`, `math`, `time`, `typing`, `dataclasses`, `unittest`)

### Installation Steps

1. **Clone the repository or navigate to project directory:**
   ```bash
   cd smart-campus-navigator
   ```

2. **(Optional) Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

---

## 6. How to Run the Application

Launch the desktop interface by executing:

```bash
python main.py
```

### Keyboard Shortcuts
| Key | Action |
| :--- | :--- |
| `Enter` or `Space` | Calculate Route (A* Search) |
| `R` | Reset Route Planner |
| `T` | Toggle Light / Dark Mode |
| `+` or `=` | Zoom In Map |
| `-` | Zoom Out Map |
| `Esc` | Close any open dropdown menu |

---

## 7. Automated Testing & Validation

The project includes an exhaustive unit test suite in `tests.py` verifying mathematical correctness, admissibility, and edge cases.

### Run the Tests:
```bash
python tests.py -v
```

### Verified Test Cases:
1. `test_01_graph_structure`: Verifies 10 campus landmarks and bidirectional walkway symmetry.
2. `test_02_straightforward_route`: Verifies direct adjacent route calculation.
3. `test_03_multi_step_optimal_path`: Verifies multi-step path selection against Dijkstra ground truth.
4. `test_04_admissibility_all_pairs`: Exhaustively validates that $h(u, v) \le h^*(u, v)$ for all $\binom{10}{2} = 45$ location pairs in the graph.
5. `test_05_consistency_triangle_inequality`: Verifies monotonicity $h(u, G) \le c(u, v) + h(v, G)$ across all edges and goals.
6. `test_06_heuristic_efficiency`: Proves A* expands fewer or equal nodes compared to Dijkstra (Uniform-Cost Search).
7. `test_07_start_equals_goal`: Verifies zero-distance, single-node path when start equals destination.
8. `test_08_disconnected_destination`: Verifies graceful failure (`found=False`, empty path) when all walkways to destination are severed.
9. `test_09_road_closure_and_rerouting`: Verifies dynamic detour calculation when primary walkway is blocked.
10. `test_10_road_reopening`: Verifies path restoration upon reopening closed roads.
11. `test_11_alternative_routes`: Validates that the alternative route is distinct, valid, and has cost $\ge$ optimal path.

**Test Run Output:**
```
Ran 11 tests in 0.010s

OK
```

---

## 8. Campus Locations & Walkway Topology

```
             [Sports Complex] -------- [Engineering Building] -------- [Science Building]
                    |                          |                              |
                    |                          |                              |
             [Student Center] ----------- [Library] -------------------- [Cafeteria]
                    |                     (Center Hub)                        |
                    |                          |                              |
          [CS Building] -------------- [Administration] -------------- [Dormitory]
                    \                          |                             /
                     \                         |                            /
                      \------------------ [Main Gate] ---------------------/
```

### Building IDs and Roles:
1. `MAIN_GATE`: Primary campus south entrance.
2. `CS_BUILDING`: Faculty of Computers and Information Technology.
3. `STUDENT_CENTER`: Social hub, student activities, and lounges.
4. `SPORTS_COMPLEX`: Olympic running track, stadium field, and gymnasium.
5. `ENGINEERING`: Engineering laboratories and technical workshops.
6. `LIBRARY`: Central academic rotunda, research archives, and study halls.
7. `ADMINISTRATION`: Dean's office, registrar, and student affairs.
8. `SCIENCE_BUILDING`: Physics, Chemistry, and Biological research labs.
9. `CAFETERIA`: Campus food court, cafes, and lakeside dining.
10. `DORMITORY`: Student residential housing and campus dormitories.

---

## 9. Known Limitations

1. **2D Surface Assumption:** Walkway slope and multi-story building interior elevators/stairs are not explicitly modeled; elevation differences are abstracted into the walkway effort cost metric.
2. **Static Obstacles:** Walkway closures are managed per whole segment rather than time-variable pedestrian congestion curves.
3. **Screen Resolution:** The interface is optimized for desktop displays of $1440 \times 920$ resolution. Scaling below $1024 \times 768$ may compress certain panel elements.

---

## 10. Student Presentation & Defense Summary

When presenting this project:
1. **Explain the Priority Queue:** Detail how `heapq` retrieves the node with the lowest $f(n)$ in $O(\log |V|)$ time.
2. **Defend the Heuristic:** Explain that straight-line distance is the physical Euclidean lower bound ($h \le h^*$), guaranteeing optimality without overestimating remaining distance.
3. **Demonstrate Road Closures:** Close `Library <-> Cafeteria` (as shown in the reference design) or `Main Gate <-> Administration` and show how A* automatically finds the detour through `Computer Science Building`.
4. **Demonstrate Efficiency:** Switch algorithm mode to `Dijkstra (Zero Heuristic)` and demonstrate that while the final path cost is identical, A* evaluates significantly fewer nodes.
