const ZONES = [
    "North Entry", "South Entry",
    "Concourse A", "Concourse B", "Concourse C",
    "Food Court 1", "Food Court 2",
    "Restrooms A", "Restrooms B",
    "Section 101", "Section 102", "Section 201", "Section 202"
];

// Initialize select dropdowns
function initSelects() {
    const startSelect = document.getElementById('start-node');
    const endSelect = document.getElementById('end-node');
    
    ZONES.forEach(zone => {
        const option1 = document.createElement('option');
        option1.value = zone;
        option1.textContent = zone;
        startSelect.appendChild(option1);
        
        const option2 = document.createElement('option');
        option2.value = zone;
        option2.textContent = zone;
        endSelect.appendChild(option2);
    });
    
    // Set default destinations
    endSelect.value = "Food Court 1";
}

// Fetch live data
async function fetchLiveData() {
    try {
        const [densityRes, waitTimesRes] = await Promise.all([
            fetch('/api/crowd-density'),
            fetch('/api/wait-times')
        ]);
        
        const densities = await densityRes.json();
        const waitTimes = await waitTimesRes.json();
        
        renderZones(densities, waitTimes);
    } catch (err) {
        console.error("Error fetching live data:", err);
    }
}

// Determine status color based on density
function getStatusClass(density) {
    if (density < 40) return 'status-green';
    if (density < 75) return 'status-yellow';
    return 'status-red';
}

function getStatusColor(density) {
    if (density < 40) return 'var(--status-green)';
    if (density < 75) return 'var(--status-yellow)';
    return 'var(--status-red)';
}

// Render zone cards
function renderZones(densities, waitTimes) {
    const container = document.getElementById('zones-container');
    
    // Render initially or update existing
    if (container.children.length === 0) {
        ZONES.forEach(zone => {
            const card = document.createElement('div');
            card.className = 'zone-card';
            card.id = `zone-${zone.replace(/\\s+/g, '-')}`;
            
            const density = densities[zone];
            const waitTime = waitTimes[zone];
            const statusClass = getStatusClass(density);
            
            card.innerHTML = `
                <div class="zone-header">
                    <div class="zone-name">${zone}</div>
                    <div class="status-indicator ${statusClass}"></div>
                </div>
                <div class="zone-stats">
                    <div class="stat-row">
                        <span>Crowd Density</span>
                        <span class="stat-value density-val">${density}%</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${density}%; background-color: ${getStatusColor(density)}"></div>
                    </div>
                    <div class="stat-row" style="margin-top: 0.5rem">
                        <span>Est. Wait Time</span>
                        <span class="stat-value wait-val">${waitTime} min</span>
                    </div>
                </div>
            `;
            container.appendChild(card);
        });
    } else {
        // Update existing to animate smoothly
        ZONES.forEach(zone => {
            const card = document.getElementById(`zone-${zone.replace(/\\s+/g, '-')}`);
            if(!card) return;
            
            const density = densities[zone];
            const waitTime = waitTimes[zone];
            const statusClass = getStatusClass(density);
            
            const indicator = card.querySelector('.status-indicator');
            indicator.className = `status-indicator ${statusClass}`;
            
            card.querySelector('.density-val').textContent = `${density}%`;
            card.querySelector('.wait-val').textContent = `${waitTime} min`;
            
            const fill = card.querySelector('.progress-fill');
            fill.style.width = `${density}%`;
            fill.style.backgroundColor = getStatusColor(density);
        });
    }
}

// Route fetching
document.getElementById('find-route-btn').addEventListener('click', async () => {
    const start = document.getElementById('start-node').value;
    const end = document.getElementById('end-node').value;
    
    if (start === end) {
        alert("Start and Destination cannot be the same.");
        return;
    }
    
    try {
        const res = await fetch(`/api/best-route?start=${encodeURIComponent(start)}&end=${encodeURIComponent(end)}`);
        const data = await res.json();
        
        if (res.ok) {
            document.getElementById('route-result').classList.remove('hidden');
            document.getElementById('route-time').textContent = data.estimated_time_minutes;
            
            const pathVisual = document.getElementById('route-path');
            pathVisual.innerHTML = '';
            
            data.path.forEach((node, index) => {
                const nodeEl = document.createElement('div');
                nodeEl.className = 'path-node';
                nodeEl.textContent = node;
                pathVisual.appendChild(nodeEl);
                
                if (index < data.path.length - 1) {
                    const arrow = document.createElement('div');
                    arrow.className = 'path-arrow';
                    arrow.innerHTML = '&#8594;';
                    pathVisual.appendChild(arrow);
                }
            });
        } else {
            alert(data.detail || "Error finding route.");
        }
    } catch (err) {
        console.error(err);
        alert("Error fetching route.");
    }
});

// Init
initSelects();
fetchLiveData();

// Poll every 5 seconds to simulate real-time updates
setInterval(fetchLiveData, 5000);
