// App State
const API_BASE = 'http://127.0.0.1:5000'; // Define backend URL
const state = {
    servers: [],
    intervals: {} // Store intervals for cleanup if needed
};

// DOM Elements
const container = document.getElementById('dashboard-container');

// Initial Load
document.addEventListener('DOMContentLoaded', () => {
    loadConfig(); // Load UI immediately
    setInterval(updateStatus, 5000); // Start polling
});

async function loadConfig() {
    try {
        const response = await fetch(`${API_BASE}/api/config`);
        const servers = await response.json();

        // Initialize state with "unknown" status
        state.servers = servers.map(s => ({ ...s, status: 'unknown' }));
        renderServers();

        // Trigger first status update immediately
        updateStatus();
    } catch (error) {
        console.error('Error loading config:', error);
        container.innerHTML = '<div style="color:red; text-align:center">Error loading configuration. Check backend.</div>';
    }
}

async function updateStatus() {
    try {
        const response = await fetch(`${API_BASE}/api/servers`);
        const servers = await response.json();

        // Update state and UI
        state.servers = servers;
        updateServers(servers);

        // Fetch stats/screenshots for running servers
        servers.forEach(server => {
            if (server.status === 'running') {
                fetchStats(server.id);
                updateScreenshot(server.id, server.name);
            }
        });
    } catch (error) {
        console.error('Error updating status:', error);
    }
}

function renderServers() {
    container.innerHTML = '';
    state.servers.forEach(server => {
        const card = document.createElement('div');
        card.className = 'server-card';
        card.id = `card-${server.id}`;

        card.innerHTML = `
            <div class="card-header">
                <div class="server-info">
                    <h2>${server.display_name}</h2>
                    <div class="server-ip">${server.ip}</div>
                </div>
                <span class="status-badge status-${server.status}" id="status-${server.id}">
                    ${server.status}
                </span>
            </div>

            <div class="live-view-container">
                <div class="live-view-header">Live Preview</div>
                <img id="live-img-${server.id}" src="" alt="Server Screen" class="live-view-img"
                    onclick="openFullscreen('${server.id}', '${server.name}')" title="Click for Full Screen">
            </div>

            <div class="controls">
                <button class="btn btn-start" onclick="startServer('${server.name}')" 
                    ${server.status === 'running' ? 'disabled' : ''} id="btn-start-${server.id}">
                    <i class="fas fa-play"></i> Start
                </button>
                <button class="btn btn-restart" onclick="restartServer('${server.name}')"
                    ${server.status !== 'running' ? 'disabled' : ''} id="btn-restart-${server.id}">
                    <i class="fas fa-undo"></i> Restart
                </button>
                <button class="btn btn-stop" onclick="stopServer('${server.name}')"
                    ${server.status !== 'running' ? 'disabled' : ''} id="btn-stop-${server.id}">
                    <i class="fas fa-stop"></i> Stop
                </button>
            </div>

            <div class="stats-grid">
                <div class="stat-item">
                    <div class="stat-value" id="cpu-${server.id}">0%</div>
                    <div class="stat-label">CPU</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value" id="ram-${server.id}">0%</div>
                    <div class="stat-label">RAM</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value" id="disk-${server.id}">0%</div>
                    <div class="stat-label">DISK</div>
                </div>
            </div>

            <div class="console-section">
                <!-- Direct Hardware Input -->
                <div class="command-input-group">
                    <input type="text" class="cmd-input" placeholder="Type to inject keyboard..." 
                        id="input-${server.id}" onkeypress="handleEnter(event, '${server.id}', '${server.name}')">
                    
                    <button class="btn btn-send" onclick="sendCommand('${server.id}', '${server.name}')" title="Inject Keystrokes">
                        <i class="fas fa-keyboard"></i> Type
                    </button>
                    <button class="btn btn-ssh" onclick="sendSSHCommand('${server.id}')" title="Execute via SSH">
                        <i class="fas fa-terminal"></i> SSH
                    </button>
                </div>
                <div id="ssh-output-${server.id}" class="ssh-output hidden"></div>
            </div>
        `;
        container.appendChild(card);
    });
}

function updateServers(servers) {
    servers.forEach(server => {
        // Update Status Badge
        const statusBadge = document.getElementById(`status-${server.id}`);
        if (statusBadge) {
            statusBadge.className = `status-badge status-${server.status}`;
            statusBadge.textContent = server.status;
        }

        // Update Buttons
        const btnStart = document.getElementById(`btn-start-${server.id}`);
        const btnRestart = document.getElementById(`btn-restart-${server.id}`);
        const btnStop = document.getElementById(`btn-stop-${server.id}`);

        if (btnStart && btnStop && btnRestart) {
            if (server.status === 'running') {
                btnStart.disabled = true;
                btnRestart.disabled = false;
                btnStop.disabled = false;
            } else {
                btnStart.disabled = false;
                btnRestart.disabled = true;
                btnStop.disabled = true;
                // Reset stats if stopped
                updateStatsUI(server.id, { cpu: 0, ram: 0, disk: 0 });
            }
        }
    });
}

async function startServer(name) {
    try {
        await fetch(`${API_BASE}/api/server/${name}/start`, { method: 'POST' });
        // Immediate status check
        setTimeout(fetchServers, 1000);
    } catch (error) {
        console.error('Error starting server:', error);
    }
}

async function stopServer(name) {
    try {
        await fetch(`${API_BASE}/api/server/${name}/stop`, { method: 'POST' });
        // Immediate status check
        setTimeout(fetchServers, 1000);
    } catch (error) {
        console.error('Error stopping server:', error);
    }
}

async function restartServer(name) {
    if (!confirm("Are you sure you want to restart this server? Unsaved data may be lost.")) return;
    try {
        await fetch(`${API_BASE}/api/server/${name}/restart`, { method: 'POST' });
        // Immediate status check
        setTimeout(fetchServers, 1000);
    } catch (error) {
        console.error('Error restarting server:', error);
    }
}

function updateScreenshot(id, name) {
    const img = document.getElementById(`live-img-${id}`);
    if (img) {
        // Add timestamp to prevent caching
        const timestamp = new Date().getTime();
        // Use a background loader or just let it update
        // We can check if image loads successfully
        const newSrc = `${API_BASE}/api/server/${name}/screenshot?t=${timestamp}`;

        // Optional: Preload to avoid flickering
        const loader = new Image();
        loader.onload = () => {
            if (img) img.src = newSrc;
        };
        loader.src = newSrc;
    }
}

async function fetchStats(id) {
    try {
        const response = await fetch(`${API_BASE}/api/server/${id}/stats`);
        const stats = await response.json();
        updateStatsUI(id, stats);
    } catch (error) {
        console.error('Error fetching stats:', error);
    }
}

function updateStatsUI(id, stats) {
    if (stats.error) return; // Don't update if error (or maybe show error)

    document.getElementById(`cpu-${id}`).textContent = `${stats.cpu.toFixed(1)}%`;
    document.getElementById(`ram-${id}`).textContent = `${stats.ram.toFixed(1)}%`;
    document.getElementById(`disk-${id}`).textContent = `${stats.disk.toFixed(1)}%`;
}



// Unified command handler using Keyboard Injection
async function sendCommand(id, name) {
    const input = document.getElementById(`input-${id}`);
    const command = input.value;

    if (!command && command !== "") return;

    input.value = ''; // Clear immediately

    try {
        console.log(`Typing to ${name}: ${command}`);
        // Use TYPE endpoint for keyboard injection
        await fetch(`${API_BASE}/api/server/${name}/type`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: command })
        });

        // Force refresh screenshot immediately to see result
        setTimeout(() => updateScreenshot(id, name), 500);
        setTimeout(() => updateScreenshot(id, name), 1500);
    } catch (error) {
        console.error("Type error", error);
    }
}

// SSH Command Handler
async function sendSSHCommand(id) {
    const input = document.getElementById(`input-${id}`);
    const command = input.value;
    const outputDiv = document.getElementById(`ssh-output-${id}`);

    if (!command) return;

    // Don't clear input immediately for SSH in case they want to edit
    // input.value = ''; 

    try {
        outputDiv.textContent = "Executing SSH...";
        outputDiv.classList.remove('hidden');

        const response = await fetch(`${API_BASE}/api/server/${id}/ssh_exec`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ command })
        });

        const data = await response.json();
        outputDiv.textContent = data.output || "[No Output]";

        // Auto hide removed as per user request
        // setTimeout(() => { ... }, 8000);

    } catch (error) {
        outputDiv.textContent = "Error executing SSH command";
        console.error(error);
    }
}

// Poll for console output
setInterval(updateConsoles, 1000);

async function updateConsoles() {
    state.servers.forEach(async (server) => {
        if (server.status !== 'running') return;

        try {
            const response = await fetch(`${API_BASE}/api/server/${server.id}/console/output`);
            const data = await response.json();

            if (data.output) {
                const consoleOut = document.getElementById(`console-${server.id}`);
                if (consoleOut) {
                    // Simple cleaning
                    const safeOutput = data.output.replace(/</g, '&lt;').replace(/>/g, '&gt;');
                    consoleOut.innerHTML += safeOutput;
                    consoleOut.scrollTop = consoleOut.scrollHeight;
                }
            }
        } catch (e) {
            // silent fail
        }
    });
}



function handleEnter(event, id, name) {
    if (event.key === 'Enter') {
        sendCommand(id, name);
    }
}

// Full Screen Logic
let fullScreenInterval = null;
let currentFullscreenServerId = null;
let currentFullscreenServerName = null;

function openFullscreen(id, name) {
    const overlay = document.getElementById('fullscreen-overlay');
    const fsImg = document.getElementById('fullscreen-img');
    const label = document.getElementById('fullscreen-label');
    const input = document.getElementById('fullscreen-input');

    // Store current context
    currentFullscreenServerId = id;
    currentFullscreenServerName = name;

    // Clear previous source
    fsImg.src = '';
    // Clear input
    if (input) input.value = '';

    // Set initial content
    label.textContent = name;
    fsImg.src = `${API_BASE}/api/server/${name}/screenshot?t=${new Date().getTime()}`;

    // Show overlay
    overlay.classList.add('active');

    // Focus input automatically
    if (input) setTimeout(() => input.focus(), 100);

    // Start "Live" loop using recursive timeout to avoid stacking if loading is slow
    const updateLoop = () => {
        if (!overlay.classList.contains('active')) return;

        const timestamp = new Date().getTime();
        const newSrc = `${API_BASE}/api/server/${name}/screenshot?t=${timestamp}`;

        const loader = new Image();
        loader.onload = () => {
            if (overlay.classList.contains('active')) {
                fsImg.src = newSrc;
                // Schedule next update only after load is complete (approx 200ms delay for "live" feel)
                fullScreenInterval = setTimeout(updateLoop, 200);
            }
        };
        loader.onerror = () => {
            // Retry even on error but slightly slower
            if (overlay.classList.contains('active')) {
                fullScreenInterval = setTimeout(updateLoop, 500);
            }
        };
        loader.src = newSrc;
    };

    // Start the loop
    if (fullScreenInterval) clearTimeout(fullScreenInterval); // Clear any existing
    updateLoop();
}

function closeFullscreen() {
    const overlay = document.getElementById('fullscreen-overlay');
    overlay.classList.remove('active');

    currentFullscreenServerId = null;
    currentFullscreenServerName = null;

    if (fullScreenInterval) {
        clearTimeout(fullScreenInterval); // Changed to clearTimeout
        fullScreenInterval = null;
    }
}

// Fullscreen Command Handlers
async function sendFullscreenCommand() {
    if (!currentFullscreenServerId || !currentFullscreenServerName) return;

    const input = document.getElementById('fullscreen-input');
    const command = input.value;

    if (!command && command !== "") return;

    input.value = ''; // Clear immediately

    try {
        console.log(`Typing to ${currentFullscreenServerName} (FS): ${command}`);
        await fetch(`${API_BASE}/api/server/${currentFullscreenServerName}/type`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: command })
        });

        // Force refresh is handled by the interval basically, but we can try to force one
        // Note: The loop runs every second.
    } catch (error) {
        console.error("Type error", error);
    }
}

async function sendFullscreenSSHCommand() {
    if (!currentFullscreenServerId) return;

    const input = document.getElementById('fullscreen-input');
    const command = input.value;

    if (!command) return;

    // UI Feedback (maybe toast? for now using alert as it works in fullscreen)
    // Better: Helper text in sidebar?
    const helpText = document.querySelector('.sidebar-help p');
    const originalText = helpText.innerHTML;

    try {
        helpText.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Executing SSH...';

        const response = await fetch(`${API_BASE}/api/server/${currentFullscreenServerId}/ssh_exec`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ command })
        });

        const data = await response.json();

        // Output to embedded div instead of alert
        const fsOutput = document.getElementById('fullscreen-ssh-output');
        if (fsOutput) {
            fsOutput.textContent = data.output || "[No Output]";
            fsOutput.classList.remove('hidden');
            fsOutput.scrollTop = fsOutput.scrollHeight;
        }

        helpText.innerHTML = originalText;
    } catch (error) {
        console.error("SSH Error", error);
        helpText.innerHTML = originalText;

        const fsOutput = document.getElementById('fullscreen-ssh-output');
        if (fsOutput) {
            fsOutput.textContent = "Error executing SSH command";
            fsOutput.classList.remove('hidden');
        }
    }
}

function handleFullscreenEnter(event) {
    if (event.key === 'Enter') {
        sendFullscreenCommand();
    }
}

// Close on escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeFullscreen();
});
