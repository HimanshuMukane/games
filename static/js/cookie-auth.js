// Cookie-based Authentication Manager
class CookieAuthManager {
    constructor() {
        this.init();
    }

    init() {
        // Check if user is authenticated on page load
        this.checkAuthStatus();
    }

    // Get cookie value by name
    getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
        return null;
    }

    // Set cookie
    setCookie(name, value, days = 1) {
        const expires = new Date();
        expires.setTime(expires.getTime() + (days * 24 * 60 * 60 * 1000));
        document.cookie = `${name}=${value};expires=${expires.toUTCString()};path=/;SameSite=Lax`;
    }

    // Delete cookie
    deleteCookie(name) {
        document.cookie = `${name}=;expires=Thu, 01 Jan 1970 00:00:00 UTC;path=/;`;
    }

    // Check if user is authenticated
    isAuthenticated() {
        const username = this.getCookie('username');
        const userRole = this.getCookie('user_role');
        const sessionToken = this.getCookie('session_token');
        
        console.log('Auth check - username:', username, 'role:', userRole, 'token:', sessionToken ? 'present' : 'missing');
        
        return !!(username && userRole && sessionToken);
    }

    // Get current user info from cookies
    getCurrentUser() {
        if (!this.isAuthenticated()) {
            console.log('getCurrentUser: User not authenticated');
            return null;
        }
        
        const user = {
            username: this.getCookie('username'),
            role: this.getCookie('user_role'),
            real_name: this.getCookie('real_name') || this.getCookie('username')
        };
        
        console.log('getCurrentUser: Returning user:', user);
        return user;
    }

    // Check authentication and redirect if needed
    async checkAuthAndRedirect() {
        if (!this.isAuthenticated()) {
            window.location.href = '/login';
            return false;
        }
        return true;
    }

    // Logout user
    async logout() {
        try {
            // Call server logout endpoint to clear server-side cookies
            await fetch('/api/logout', {
                method: 'POST',
                credentials: 'include'
            });
        } catch (error) {
            console.error('Logout error:', error);
        }
        
        // Clear client-side cookies as backup
        this.deleteCookie('username');
        this.deleteCookie('user_role');
        this.deleteCookie('session_token');
        this.deleteCookie('real_name');
        
        // Redirect to login
        window.location.href = '/login';
    }

    // Check auth status and update UI
    checkAuthStatus() {
        const user = this.getCurrentUser();
        if (user) {
            // Update welcome message if element exists
            const welcomeMsg = document.getElementById('welcomeMsg');
            if (welcomeMsg) {
                const displayName = user.real_name || user.username || 'User';
                const role = user.role || 'user';
                welcomeMsg.textContent = `Welcome, ${displayName}! (${role})`;
            }
        } else {
            // If no user data, try to get from cookies directly
            const username = this.getCookie('username');
            const realName = this.getCookie('real_name');
            const role = this.getCookie('user_role');
            
            if (username) {
                const welcomeMsg = document.getElementById('welcomeMsg');
                if (welcomeMsg) {
                    const displayName = realName || username;
                    const userRole = role || 'user';
                    welcomeMsg.textContent = `Welcome, ${displayName}! (${userRole})`;
                }
            }
        }
    }

    // Get username for API calls
    getUsername() {
        return this.getCookie('username') || '';
    }

    // Check if user is admin
    isAdmin() {
        const user = this.getCurrentUser();
        return user && user.role === 'admin';
    }
}

// Global auth manager instance
window.cookieAuthManager = new CookieAuthManager();

// Ensure welcome message is set when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    window.cookieAuthManager.checkAuthStatus();
});

// Utility functions for easy access
window.getCurrentUser = () => {
    return window.cookieAuthManager.getCurrentUser();
};

window.logout = () => {
    window.cookieAuthManager.logout();
};

window.checkAuth = async () => {
    return await window.cookieAuthManager.checkAuthAndRedirect();
};

window.isAuthenticated = () => {
    return window.cookieAuthManager.isAuthenticated();
};

window.isAdmin = () => {
    return window.cookieAuthManager.isAdmin();
};

window.getUsername = () => {
    return window.cookieAuthManager.getUsername();
};
