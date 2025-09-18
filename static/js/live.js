// Live WebSocket Manager for Fun Thursday
class LiveWebSocketManager {
    constructor() {
        this.leaderboardWs = null;
        this.boardWs = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
        this.imageCache = new Map(); // Cache for loaded images
        this.updateTimeout = null; // For debouncing updates
    }

    // Initialize WebSocket connections
    init() {
        this.connectLeaderboard();
        this.connectBoard();
    }

    // Load image with caching to prevent unnecessary refetching
    loadImageWithCache(imgElement, src) {
        if (!imgElement || !src) return;
        
        // Check if image is already cached and loaded
        if (this.imageCache.has(src)) {
            imgElement.src = src;
            return;
        }
        
        // Only update if src is different
        if (imgElement.src !== src) {
            imgElement.src = src;
            // Cache the image URL
            this.imageCache.set(src, true);
        }
    }

    // Preload images to improve performance
    preloadImage(src) {
        if (!src || this.imageCache.has(src)) return;
        
        const img = new Image();
        img.onload = () => {
            this.imageCache.set(src, true);
        };
        img.src = src;
    }

    // Debounced update to prevent too frequent updates
    debouncedUpdate(callback, delay = 100) {
        if (this.updateTimeout) {
            clearTimeout(this.updateTimeout);
        }
        this.updateTimeout = setTimeout(callback, delay);
    }

    // Connect to leaderboard WebSocket
    connectLeaderboard() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/leaderboard`;
        
        try {
            this.leaderboardWs = new WebSocket(wsUrl);
            
            this.leaderboardWs.onopen = () => {
                console.log('Leaderboard WebSocket connected');
                this.reconnectAttempts = 0;
            };
            
            this.leaderboardWs.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    if (data.type === 'leaderboard_update') {
                        this.updateLeaderboard(data.data.leaderboard);
                    }
                } catch (e) {
                    console.error('Error parsing leaderboard data:', e);
                }
            };
            
            this.leaderboardWs.onclose = () => {
                console.log('Leaderboard WebSocket disconnected');
                this.reconnectLeaderboard();
            };
            
            this.leaderboardWs.onerror = (error) => {
                console.error('Leaderboard WebSocket error:', error);
            };
        } catch (error) {
            console.error('Error connecting to leaderboard WebSocket:', error);
        }
    }

    // Connect to board WebSocket
    connectBoard() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/board`;
        
        try {
            this.boardWs = new WebSocket(wsUrl);
            
            this.boardWs.onopen = () => {
                console.log('Board WebSocket connected');
                this.reconnectAttempts = 0;
            };
            
            this.boardWs.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    if (data.type === 'board_update') {
                        this.updateBoard(data.data);
                    }
                } catch (e) {
                    console.error('Error parsing board data:', e);
                }
            };
            
            this.boardWs.onclose = () => {
                console.log('Board WebSocket disconnected');
                this.reconnectBoard();
            };
            
            this.boardWs.onerror = (error) => {
                console.error('Board WebSocket error:', error);
            };
        } catch (error) {
            console.error('Error connecting to board WebSocket:', error);
        }
    }

    // Reconnect leaderboard WebSocket
    reconnectLeaderboard() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`Attempting to reconnect leaderboard WebSocket (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
            setTimeout(() => {
                this.connectLeaderboard();
            }, this.reconnectDelay * this.reconnectAttempts);
        }
    }

    // Reconnect board WebSocket
    reconnectBoard() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`Attempting to reconnect board WebSocket (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
            setTimeout(() => {
                this.connectBoard();
            }, this.reconnectDelay * this.reconnectAttempts);
        }
    }

    // Update leaderboard display
    updateLeaderboard(leaderboard) {
        // Use debounced update to prevent too frequent updates
        this.debouncedUpdate(() => {
            this._doUpdateLeaderboard(leaderboard);
        });
    }

    // Actual leaderboard update logic
    _doUpdateLeaderboard(leaderboard) {
        const tbody = document.getElementById('leaderboard');
        if (!tbody) return;

        // Store leaderboard data in localStorage
        this.saveLeaderboardToStorage(leaderboard);

        if (leaderboard.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="4" class="text-center">
                        <div class="alert alert-info">No players yet</div>
                    </td>
                </tr>
            `;
            this.updateTop3([]);
            this.updateUserProgress(null, 0);
            return;
        }

        // Preload images for better performance
        leaderboard.slice(0, 3).forEach(player => {
            if (player.profile_photo) {
                this.preloadImage(player.profile_photo);
            }
        });

        // Update top 3 section
        this.updateTop3(leaderboard.slice(0, 3));

        // Update user progress
        const currentUser = window.getCurrentUser();
        const userRank = leaderboard.findIndex(player => player.username === currentUser?.username) + 1;
        this.updateUserProgress(userRank, leaderboard.length);

        // Update full leaderboard table (excluding top 3) - granular updates only
        this.updateLeaderboardTable(leaderboard.slice(3));
    }

    // Save leaderboard data to localStorage
    saveLeaderboardToStorage(leaderboard) {
        try {
            localStorage.setItem('funthursday_leaderboard', JSON.stringify({
                data: leaderboard,
                timestamp: Date.now()
            }));
        } catch (error) {
            console.warn('Could not save leaderboard to localStorage:', error);
        }
    }

    // Load leaderboard data from localStorage
    loadLeaderboardFromStorage() {
        try {
            const stored = localStorage.getItem('funthursday_leaderboard');
            if (stored) {
                const parsed = JSON.parse(stored);
                // Use data if it's less than 5 minutes old
                if (Date.now() - parsed.timestamp < 300000) {
                    return parsed.data;
                }
            }
        } catch (error) {
            console.warn('Could not load leaderboard from localStorage:', error);
        }
        return null;
    }

    // Update leaderboard table with granular updates
    updateLeaderboardTable(remainingPlayers) {
        const tbody = document.getElementById('leaderboard');
        if (!tbody) return;

        if (remainingPlayers.length === 0) {
            tbody.innerHTML = `<tr></tr>`;
            return;
        }

        // Get existing rows
        const existingRows = Array.from(tbody.querySelectorAll('tr'));
        const existingData = new Map();
        
        // Build map of existing data
        existingRows.forEach(row => {
            const cells = row.querySelectorAll('td');
            if (cells.length >= 4) {
                const name = cells[2].textContent;
                const points = cells[3].querySelector('.points-badge')?.textContent || '0';
                existingData.set(name, {
                    row: row,
                    rank: cells[0].textContent,
                    points: points
                });
            }
        });

        // Check if we need to rebuild the table (structure change)
        const needsRebuild = this.needsTableRebuild(remainingPlayers, existingData);
        
        if (needsRebuild) {
            // Rebuild entire table
            tbody.innerHTML = remainingPlayers.map(player => `
                <tr data-username="${player.username}">
                    <td class="rank-column">${player.rank}</td>
                    <td class="photo-column">
                        <img src="" alt="${player.real_name}" class="player-photo-small" data-src="${player.profile_photo}">
                    </td>
                    <td>${player.real_name}</td>
                    <td class="points-column">
                        <span class="points-badge">${player.points}</span>
                    </td>
                </tr>
            `).join('');
            
            // Apply image caching to all leaderboard images
            const leaderboardImages = tbody.querySelectorAll('.player-photo-small[data-src]');
            leaderboardImages.forEach(img => {
                const src = img.getAttribute('data-src');
                this.loadImageWithCache(img, src);
            });
        } else {
            // Update existing rows granularly
            remainingPlayers.forEach(player => {
                const existingRow = tbody.querySelector(`tr[data-username="${player.username}"]`);
                if (existingRow) {
                    // Update only rank and points
                    const cells = existingRow.querySelectorAll('td');
                    if (cells.length >= 4) {
                        cells[0].textContent = player.rank;
                        const pointsBadge = cells[3].querySelector('.points-badge');
                        if (pointsBadge) {
                            pointsBadge.textContent = player.points;
                        }
                    }
                } else {
                    // Add new player row
                    const newRow = document.createElement('tr');
                    newRow.setAttribute('data-username', player.username);
                    newRow.innerHTML = `
                        <td class="rank-column">${player.rank}</td>
                        <td class="photo-column">
                            <img src="" alt="${player.real_name}" class="player-photo-small" data-src="${player.profile_photo}">
                        </td>
                        <td>${player.real_name}</td>
                        <td class="points-column">
                            <span class="points-badge">${player.points}</span>
                        </td>
                    `;
                    tbody.appendChild(newRow);
                    
                    // Apply image caching to new image
                    const img = newRow.querySelector('.player-photo-small[data-src]');
                    if (img) {
                        const src = img.getAttribute('data-src');
                        this.loadImageWithCache(img, src);
                    }
                }
            });

            // Remove players that are no longer in the list
            const currentUsernames = new Set(remainingPlayers.map(p => p.username));
            const rowsToRemove = Array.from(tbody.querySelectorAll('tr[data-username]'))
                .filter(row => !currentUsernames.has(row.getAttribute('data-username')));
            
            rowsToRemove.forEach(row => row.remove());
        }
    }

    // Check if table needs to be rebuilt
    needsTableRebuild(remainingPlayers, existingData) {
        // Check if number of players changed significantly
        if (Math.abs(remainingPlayers.length - existingData.size) > 2) {
            return true;
        }

        // Check if any player names changed (indicating new players)
        const existingNames = new Set(existingData.keys());
        const newNames = new Set(remainingPlayers.map(p => p.real_name));
        
        // If more than 1 new player, rebuild
        const newPlayerCount = Array.from(newNames).filter(name => !existingNames.has(name)).length;
        return newPlayerCount > 1;
    }

    // Update top 3 cards
    updateTop3(top3) {
        const cards = document.querySelectorAll('.top3-card');
        cards.forEach((card, index) => {
            if (top3[index]) {
                const player = top3[index];
                const photo = card.querySelector('.player-photo');
                const name = card.querySelector('.player-name');
                const pointsValue = card.querySelector('.points-value span');
                
                // Use cached image loading to prevent unnecessary refetching
                this.loadImageWithCache(photo, player.profile_photo);
                if (name) name.textContent = player.real_name;
                if (pointsValue) pointsValue.textContent = player.points.toLocaleString();
            } else {
                const name = card.querySelector('.player-name');
                const pointsValue = card.querySelector('.points-value span');
                
                if (name) name.textContent = 'No Player';
                if (pointsValue) pointsValue.textContent = '0';
            }
        });
    }

    // Update user progress bar
    updateUserProgress(userRank, totalUsers) {
        const userPointsEl = document.getElementById('userPoints');
        const userRankEl = document.getElementById('userRank');
        const totalUsersEl = document.getElementById('totalUsers');
        const progressFillEl = document.getElementById('progressFill');

        if (userPointsEl) {
            const currentUser = window.getCurrentUser();
            userPointsEl.textContent = currentUser?.points || 0;
        }

        if (userRankEl) {
            userRankEl.textContent = userRank || '-';
        }

        if (totalUsersEl) {
            totalUsersEl.textContent = totalUsers;
        }

        if (progressFillEl && userRank && totalUsers > 0) {
            const progress = ((totalUsers - userRank + 1) / totalUsers) * 100;
            progressFillEl.style.width = `${Math.max(progress, 5)}%`;
        }
    }

    // Update board display
    updateBoard(data) {
        // Update current number
        const currentElement = document.getElementById('current');
        if (currentElement) {
            const span = currentElement.querySelector('span');
            if (span) {
                span.textContent = data.current_number || '-';
            }
        }

        // Update history
        const historyElement = document.getElementById('history');
        if (historyElement) {
            if (data.drawn_numbers && data.drawn_numbers.length > 0) {
                historyElement.innerHTML = data.drawn_numbers.map(num => 
                    `<span class="number-badge">${num}</span>`
                ).join('');
            } else {
                historyElement.innerHTML = '<div class="alert alert-info">No numbers drawn yet</div>';
            }
        }
    }

    // Load leaderboard data
    async loadLeaderboard() {
        try {
            // Try to load from localStorage first
            const cachedData = this.loadLeaderboardFromStorage();
            if (cachedData) {
                console.log('Loading leaderboard from cache');
                this.updateLeaderboard(cachedData);
            }

            // Always fetch fresh data from server
            const response = await fetch('/api/leaderboard');
            const data = await response.json();
            this.updateLeaderboard(data.leaderboard);
        } catch (error) {
            console.error('Error loading leaderboard:', error);
            // Fallback to cached data if available
            const cachedData = this.loadLeaderboardFromStorage();
            if (cachedData) {
                console.log('Using cached leaderboard data due to error');
                this.updateLeaderboard(cachedData);
            }
        }
    }

    // Load board data
    async loadBoard() {
        try {
            const response = await fetch('/api/board');
            const data = await response.json();
            this.updateBoard(data);
        } catch (error) {
            console.error('Error loading board:', error);
        }
    }

    // Close all connections
    close() {
        if (this.leaderboardWs) {
            this.leaderboardWs.close();
        }
        if (this.boardWs) {
            this.boardWs.close();
        }
    }
}

// Global live manager instance
window.liveManager = new LiveWebSocketManager();

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Check if user is authenticated
    if (window.isAuthenticated && window.isAuthenticated()) {
        // Initialize WebSocket connections
        window.liveManager.init();
        
        // Load initial data
        window.liveManager.loadLeaderboard();
        window.liveManager.loadBoard();
        
        // Auto-load users list if on admin page
        if (window.location.pathname === '/admin' && typeof loadUsers === 'function') {
            loadUsers();
        }
        
        // Set up periodic refresh as backup (less frequent)
        setInterval(() => {
            window.liveManager.loadLeaderboard();
            window.liveManager.loadBoard();
        }, 30000); // Reduced from 5s to 30s
    }
});

// Tab switching functions
function showLeaderboard() {
    document.getElementById('leaderboardTab').classList.remove('hidden');
    document.getElementById('boardTab').classList.add('hidden');
    
    // Update active tab button
    document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
    document.querySelector('.tab-button[onclick="showLeaderboard()"]').classList.add('active');
}

function showBoard() {
    document.getElementById('boardTab').classList.remove('hidden');
    document.getElementById('leaderboardTab').classList.add('hidden');
    
    // Update active tab button
    document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
    document.querySelector('.tab-button[onclick="showBoard()"]').classList.add('active');
}

// Admin functions
async function loadUsers() {
    try {
        const response = await fetch('/api/users');
        const data = await response.json();
        updateUsersTable(data.users);
    } catch (error) {
        console.error('Error loading users:', error);
        document.getElementById('userManagementResult').innerHTML = 
            '<div class="alert alert-danger">Error loading users</div>';
    }
}

function updateUsersTable(users) {
    const table = document.getElementById('usersTable');
    if (!table) return;

    if (users.length === 0) {
        table.innerHTML = '<div class="alert alert-info">No users found</div>';
        return;
    }

    table.innerHTML = `
        <table class="table">
            <thead>
                <tr>
                    <th>Photo</th>
                    <th>Name</th>
                    <th>Username</th>
                    <th>Gender</th>
                    <th>Points</th>
                    <th>Role</th>
                    <th>Status</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                ${users.map(user => `
                    <tr class="${user.is_deleted ? 'deleted-user' : ''}">
                        <td><img src="" alt="${user.real_name}" class="player-photo-small" data-src="${user.profile_photo}"></td>
                        <td>${user.real_name}</td>
                        <td>${user.username}</td>
                        <td>
                            <span class="badge badge-${user.gender === 'female' ? 'warning' : 'info'}">
                                ${user.gender === 'female' ? '👩 Female' : '👨 Male'}
                            </span>
                        </td>
                        <td>${user.points}</td>
                        <td><span class="badge badge-${user.role === 'admin' ? 'danger' : 'primary'}">${user.role}</span></td>
                        <td>
                            <span class="badge badge-${user.is_deleted ? 'warning' : 'success'}">
                                ${user.is_deleted ? 'Deleted' : 'Active'}
                            </span>
                        </td>
                        <td>
                            ${user.is_deleted ? 
                                `<button onclick="restoreUser(${user.user_id})" class="btn btn-success btn-sm">Restore</button>` :
                                `<button onclick="deleteUser(${user.user_id})" class="btn btn-danger btn-sm">Delete</button>`
                            }
                        </td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
    
    // Apply image caching to all admin table images
    const adminImages = table.querySelectorAll('.player-photo-small[data-src]');
    adminImages.forEach(img => {
        const src = img.getAttribute('data-src');
        window.liveManager.loadImageWithCache(img, src);
    });
}

async function deleteUser(userId) {
    if (!confirm('Are you sure you want to delete this user? This will hide them from the leaderboard but they can be restored.')) return;

    try {
        const response = await fetch(`/api/delete-user/${userId}`, {
            method: 'DELETE'
        });
        const data = await response.json();
        
        if (response.ok) {
            document.getElementById('userManagementResult').innerHTML = 
                `<div class="alert alert-success">${data.message}</div>`;
            loadUsers();
        } else {
            document.getElementById('userManagementResult').innerHTML = 
                `<div class="alert alert-danger">${data.detail}</div>`;
        }
    } catch (error) {
        console.error('Error deleting user:', error);
        document.getElementById('userManagementResult').innerHTML = 
            '<div class="alert alert-danger">Error deleting user</div>';
    }
}

async function restoreUser(userId) {
    if (!confirm('Are you sure you want to restore this user?')) return;

    try {
        const response = await fetch(`/api/restore-user/${userId}`, {
            method: 'POST'
        });
        const data = await response.json();
        
        if (response.ok) {
            document.getElementById('userManagementResult').innerHTML = 
                `<div class="alert alert-success">${data.message}</div>`;
            loadUsers();
        } else {
            document.getElementById('userManagementResult').innerHTML = 
                `<div class="alert alert-danger">${data.detail}</div>`;
        }
    } catch (error) {
        console.error('Error restoring user:', error);
        document.getElementById('userManagementResult').innerHTML = 
            '<div class="alert alert-danger">Error restoring user</div>';
    }
}

async function refreshAll() {
    if (window.liveManager) {
        await window.liveManager.loadLeaderboard();
        await window.liveManager.loadBoard();
    }
    if (typeof loadUsers === 'function') {
        await loadUsers();
    }
}

async function refreshAvatars() {
    if (!confirm('Are you sure you want to refresh all user avatars? This will update all users with new gender-based avatars.')) return;
    
    try {
        const response = await fetch('/api/refresh-avatars', {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            document.getElementById('userManagementResult').innerHTML = 
                `<div class="alert alert-success">${data.message}</div>`;
            // Refresh the page to show updated avatars
            setTimeout(() => {
                window.location.reload();
            }, 2000);
        } else {
            document.getElementById('userManagementResult').innerHTML = 
                `<div class="alert alert-danger">${data.detail || 'Error refreshing avatars'}</div>`;
        }
    } catch (error) {
        console.error('Error refreshing avatars:', error);
        document.getElementById('userManagementResult').innerHTML = 
            '<div class="alert alert-danger">Error refreshing avatars</div>';
    }
}

async function clearAllNumbers() {
    if (!confirm('Are you sure you want to clear all drawn numbers? This action cannot be undone.')) return;

    try {
        const response = await fetch('/api/clear-numbers', {
            method: 'DELETE'
        });
        const data = await response.json();
        
        if (response.ok) {
            document.getElementById('drawResult').innerHTML = 
                `<div class="alert alert-success">${data.message || 'All numbers cleared successfully!'}</div>`;
        } else {
            document.getElementById('drawResult').innerHTML = 
                `<div class="alert alert-danger">${data.detail || 'Error clearing numbers'}</div>`;
        }
    } catch (error) {
        console.error('Error clearing numbers:', error);
        document.getElementById('drawResult').innerHTML = 
            '<div class="alert alert-danger">Error clearing numbers</div>';
    }
}

// Form handlers
document.addEventListener('DOMContentLoaded', function() {
    // Points form
    const pointsForm = document.getElementById('pointsForm');
    if (pointsForm) {
        pointsForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const formData = new FormData(pointsForm);
            const userId = formData.get('user_select');
            const points = formData.get('points');

            try {
                const response = await fetch('/api/update-points', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        user_id: parseInt(userId),
                        points: parseInt(points)
                    })
                });
                const data = await response.json();
                
                if (response.ok) {
                    document.getElementById('pointsResult').innerHTML = 
                        `<div class="alert alert-success">${data.message || 'Points updated successfully!'}</div>`;
                    pointsForm.reset();
                    // Auto-refresh users list
                    loadUsers();
                } else {
                    document.getElementById('pointsResult').innerHTML = 
                        `<div class="alert alert-danger">${data.detail || 'Error updating points'}</div>`;
                }
            } catch (error) {
                console.error('Error updating points:', error);
                document.getElementById('pointsResult').innerHTML = 
                    '<div class="alert alert-danger">Error updating points</div>';
            }
        });
    }

    // Draw number form
    const drawForm = document.getElementById('drawForm');
    if (drawForm) {
        drawForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const formData = new FormData(drawForm);
            const number = formData.get('number');

            try {
                const response = await fetch('/api/draw-number', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        number: parseInt(number)
                    })
                });
                const data = await response.json();
                
                if (response.ok) {
                    document.getElementById('drawResult').innerHTML = 
                        `<div class="alert alert-success">${data.message || 'Number drawn successfully!'}</div>`;
                    drawForm.reset();
                } else {
                    document.getElementById('drawResult').innerHTML = 
                        `<div class="alert alert-danger">${data.detail || 'Error drawing number'}</div>`;
                }
            } catch (error) {
                console.error('Error drawing number:', error);
                document.getElementById('drawResult').innerHTML = 
                    '<div class="alert alert-danger">Error drawing number</div>';
            }
        });
    }

    // Load users dropdown
    loadUsersForDropdown();
});

async function loadUsersForDropdown() {
    try {
        const response = await fetch('/api/users/non-admin');
        const data = await response.json();
        const select = document.getElementById('user_select');
        if (select) {
            select.innerHTML = '<option value="">Select a player</option>' +
                data.users.map(user => 
                    `<option value="${user.user_id}">${user.real_name} (${user.username})</option>`
                ).join('');
        }
    } catch (error) {
        console.error('Error loading users for dropdown:', error);
    }
}
