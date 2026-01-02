// Authentication and JWT Token Management

class AuthService {
    constructor() {
        this.baseURL = '/api';
        this.token = localStorage.getItem('jwt_token');
        this.user = JSON.parse(localStorage.getItem('user') || 'null');
    }

    // Store JWT token and user info
    setAuth(token, user) {
        this.token = token;
        this.user = user;
        localStorage.setItem('jwt_token', token);
        localStorage.setItem('user', JSON.stringify(user));
    }

    // Clear authentication data
    clearAuth() {
        this.token = null;
        this.user = null;
        localStorage.removeItem('jwt_token');
        localStorage.removeItem('user');
    }

    // Check if user is authenticated
    async isAuthenticated() {
        if (!this.token || !this.user) {
            return false;
        }
        
        // For production, do a simple token existence check
        // Server-side verification happens on API calls
        return true;
    }

    // Get current user
    getCurrentUser() {
        return this.user;
    }

    // Get current token
    getToken() {
        return this.token;
    }

    // Get authorization headers
    getAuthHeaders() {
        return {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${this.token}`
        };
    }

    // Login with credentials
    async login(username, password) {
        try {
            const response = await fetch(`${this.baseURL}/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ username, password })
            });

            const result = await response.json();

            if (response.ok) {
                this.setAuth(result.token, result.user);
                return { success: true, user: result.user };
            } else {
                return { success: false, error: result.error || 'Login failed' };
            }
        } catch (error) {
            console.error('Login error:', error);
            return { success: false, error: 'Network error. Please try again.' };
        }
    }

    // Logout
    logout() {
        this.clearAuth();
        window.location.reload();
    }

    // Make authenticated API request
    async apiRequest(endpoint, options = {}) {
        const config = {
            headers: this.getAuthHeaders(),
            ...options
        };

        try {
            const response = await fetch(`${this.baseURL}${endpoint}`, config);
            
            if (response.status === 401) {
                // Token expired or invalid
                this.logout();
                return null;
            }

            return response;
        } catch (error) {
            console.error('API request error:', error);
            throw error;
        }
    }
}

// Form validation utilities
class FormValidator {
    static validateLogin(username, password) {
        const errors = [];

        if (!username || username.trim().length === 0) {
            errors.push('Username is required');
        }

        if (!password || password.length === 0) {
            errors.push('Password is required');
        }

        if (username && username.length < 3) {
            errors.push('Username must be at least 3 characters');
        }

        if (password && password.length < 6) {
            errors.push('Password must be at least 6 characters');
        }

        return {
            isValid: errors.length === 0,
            errors
        };
    }

    static sanitizeInput(input) {
        return input.trim().replace(/[<>]/g, '');
    }
}

// UI utilities
class UIUtils {
    static showError(message, containerId = 'error-message') {
        const errorDiv = document.getElementById(containerId);
        if (errorDiv) {
            errorDiv.textContent = message;
            errorDiv.style.display = 'block';
        }
    }

    static hideError(containerId = 'error-message') {
        const errorDiv = document.getElementById(containerId);
        if (errorDiv) {
            errorDiv.style.display = 'none';
        }
    }

    static showSuccess(message, containerId = 'success-message') {
        const successDiv = document.getElementById(containerId);
        if (successDiv) {
            successDiv.textContent = message;
            successDiv.style.display = 'block';
        }
    }

    static hideSuccess(containerId = 'success-message') {
        const successDiv = document.getElementById(containerId);
        if (successDiv) {
            successDiv.style.display = 'none';
        }
    }

    static setLoading(elementId, isLoading) {
        const element = document.getElementById(elementId);
        if (element) {
            if (isLoading) {
                element.classList.add('loading');
                if (element.tagName === 'BUTTON') {
                    element.disabled = true;
                    element.dataset.originalText = element.textContent;
                    element.textContent = 'Loading...';
                } else {
                    // For containers, add a loading overlay
                    if (!element.querySelector('.loading-overlay')) {
                        const overlay = document.createElement('div');
                        overlay.className = 'loading-overlay';
                        overlay.innerHTML = '<div class="loading-spinner"></div>';
                        element.style.position = 'relative';
                        element.appendChild(overlay);
                    }
                }
            } else {
                element.classList.remove('loading');
                if (element.tagName === 'BUTTON') {
                    element.disabled = false;
                    if (element.dataset.originalText) {
                        element.textContent = element.dataset.originalText;
                        delete element.dataset.originalText;
                    }
                } else {
                    // Remove loading overlay
                    const overlay = element.querySelector('.loading-overlay');
                    if (overlay) {
                        overlay.remove();
                    }
                }
            }
        }
    }

    static formatCurrency(amount) {
        return new Intl.NumberFormat('en-IN', {
            style: 'currency',
            currency: 'INR'
        }).format(amount);
    }

    static formatDate(dateString) {
        return new Date(dateString).toLocaleDateString('en-IN');
    }
}

// Initialize auth service globally
window.authService = new AuthService();