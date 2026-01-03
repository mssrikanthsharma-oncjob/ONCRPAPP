// Analytics Dashboard Implementation

class AnalyticsManager {
    constructor() {
        this.charts = {};
        this.currentFilters = {};
        this.dateRange = {
            start_date: null,
            end_date: null
        };
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.initializeDateFilters();
    }

    setupEventListeners() {
        // Filter controls
        const applyFilterBtn = document.getElementById('apply-filter-btn');
        if (applyFilterBtn) {
            applyFilterBtn.addEventListener('click', () => this.applyFilters());
        }

        // Export button
        const exportBtn = document.getElementById('export-btn');
        if (exportBtn) {
            exportBtn.addEventListener('click', () => this.exportData());
        }

        // Date inputs
        const dateFromInput = document.getElementById('date-from');
        const dateToInput = document.getElementById('date-to');
        
        if (dateFromInput) {
            dateFromInput.addEventListener('change', (e) => {
                this.dateRange.start_date = e.target.value;
            });
        }
        
        if (dateToInput) {
            dateToInput.addEventListener('change', (e) => {
                this.dateRange.end_date = e.target.value;
            });
        }
    }

    initializeDateFilters() {
        // Set default date range to last 30 days
        const today = new Date();
        const thirtyDaysAgo = new Date(today.getTime() - (30 * 24 * 60 * 60 * 1000));
        
        const dateFromInput = document.getElementById('date-from');
        const dateToInput = document.getElementById('date-to');
        
        if (dateFromInput) {
            dateFromInput.value = thirtyDaysAgo.toISOString().split('T')[0];
            this.dateRange.start_date = dateFromInput.value;
        }
        
        if (dateToInput) {
            dateToInput.value = today.toISOString().split('T')[0];
            this.dateRange.end_date = dateToInput.value;
        }
    }

    async loadAnalytics() {
        try {
            UIUtils.setLoading('analytics-tab', true);
            
            // Load dashboard data
            await this.loadDashboardData();
            
        } catch (error) {
            console.error('Error loading analytics:', error);
            UIUtils.showError('Failed to load analytics data');
        } finally {
            UIUtils.setLoading('analytics-tab', false);
        }
    }

    async loadDashboardData() {
        try {
            const params = new URLSearchParams();
            
            // Add date range
            if (this.dateRange.start_date) {
                params.append('start_date', this.dateRange.start_date + 'T00:00:00');
            }
            if (this.dateRange.end_date) {
                params.append('end_date', this.dateRange.end_date + 'T23:59:59');
            }
            
            // Add filters
            Object.keys(this.currentFilters).forEach(key => {
                if (this.currentFilters[key]) {
                    params.append(key, this.currentFilters[key]);
                }
            });

            const response = await authService.apiRequest(`/analytics/dashboard?${params.toString()}`);

            if (!response || !response.ok) {
                if (response && response.status === 403) {
                    throw new Error('Access denied: You do not have permission to view analytics.');
                } else if (response) {
                    const errorData = await response.json();
                    throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
                } else {
                    throw new Error('Network error or authentication failed');
                }
            }

            const data = await response.json();
            
            // Update KPIs
            this.updateKPIs(data.kpis);
            
            // Update charts
            this.updateCharts(data.charts);
            
        } catch (error) {
            console.error('Error loading dashboard data:', error);
            throw error;
        }
    }

    updateKPIs(kpis) {
        // Update KPI values
        const totalBookingsEl = document.getElementById('total-bookings');
        const totalRevenueEl = document.getElementById('total-revenue');
        const completionRateEl = document.getElementById('completion-rate');
        const activeBookingsEl = document.getElementById('active-bookings');

        if (totalBookingsEl) {
            totalBookingsEl.textContent = kpis.total_bookings || 0;
        }
        
        if (totalRevenueEl) {
            totalRevenueEl.textContent = this.formatCurrency(kpis.total_revenue || 0);
        }
        
        if (completionRateEl) {
            completionRateEl.textContent = `${(kpis.completion_rate || 0).toFixed(1)}%`;
        }
        
        if (activeBookingsEl) {
            activeBookingsEl.textContent = kpis.active_bookings || 0;
        }
    }

    updateCharts(chartsData) {
        // Update project distribution chart
        this.updateProjectChart(chartsData.project_distribution);
        
        // Update revenue by type chart
        this.updateRevenueChart(chartsData.property_types);
        
        // Update status distribution chart
        this.updateStatusChart(chartsData.status_distribution);
    }

    updateProjectChart(projectData) {
        const ctx = document.getElementById('project-chart');
        if (!ctx) return;

        // Destroy existing chart if it exists
        if (this.charts.projects) {
            this.charts.projects.destroy();
        }

        // Prepare data from Chart.js format
        const labels = projectData.labels || [];
        const datasets = projectData.datasets || [];
        const dataset = datasets[0] || { data: [], backgroundColor: [] };

        this.charts.projects = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: dataset.data,
                    backgroundColor: dataset.backgroundColor || this.generateColors(labels.length),
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Bookings by Project'
                    },
                    legend: {
                        display: true,
                        position: 'bottom'
                    }
                }
            }
        });
    }

    updateRevenueChart(propertyTypeData) {
        const ctx = document.getElementById('revenue-chart');
        if (!ctx) return;

        // Destroy existing chart if it exists
        if (this.charts.revenue) {
            this.charts.revenue.destroy();
        }

        // Prepare data from Chart.js format
        const labels = propertyTypeData.labels || [];
        const datasets = propertyTypeData.datasets || [];
        const dataset = datasets[0] || { data: [], backgroundColor: [] };

        this.charts.revenue = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Revenue (₹)',
                    data: dataset.data,
                    backgroundColor: dataset.backgroundColor || this.generateColors(labels.length),
                    borderColor: (dataset.backgroundColor || this.generateColors(labels.length)).map(color => color.replace('0.8', '1')),
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Revenue (₹)'
                        },
                        ticks: {
                            callback: function(value) {
                                return '₹' + value.toLocaleString();
                            }
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Property Type'
                        }
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Revenue by Property Type'
                    },
                    legend: {
                        display: false
                    }
                }
            }
        });
    }

    updateStatusChart(statusData) {
        const ctx = document.getElementById('status-chart');
        if (!ctx) return;

        // Destroy existing chart if it exists
        if (this.charts.status) {
            this.charts.status.destroy();
        }

        // Prepare data from Chart.js format
        const labels = statusData.labels || [];
        const datasets = statusData.datasets || [];
        const dataset = datasets[0] || { data: [], backgroundColor: [] };

        this.charts.status = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: dataset.data,
                    backgroundColor: dataset.backgroundColor || [
                        'rgba(40, 167, 69, 0.8)',   // Green for Active
                        'rgba(0, 123, 255, 0.8)',   // Blue for Complete
                        'rgba(220, 53, 69, 0.8)'    // Red for Cancelled
                    ],
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Bookings by Status'
                    },
                    legend: {
                        display: true,
                        position: 'bottom'
                    }
                }
            }
        });
    }

    generateColors(count) {
        const baseColors = [
            'rgba(102, 126, 234, 0.8)',
            'rgba(118, 75, 162, 0.8)',
            'rgba(255, 99, 132, 0.8)',
            'rgba(54, 162, 235, 0.8)',
            'rgba(255, 205, 86, 0.8)',
            'rgba(75, 192, 192, 0.8)',
            'rgba(153, 102, 255, 0.8)',
            'rgba(255, 159, 64, 0.8)'
        ];

        const colors = [];
        for (let i = 0; i < count; i++) {
            colors.push(baseColors[i % baseColors.length]);
        }
        return colors;
    }

    async applyFilters() {
        try {
            UIUtils.setLoading('apply-filter-btn', true);
            
            // Reload dashboard data with current filters
            await this.loadDashboardData();
            
            UIUtils.showSuccess('Filters applied successfully');
            
        } catch (error) {
            console.error('Error applying filters:', error);
            UIUtils.showError('Failed to apply filters');
        } finally {
            UIUtils.setLoading('apply-filter-btn', false);
        }
    }

    async exportData() {
        try {
            UIUtils.setLoading('export-btn', true);
            
            // Get selected export format
            const exportFormat = document.getElementById('export-format')?.value || 'csv';
            
            const params = new URLSearchParams();
            params.append('type', 'kpis');
            params.append('format', exportFormat);
            
            // Add date range
            if (this.dateRange.start_date) {
                params.append('start_date', this.dateRange.start_date + 'T00:00:00');
            }
            if (this.dateRange.end_date) {
                params.append('end_date', this.dateRange.end_date + 'T23:59:59');
            }
            
            // Add filters
            Object.keys(this.currentFilters).forEach(key => {
                if (this.currentFilters[key]) {
                    params.append(key, this.currentFilters[key]);
                }
            });

            const response = await authService.apiRequest(`/analytics/export?${params.toString()}`);

            if (!response || !response.ok) {
                if (response) {
                    const errorData = await response.json();
                    throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
                } else {
                    throw new Error('Network error or authentication failed');
                }
            }

            const data = await response.json();
            
            // Export based on format
            if (exportFormat === 'csv' && data.csv_data && data.csv_headers) {
                // Create and download CSV file
                this.downloadCSV(data.csv_data, data.csv_headers, 'analytics_kpis');
            } else {
                // Fallback to JSON export
                this.downloadJSON(data, 'analytics_export');
            }
            
            UIUtils.showSuccess(`Data exported successfully as ${exportFormat.toUpperCase()}`);
            
        } catch (error) {
            console.error('Error exporting data:', error);
            UIUtils.showError('Failed to export data');
        } finally {
            UIUtils.setLoading('export-btn', false);
        }
    }

    downloadCSV(data, headers, filename) {
        // Convert data to CSV format
        const csvContent = this.convertToCSV(data, headers);
        
        // Create blob and download
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `${filename}_${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        
        URL.revokeObjectURL(url);
    }

    convertToCSV(data, headers) {
        if (!data || data.length === 0) {
            return '';
        }

        // Create CSV header
        let csv = headers.join(',') + '\n';
        
        // Add data rows
        data.forEach(row => {
            const values = headers.map(header => {
                const value = row[header] || '';
                // Escape commas and quotes in values
                if (typeof value === 'string' && (value.includes(',') || value.includes('"') || value.includes('\n'))) {
                    return `"${value.replace(/"/g, '""')}"`;
                }
                return value;
            });
            csv += values.join(',') + '\n';
        });
        
        return csv;
    }

    downloadJSON(data, filename) {
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `${filename}_${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        
        URL.revokeObjectURL(url);
    }

    formatCurrency(amount) {
        return '₹' + amount.toLocaleString('en-IN');
    }

    // Cleanup method to destroy charts when switching tabs
    cleanup() {
        Object.keys(this.charts).forEach(key => {
            if (this.charts[key]) {
                this.charts[key].destroy();
                delete this.charts[key];
            }
        });
    }
}

// Initialize analytics manager when DOM is loaded and auth is ready
document.addEventListener('DOMContentLoaded', () => {
    const initAnalytics = () => {
        if (window.KIRO_AUTH_READY) {
            window.analyticsManager = new AnalyticsManager();
        } else {
            // Wait for auth to be ready
            setTimeout(initAnalytics, 50);
        }
    };
    initAnalytics();
});