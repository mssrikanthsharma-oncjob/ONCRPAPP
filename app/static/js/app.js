// Main Application Logic

class BookingApp {
    constructor() {
        this.currentTab = 'bookings';
        this.bookings = [];
        this.filteredBookings = [];
        this.sortColumn = null;
        this.sortDirection = 'asc';
        this.editingBooking = null;
        
        this.init();
    }

    async init() {
        try {
            // Load cached authentication data
            authService.loadCachedAuth();
            
            // Clear any invalid cached tokens first
            if (authService.token && !authService.user) {
                authService.clearAuth();
            }
            
            // Check authentication on page load
            const isAuth = await authService.isAuthenticated();
            if (isAuth) {
                const user = authService.getCurrentUser();
                if (user && user.role === 'customer') {
                    this.showCustomerPortal();
                } else {
                    this.showDashboard();
                }
            } else {
                // Ensure we show login by default
                this.showLogin();
            }
        } catch (error) {
            console.error('Authentication check failed:', error);
            // On error, clear auth and show login
            authService.clearAuth();
            this.showLogin();
        }

        this.setupEventListeners();
    }

    setupEventListeners() {
        // Login form
        const loginForm = document.getElementById('login-form');
        if (loginForm) {
            loginForm.addEventListener('submit', (e) => this.handleLogin(e));
        }

        // Logout button
        const logoutBtn = document.getElementById('logout-btn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', () => authService.logout());
        }

        // Tab navigation
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('nav-tab')) {
                this.switchTab(e.target.dataset.tab);
            }
        });
    }

    async handleLogin(e) {
        e.preventDefault();
        
        const username = FormValidator.sanitizeInput(document.getElementById('username').value);
        const password = document.getElementById('password').value;

        // Validate form
        const validation = FormValidator.validateLogin(username, password);
        if (!validation.isValid) {
            UIUtils.showError(validation.errors.join(', '));
            return;
        }

        UIUtils.hideError();
        UIUtils.setLoading('login-btn', true);

        try {
            const result = await authService.login(username, password);
            
            if (result.success) {
                UIUtils.showSuccess('Login successful! Redirecting...');
                setTimeout(() => {
                    const user = authService.getCurrentUser();
                    if (user && user.role === 'customer') {
                        this.showCustomerPortal();
                    } else {
                        this.showDashboard();
                    }
                }, 1000);
            } else {
                UIUtils.showError(result.error);
            }
        } catch (error) {
            UIUtils.showError('Login failed. Please try again.');
        } finally {
            UIUtils.setLoading('login-btn', false);
        }
    }

    showLogin() {
        // Ensure login container is visible and others are hidden
        const loginContainer = document.getElementById('login-container');
        const dashboard = document.getElementById('dashboard');
        const customerPortal = document.getElementById('customer-portal');
        
        if (loginContainer) loginContainer.style.display = 'flex';
        if (dashboard) dashboard.style.display = 'none';
        if (customerPortal) customerPortal.style.display = 'none';
        
        // Clear any error messages
        UIUtils.hideError();
        UIUtils.hideSuccess();
        
        // Focus on username field
        const usernameField = document.getElementById('username');
        if (usernameField) {
            setTimeout(() => usernameField.focus(), 100);
        }
    }

    showDashboard() {
        document.getElementById('login-container').style.display = 'none';
        document.getElementById('dashboard').style.display = 'block';
        document.getElementById('customer-portal').style.display = 'none';
        
        this.updateUserInfo();
        this.setupDashboardTabs();
        this.loadBookings();
    }

    showCustomerPortal() {
        document.getElementById('login-container').style.display = 'none';
        document.getElementById('dashboard').style.display = 'none';
        document.getElementById('customer-portal').style.display = 'block';
        
        // Load customer data after showing the portal
        if (window.customerPortal) {
            window.customerPortal.loadActivitySummary();
        }
    }

    updateUserInfo() {
        const user = authService.getCurrentUser();
        if (user) {
            document.getElementById('user-role').textContent = user.role.replace('_', ' ').toUpperCase();
        }
    }

    setupDashboardTabs() {
        const user = authService.getCurrentUser();
        
        // Show/hide tabs and features based on user role
        if (user && user.role === 'sales_person') {
            // Sales person has limited access
            this.applySalesPersonRestrictions();
        } else if (user && user.role === 'admin') {
            // Admin has full access
            this.applyAdminPermissions();
        }

        // Set default active tab
        this.switchTab('bookings');
    }

    applySalesPersonRestrictions() {
        // Hide analytics tab for sales persons
        const analyticsTab = document.querySelector('[data-tab="analytics"]');
        if (analyticsTab) {
            analyticsTab.style.display = 'none';
        }

        // Hide admin-only tabs
        const customersTab = document.querySelector('[data-tab="customers"]');
        const llmConfigTab = document.querySelector('[data-tab="llm-config"]');
        if (customersTab) customersTab.style.display = 'none';
        if (llmConfigTab) llmConfigTab.style.display = 'none';

        // Hide certain booking actions for sales persons
        this.restrictBookingActions();
        
        // Add visual indicator for limited access
        this.addRoleIndicator('Limited Access - Sales Person');
        
        // Add click handler to show permission denied message for hidden tabs
        this.addRestrictedTabHandlers();
    }

    applyAdminPermissions() {
        // Show all tabs for admin
        const analyticsTab = document.querySelector('[data-tab="analytics"]');
        const customersTab = document.querySelector('[data-tab="customers"]');
        const llmConfigTab = document.querySelector('[data-tab="llm-config"]');
        
        if (analyticsTab) analyticsTab.style.display = 'block';
        if (customersTab) customersTab.style.display = 'block';
        if (llmConfigTab) llmConfigTab.style.display = 'block';

        // Enable all booking actions for admin
        this.enableAllBookingActions();
        
        // Add visual indicator for full access
        this.addRoleIndicator('Full Access - Administrator');
    }

    addRestrictedTabHandlers() {
        // Add event listeners to show permission messages
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('nav-tab') && e.target.style.display === 'none') {
                e.preventDefault();
                UIUtils.showError('Access denied: This section requires administrator privileges.');
            }
        });
    }

    restrictBookingActions() {
        // Sales persons can view and edit bookings but have limited delete permissions
        // This will be implemented in the booking manager
        if (window.bookingManager) {
            window.bookingManager.setUserRole('sales_person');
        }
    }

    enableAllBookingActions() {
        // Admins have full permissions
        if (window.bookingManager) {
            window.bookingManager.setUserRole('admin');
        }
    }

    addRoleIndicator(message) {
        const userRole = document.getElementById('user-role');
        if (userRole) {
            userRole.title = message;
        }
    }

    switchTab(tabName) {
        // Check if user has permission to access this tab
        if (!this.canAccessTab(tabName)) {
            UIUtils.showError('You do not have permission to access this section.');
            return;
        }

        // Update tab buttons
        document.querySelectorAll('.nav-tab').forEach(tab => {
            tab.classList.remove('active');
        });
        
        const targetTab = document.querySelector(`[data-tab="${tabName}"]`);
        if (targetTab && targetTab.style.display !== 'none') {
            targetTab.classList.add('active');
        }

        // Update tab content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(`${tabName}-tab`).classList.add('active');

        this.currentTab = tabName;

        // Load tab-specific data
        if (tabName === 'bookings') {
            this.loadBookings();
        } else if (tabName === 'analytics') {
            this.loadAnalytics();
        } else if (tabName === 'customers') {
            // Load customer enquiries (handled by admin.js)
            if (window.adminPortal) {
                window.adminPortal.loadCustomerEnquiries();
                window.adminPortal.loadEnquiryStats();
            }
        } else if (tabName === 'llm-config') {
            // Load LLM configuration (handled by admin.js)
            if (window.adminPortal) {
                window.adminPortal.loadLLMConfig();
            }
        }
    }

    canAccessTab(tabName) {
        const user = authService.getCurrentUser();
        if (!user) return false;

        // Route guards based on user role
        if (tabName === 'analytics' || tabName === 'customers' || tabName === 'llm-config') {
            // Only admins can access analytics and admin features
            return user.role === 'admin';
        } else if (tabName === 'bookings') {
            // Both admins and sales persons can access bookings
            return user.role === 'admin' || user.role === 'sales_person';
        }

        return true; // Default allow
    }

    async loadBookings() {
        // Delegate to booking manager
        if (window.bookingManager) {
            await window.bookingManager.loadBookings();
        }
    }

    async loadAnalytics() {
        // Load analytics data using the analytics manager
        if (window.analyticsManager) {
            await window.analyticsManager.loadAnalytics();
        }
    }

    // Delegate booking operations to booking manager
    editBooking(id) {
        if (window.bookingManager) {
            window.bookingManager.editBooking(id);
        }
    }

    deleteBooking(id) {
        if (window.bookingManager) {
            window.bookingManager.confirmDeleteBooking(id);
        }
    }

    sortTable(column) {
        if (window.bookingManager) {
            window.bookingManager.sortTable(column);
        }
    }
}

// App initialization is handled in HTML template to control timing