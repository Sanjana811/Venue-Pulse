from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
import asyncio
import random
import heapq
import os

# ------------------------------------------------------------------
# APP INITIALIZATION
# ------------------------------------------------------------------
app = FastAPI(
    title="Venue Pulse API",
    description="Real-time crowd intelligence and routing for large-scale venues.",
    version="1.0.0",
)

# SECURITY: Restrict CORS in production, but open for hackathon demonstration.
# In a real environment, ALLOWED_ORIGINS would be loaded from env variables.
ALLOWED_ORIGINS = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET"], # SECURITY: Only allow GET methods to prevent unauthorized mutations
    allow_headers=["*"],
)

# ------------------------------------------------------------------
# MODELS (Input/Output Validation)
# ------------------------------------------------------------------
class RouteResponse(BaseModel):
    start: str = Field(..., description="The starting zone name")
    end: str = Field(..., description="The destination zone name")
    path: List[str] = Field(..., description="Ordered list of zones to traverse")
    estimated_time_minutes: float = Field(..., description="Total estimated travel time in minutes")

# ------------------------------------------------------------------
# IN-MEMORY STATE (Lightweight Data Management)
# ------------------------------------------------------------------
ZONES = [
    "North Entry", "South Entry",
    "Concourse A", "Concourse B", "Concourse C",
    "Food Court 1", "Food Court 2",
    "Restrooms A", "Restrooms B",
    "Section 101", "Section 102", "Section 201", "Section 202"
]

# Graph: Adjacency list mapping zone to its neighbors and base travel time (minutes)
GRAPH: Dict[str, Dict[str, float]] = {
    "North Entry": {"Concourse A": 2, "Concourse B": 3},
    "South Entry": {"Concourse B": 3, "Concourse C": 2},
    "Concourse A": {"North Entry": 2, "Food Court 1": 1, "Restrooms A": 1, "Section 101": 2, "Concourse B": 3},
    "Concourse B": {"North Entry": 3, "South Entry": 3, "Concourse A": 3, "Concourse C": 3, "Food Court 2": 2, "Section 102": 2, "Section 201": 2},
    "Concourse C": {"South Entry": 2, "Concourse B": 3, "Restrooms B": 1, "Section 202": 2},
    "Food Court 1": {"Concourse A": 1},
    "Food Court 2": {"Concourse B": 2},
    "Restrooms A": {"Concourse A": 1},
    "Restrooms B": {"Concourse C": 1},
    "Section 101": {"Concourse A": 2},
    "Section 102": {"Concourse B": 2},
    "Section 201": {"Concourse B": 2},
    "Section 202": {"Concourse C": 2},
}

# In-memory dictionary to hold live crowd density (percentage 0-100)
crowd_density: Dict[str, int] = {zone: random.randint(10, 50) for zone in ZONES}

# ------------------------------------------------------------------
# BACKGROUND WORKERS
# ------------------------------------------------------------------
async def simulate_crowds() -> None:
    """
    Simulates real-time crowd movement. 
    Adjusts the density of each zone slightly every 5 seconds.
    """
    while True:
        for zone in ZONES:
            # Simulate natural fluctuations in crowd size
            change = random.randint(-15, 15)
            new_density = crowd_density[zone] + change
            # Ensure density stays within realistic bounds (5% to 95%)
            crowd_density[zone] = max(5, min(95, new_density))
        await asyncio.sleep(5)

@app.on_event("startup")
async def startup_event() -> None:
    """Initialize background tasks on server startup."""
    asyncio.create_task(simulate_crowds())

# ------------------------------------------------------------------
# AI / LOGIC LAYER
# ------------------------------------------------------------------
def calculate_wait_time(density: int, zone_type: str) -> int:
    """
    Lightweight rule-based AI to estimate wait times.
    Avoids heavy ML models for efficiency and zero-cost cloud deployment.
    
    Args:
        density (int): Current crowd density percentage (0-100).
        zone_type (str): The name/type of the zone.
        
    Returns:
        int: Estimated wait time in minutes.
    """
    if "Food Court" in zone_type:
        base = density * 0.4
    elif "Restrooms" in zone_type:
        base = density * 0.15
    elif "Entry" in zone_type:
        base = density * 0.2
    else:
        # Concourses and sections represent transit flow, not static waiting lines
        base = density * 0.05
    return int(base)

# ------------------------------------------------------------------
# API ENDPOINTS
# ------------------------------------------------------------------
@app.get("/api/crowd-density", response_model=Dict[str, int])
async def get_crowd_density() -> Dict[str, int]:
    """Returns the current simulated crowd density (0-100%) for all zones."""
    return crowd_density

@app.get("/api/wait-times", response_model=Dict[str, int])
async def get_wait_times() -> Dict[str, int]:
    """Returns the predicted wait times in minutes for all zones."""
    wait_times = {zone: calculate_wait_time(density, zone) for zone, density in crowd_density.items()}
    return wait_times

@app.get("/api/best-route", response_model=RouteResponse)
async def get_best_route(
    start: str = Query(..., description="Starting location"), 
    end: str = Query(..., description="Destination location")
) -> RouteResponse:
    """
    Calculates the optimal path between two zones, dynamically adjusting
    for real-time crowd congestion using Dijkstra's algorithm.
    """
    # INPUT VALIDATION
    if start not in GRAPH or end not in GRAPH:
        raise HTTPException(status_code=400, detail="Invalid start or end zone provided.")
    if start == end:
        raise HTTPException(status_code=400, detail="Start and end zones must be different.")
    
    # DIJKSTRA'S ALGORITHM SETUP
    distances = {node: float('inf') for node in GRAPH}
    distances[start] = 0
    previous_nodes = {node: None for node in GRAPH}
    pq = [(0.0, start)]
    
    # PATHFINDING CORE
    while pq:
        current_distance, current_node = heapq.heappop(pq)
        
        # Early exit if we reached the destination
        if current_node == end:
            break
            
        if current_distance > distances[current_node]:
            continue
            
        for neighbor, base_dist in GRAPH[current_node].items():
            # Apply dynamic congestion penalty: weights scale from 1.0x to 3.0x 
            # depending on the real-time density of the target neighbor.
            density = crowd_density[neighbor]
            congestion_multiplier = 1.0 + (density / 100.0) * 2.0
            weighted_dist = base_dist * congestion_multiplier
            
            distance = current_distance + weighted_dist
            
            # Update path if a shorter route is found
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous_nodes[neighbor] = current_node # type: ignore
                heapq.heappush(pq, (distance, neighbor))
                
    # PATH RECONSTRUCTION
    path = []
    curr: Optional[str] = end
    while curr is not None:
        path.insert(0, curr)
        curr = previous_nodes[curr]
        
    if path[0] != start:
        raise HTTPException(status_code=404, detail="No route could be found between these zones.")
        
    return RouteResponse(
        start=start,
        end=end,
        path=path,
        estimated_time_minutes=round(distances[end], 1)
    )

# ------------------------------------------------------------------
# STATIC FILE SERVING
# ------------------------------------------------------------------
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(FRONTEND_DIR):
    # SERVING SECURELY: Disabling directory browsing
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
else:
    print(f"Warning: Frontend directory not found at {FRONTEND_DIR}. API only mode.")
