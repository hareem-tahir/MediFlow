# MediFlow – AI-Based Emergency Medical Resource Allocation and Simulation

MediFlow is an educational AI project that simulates emergency medical resource allocation in a fictional city. It integrates five classical Artificial Intelligence algorithms into an interactive Streamlit dashboard to demonstrate intelligent routing, resource allocation, and strategic decision-making.

The simulation operates on a fictional city consisting of **12 locations, 18 roads, 3 hospitals, 5 ambulances, and 5 active emergencies**.

> **Educational Simulation Only**
>
> MediFlow is developed for academic and learning purposes. It is not a real-world emergency dispatch, medical diagnosis, or clinical decision-support system. The city map represents a fictional environment and does not correspond to actual geographic locations.

## Features

- **Interactive City Visualization:** Explore a fictional city with roads, intersections, hospitals, ambulances, and emergencies.
- **Emergency Dispatch Simulation:** Visualize ambulance movement along calculated routes, including alternative routes and dispatch status.
- **Intelligent Route Planning:** Compare A* and Dijkstra search algorithms through step-by-step visualizations.
- **Constraint-Based Resource Allocation:** Assign ambulances and hospitals to emergencies while checking equipment, availability, capacity, and reachability.
- **Strategic Decision-Making:** Compare Minimax and Alpha-Beta Pruning through interactive decision trees.
- **Scenario Customization:** Simulate traffic congestion, road closures, hospital capacity changes, ambulance shortages, and mass-casualty situations.
- **Performance Evaluation:** Review algorithm benchmarks, allocation statistics, route metrics, and automated test results.
- **Interactive Reports:** Explore visual analytics and export evaluation data as CSV files.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python 3.10+ | Core application and algorithms |
| Streamlit | Interactive dashboard |
| Pandas | Data handling and analysis |
| Plotly | Charts and data visualization |
| HTML, CSS, JavaScript, SVG | Interactive city maps and algorithm playback |
| Pytest | Automated testing |

No paid APIs, external services, or API keys are required.

## AI Algorithms Implemented

### 1. Dijkstra's Algorithm

Dijkstra's algorithm calculates optimal paths by repeatedly expanding the unvisited node with the lowest accumulated travel cost.

It provides optimal routes without relying on heuristic information.

### 2. A* Search Algorithm

A* extends Dijkstra's approach by combining the accumulated path cost with a heuristic estimate of the remaining distance:

`f(n) = g(n) + h(n)`

Where:
- `g(n)` represents the cost from the starting location to the current node.
- `h(n)` estimates the remaining cost to the destination.

MediFlow uses straight-line distance multiplied by 3 minutes per unit as its heuristic. Since road costs are never lower than their corresponding straight-line travel times, the heuristic is admissible.

Both routing algorithms report the selected route, travel cost, average execution time over 100 runs, and explored nodes.

### 3. Constraint Satisfaction Problem (CSP)

The CSP module assigns ambulances and hospitals to active emergencies while satisfying resource constraints.

**Variables:** Open emergencies.

**Domains:** Valid ambulance-hospital combinations.

**Constraints include:**
- Ambulances must be available.
- Ambulances must carry the required equipment.
- Hospitals must provide the required medical service.
- Hospitals must have available beds.
- Ambulances and hospitals must be reachable.
- Each ambulance can serve only one emergency per allocation plan.
- Hospital admissions cannot exceed available capacity.

**Search techniques:**
- Backtracking
- Minimum Remaining Values (MRV)
- Forward Checking

Emergencies are prioritized by severity. When an assignment cannot satisfy the constraints, the application reports the failure and its explanation.

### 4. Minimax Algorithm

Minimax evaluates dispatch decisions under modeled adversarial conditions.

- **MAX:** The dispatcher selects the next emergency to serve.
- **MIN:** An adversary selects the worst modeled operating condition.

The adversary can introduce:
- Heavy traffic, increasing response time by 1.5×.
- Hospital overload, reducing available capacity by one bed.
- Ambulance failure, removing the most capable available ambulance.

The utility function considers patient severity, response time, unserved emergencies, and hospital capacity.

The algorithm selects the dispatch plan with the highest worst-case utility.

### 5. Alpha-Beta Pruning

Alpha-Beta Pruning optimizes Minimax by eliminating branches that cannot influence the final decision.

MediFlow visualizes:
- Explored decision-tree branches.
- Selected decisions.
- Adversarial responses.
- Pruned branches.
- Evaluated node counts.
- Pruning statistics.

The implementation and tests compare Alpha-Beta results against Minimax to verify that both return the same selected action and utility.

## Dashboard Pages

MediFlow provides eight interactive dashboard pages.

| Page | Functionality |
|---|---|
| Overview Dashboard | KPI cards, emergency alerts, decision pipeline, city map, hospital capacity, ambulance status, and activity feed |
| Emergency Management | Register, edit, resolve, delete, and filter emergencies |
| Live Simulation Map | Animated ambulance dispatch, route playback, mission timelines, and event logs |
| Route Analysis | Side-by-side A* and Dijkstra comparisons, search trees, explored nodes, and route metrics |
| Resource Allocation | CSP statistics, allocation results, Sankey diagrams, capacity tables, and failure explanations |
| Strategic Planning | Minimax and Alpha-Beta comparisons, decision trees, alternative plans, and node counts |
| Scenario Controls | Scenario presets, road closures, traffic adjustments, hospital capacity, and ambulance availability |
| Evaluation and Reports | Automated tests, algorithm benchmarks, performance tables, and CSV exports |

### Interactive City Map

The city visualization includes:
- Roads, intersections, buildings, parks, and harbour.
- Closed roads with visual barriers.
- Congested roads with traffic multipliers.
- Hospitals with available-bed indicators.
- Severity-based emergency markers.
- Ambulance locations and operational status.

### Dispatch Simulation

Press **Run Dispatch** or use the animated simulation page to observe ambulance movement along calculated A* routes.

Route styles distinguish:
- Solid lines: Ambulance travelling to the emergency.
- Dashed lines: Patient transportation to the hospital.
- Dotted grey lines: Alternative routes.

The dashboard also provides ambulance fleet cards, dispatch status, mission timelines, and activity logs.

Manual dispatch allows selection of an ambulance, emergency, and hospital with live constraint validation.

## Project Structure

```text
MediFlow/
│
├── app.py
├── requirements.txt
│
├── .streamlit/
│   └── config.toml
│
├── mediflow/
│   ├── data.py
│   ├── routing.py
│   ├── csp.py
│   ├── strategy.py
│   ├── planner.py
│   ├── cityview.py
│   ├── city_assets.py
│   └── visuals.py
│
└── tests/
    ├── algorithm tests
    ├── edge-case tests
    ├── integration tests
    ├── visualization tests
    └── GUI page-load tests
```

### Core Modules

| Module | Responsibility |
|---|---|
| `data.py` | Fictional city, locations, and default scenario |
| `routing.py` | Dijkstra, A*, and travel-time calculations |
| `csp.py` | Constraint satisfaction, backtracking, MRV, and forward checking |
| `strategy.py` | Minimax and Alpha-Beta Pruning |
| `planner.py` | Integration of routing, allocation, and strategic planning |
| `cityview.py` | SVG city map, dispatch playback, search visualization, and decision trees |
| `city_assets.py` | CSS and JavaScript for interactive visualizations |
| `visuals.py` | Plotly charts, including Sankey and Gantt visualizations |

## Installation and Setup

### Prerequisites

- Python 3.10 or later
- pip
- Git (optional, for cloning the repository)

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR-USERNAME/MediFlow.git
cd MediFlow
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Launch the Application

```bash
streamlit run app.py
```

Streamlit will provide a local URL to open the dashboard in your browser.

### 4. Run Automated Tests

```bash
python -m pytest tests -q
```

## Reproducible Simulation Scenarios

All scenarios can be tested using the dashboard. Start each scenario by selecting **Reset to Default Scenario**.

### Scenario 1: Baseline

- Open Resource Allocation.
- Verify that all five emergencies receive assignments.
- Open Live Simulation Map and start playback.
- Open Route Analysis and inspect the Harbor → North Med route.

### Scenario 2: District Isolation

Close the following roads under Scenario Controls:

- Old Town ↔ Riverside
- North Park ↔ Riverside
- Riverside ↔ City General

Expected result: INC-1 (Riverside) becomes unreachable, and the application explains the allocation failure.

### Scenario 3: Equipment Shortage

Disable AMB-2 and AMB-4.

Expected results:
- INC-1 (ICU) cannot be assigned because no suitable ICU ambulance is available.
- INC-3 and INC-5 both require AMB-3.
- The higher-severity INC-5 receives priority, while INC-3 is reported as a constraint conflict.

### Scenario 4: Additional Emergencies

Register a sixth emergency with severity level 1.

Expected result: The new emergency cannot be assigned because only five ambulances are available.

### Scenario 5: Strategic Planning

- Open Strategic Planning.
- Set the search depth to 3.
- Run Minimax and Alpha-Beta.
- Open Evaluation and Reports.
- Run the depth benchmark to compare node counts at depths 1–4.

## Testing and Evaluation

The project includes automated tests covering:

- Core AI algorithms.
- Routing and allocation edge cases.
- Integration between planning modules.
- Visualization data.
- Streamlit GUI page loading and interactions.

The Evaluation and Reports page also provides access to the automated test suite, route comparisons, allocation benchmarks, and CSV exports.

## Assumptions and Simulation Model

- Travel time is calculated as straight-line distance × 3 minutes per unit × traffic multiplier.
- Traffic multipliers range from 1.0 to 5.0.
- Ambulances begin at fixed locations.
- Each ambulance serves one emergency per allocation plan.
- Hospital availability is calculated as total beds minus occupied beds.
- The Minimax search uses a configurable depth limit, with a default of 3 and a maximum of 4.
- Utility weights and adversarial conditions are educational modeling choices, not medical evidence.

## Limitations

- **Small simulation environment:** The city contains only 12 locations and 18 roads. Execution-time measurements can be dominated by Python overhead, so A* is not necessarily faster than Dijkstra in milliseconds.
- **CSP prioritization:** Allocation uses severity-based prioritization and does not sacrifice a higher-priority emergency to serve multiple lower-priority emergencies.
- **No ambulance return cycle:** Ambulances do not automatically become available again after completing a trip.
- **Minimax complexity:** Search complexity increases rapidly with depth, so the interface limits the maximum depth to 4.
- **Visualization behavior:** Interactive visuals use `streamlit.components.v1.html` with inline SVG and JavaScript. Changing a control reruns the page and resets playback.
- **Browser testing:** GUI functionality and animation data are tested, but the visual layout has not been fully validated across real browsers and mobile devices.
- **No live integrations:** The application does not use real traffic, geographic data, hospital systems, emergency services, or medical information.

## Screenshots

Screenshots can be added to a `screenshots/` directory to demonstrate the dashboard.

Suggested captures:

| Filename | Recommended View |
|---|---|
| `01_overview.png` | Overview Dashboard |
| `02_map.png` | Live Simulation Map during dispatch |
| `03_routes.png` | A* and Dijkstra comparison |
| `04_csp_success.png` | Successful resource allocation |
| `05_csp_failure.png` | Resource allocation under equipment shortage |
| `06_strategy.png` | Minimax and Alpha-Beta decision trees |
| `07_controls.png` | Scenario Controls |
| `08_tests.png` | Automated test results |

## Learning Outcomes

MediFlow demonstrates how multiple classical AI techniques can work together in a single application.

The project explores:

- Informed and uninformed search.
- Heuristic pathfinding.
- Constraint satisfaction and backtracking.
- Adversarial search and optimization.
- Resource allocation under constraints.
- Algorithm evaluation and visualization.
- Integration of AI algorithms into an interactive Python application.

## License

No license has been specified yet. All rights and usage permissions remain subject to the repository owner's decision.