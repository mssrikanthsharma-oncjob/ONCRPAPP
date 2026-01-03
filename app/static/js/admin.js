/**
 * Admin Portal JavaScript
 * Handles LLM configuration and customer enquiry management
 */

class AdminPortal {
    constructor() {
        this.init();
    }

    init() {
        this.bindEvents();
        // Don't load data immediately - wait for authentication
        // Data will be loaded when tabs are switched to
    }

    bindEvents() {
        // LLM Configuration
        document.getElementById('save-llm-config-btn')?.addEventListener('click', () => this.saveLLMConfig());
        
        // Customer Enquiries
        document.getElementById('refresh-enquiries-btn')?.addEventListener('click', () => this.loadCustomerEnquiries());
        document.getElementById('enquiry-type-filter')?.addEventListener('change', () => this.loadCustomerEnquiries());
    }

    async loadLLMConfig() {
        try {
            const response = await fetch('/api/admin/llm-config', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('jwt_token')}`
                }
            });

            const data = await response.json();

            if (response.ok) {
                this.displayLLMConfig(data.config, data.available_models);
            } else {
                console.error('Failed to load LLM config:', data.error);
            }
        } catch (error) {
            console.error('Network error loading LLM config:', error);
        }
    }

    displayLLMConfig(config, availableModels) {
        const modelSelect = document.getElementById('llm-model');
        const configDisplay = document.getElementById('config-display');

        // Populate model dropdown
        if (modelSelect) {
            modelSelect.innerHTML = '<option value="">Select Model</option>';
            availableModels.forEach(model => {
                const option = document.createElement('option');
                option.value = model;
                option.textContent = model.toUpperCase();
                if (config && config.model_name === model) {
                    option.selected = true;
                }
                modelSelect.appendChild(option);
            });
        }

        // Display current configuration
        if (config) {
            configDisplay.innerHTML = `
                <div class="config-item">
                    <strong>Model:</strong> ${config.model_name}
                </div>
                <div class="config-item">
                    <strong>API Key:</strong> ${config.api_key}
                </div>
                <div class="config-item">
                    <strong>Status:</strong> <span class="status-active">Active</span>
                </div>
                <div class="config-item">
                    <strong>Last Updated:</strong> ${new Date(config.updated_at).toLocaleString()}
                </div>
            `;
        } else {
            configDisplay.innerHTML = '<p>No configuration found</p>';
        }
    }

    async saveLLMConfig() {
        const modelName = document.getElementById('llm-model').value;
        const apiKey = document.getElementById('api-key').value;

        if (!modelName || !apiKey) {
            this.showError('Please select a model and enter API key');
            return;
        }

        try {
            document.getElementById('save-llm-config-btn').disabled = true;
            document.getElementById('save-llm-config-btn').textContent = 'Saving...';

            const response = await fetch('/api/admin/llm-config', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('jwt_token')}`
                },
                body: JSON.stringify({
                    model_name: modelName,
                    api_key: apiKey
                })
            });

            const data = await response.json();

            if (response.ok) {
                this.showSuccess('LLM configuration saved successfully');
                this.loadLLMConfig(); // Reload to show updated config
                document.getElementById('api-key').value = ''; // Clear API key field
            } else {
                this.showError(data.error || 'Failed to save configuration');
            }
        } catch (error) {
            this.showError('Network error. Please try again.');
        } finally {
            document.getElementById('save-llm-config-btn').disabled = false;
            document.getElementById('save-llm-config-btn').textContent = 'Save Configuration';
        }
    }

    async loadEnquiryStats() {
        try {
            const response = await fetch('/api/admin/customer-enquiries/stats', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('jwt_token')}`
                }
            });

            const data = await response.json();

            if (response.ok) {
                this.displayEnquiryStats(data.stats);
            } else {
                console.error('Failed to load enquiry stats:', data.error);
            }
        } catch (error) {
            console.error('Network error loading enquiry stats:', error);
        }
    }

    displayEnquiryStats(stats) {
        document.getElementById('total-enquiries').textContent = stats.total_enquiries || 0;
        document.getElementById('search-enquiries').textContent = stats.search_enquiries || 0;
        document.getElementById('advice-enquiries').textContent = stats.advice_enquiries || 0;
        document.getElementById('reports-generated').textContent = stats.reports_generated || 0;
    }

    async loadCustomerEnquiries() {
        try {
            const typeFilter = document.getElementById('enquiry-type-filter')?.value || '';
            const url = `/api/admin/customer-enquiries${typeFilter ? `?type=${typeFilter}` : ''}`;

            const response = await fetch(url, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('jwt_token')}`
                }
            });

            const data = await response.json();

            if (response.ok) {
                this.displayCustomerEnquiries(data.enquiries);
            } else {
                console.error('Failed to load customer enquiries:', data.error);
            }
        } catch (error) {
            console.error('Network error loading customer enquiries:', error);
        }
    }

    displayCustomerEnquiries(enquiries) {
        const tbody = document.getElementById('enquiries-tbody');
        
        if (!enquiries || enquiries.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; padding: 20px;">No enquiries found</td></tr>';
            return;
        }

        tbody.innerHTML = enquiries.map(enquiry => {
            const content = this.getEnquiryContent(enquiry);
            const reportStatus = enquiry.report_generated ? 
                '<span class="status-complete">Yes</span>' : 
                '<span class="status-pending">No</span>';

            return `
                <tr>
                    <td>${enquiry.customer_username || 'Unknown'}</td>
                    <td>${enquiry.email}</td>
                    <td><span class="enquiry-type-${enquiry.enquiry_type}">${enquiry.enquiry_type.toUpperCase()}</span></td>
                    <td>${content}</td>
                    <td>${reportStatus}</td>
                    <td>${new Date(enquiry.created_at).toLocaleDateString()}</td>
                    <td>
                        <button class="btn btn-sm" onclick="adminPortal.viewEnquiryDetails(${enquiry.id})">View</button>
                    </td>
                </tr>
            `;
        }).join('');
    }

    getEnquiryContent(enquiry) {
        if (enquiry.enquiry_type === 'search') {
            try {
                const criteria = JSON.parse(enquiry.search_criteria || '{}');
                return `Location: ${criteria.location || 'N/A'}, Type: ${criteria.property_type || 'Any'}`;
            } catch {
                return 'Search criteria';
            }
        } else if (enquiry.enquiry_type === 'advice') {
            return enquiry.advice_request ? 
                enquiry.advice_request.substring(0, 50) + '...' : 
                'Advice request';
        }
        return 'N/A';
    }

    async viewEnquiryDetails(enquiryId) {
        try {
            const response = await fetch(`/api/admin/customer-enquiries/${enquiryId}`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('jwt_token')}`
                }
            });

            const data = await response.json();

            if (response.ok) {
                this.showEnquiryModal(data.enquiry);
            } else {
                this.showError(data.error || 'Failed to load enquiry details');
            }
        } catch (error) {
            this.showError('Network error. Please try again.');
        }
    }

    showEnquiryModal(enquiry) {
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.style.display = 'block';

        let content = '';
        if (enquiry.enquiry_type === 'search') {
            try {
                const criteria = JSON.parse(enquiry.search_criteria || '{}');
                content = `
                    <h4>Search Criteria:</h4>
                    <ul>
                        <li><strong>Location:</strong> ${criteria.location || 'N/A'}</li>
                        <li><strong>Property Type:</strong> ${criteria.property_type || 'Any'}</li>
                        <li><strong>Budget Range:</strong> ₹${criteria.budget_min || 0} - ₹${criteria.budget_max || 'No limit'}</li>
                    </ul>
                `;
            } catch {
                content = '<p>Invalid search criteria data</p>';
            }
        } else if (enquiry.enquiry_type === 'advice') {
            content = `
                <h4>Advice Request:</h4>
                <p>${enquiry.advice_request || 'N/A'}</p>
                <h4>LLM Response:</h4>
                <div style="background: #f5f5f5; padding: 10px; border-radius: 4px; white-space: pre-wrap;">
                    ${enquiry.llm_response || 'No response generated'}
                </div>
            `;
        }

        if (enquiry.full_report) {
            content += `
                <h4>Generated Report:</h4>
                <div style="background: #f9f9f9; padding: 10px; border-radius: 4px; white-space: pre-wrap; max-height: 300px; overflow-y: auto;">
                    ${enquiry.full_report}
                </div>
            `;
        }

        modal.innerHTML = `
            <div class="modal-content" style="max-width: 800px;">
                <div class="modal-header">
                    <h3>Enquiry Details #${enquiry.id}</h3>
                    <span class="close" onclick="this.parentElement.parentElement.parentElement.remove()">&times;</span>
                </div>
                <div class="modal-body">
                    <div class="enquiry-info">
                        <p><strong>Customer:</strong> ${enquiry.customer_username || 'Unknown'}</p>
                        <p><strong>Email:</strong> ${enquiry.email}</p>
                        <p><strong>Type:</strong> ${enquiry.enquiry_type.toUpperCase()}</p>
                        <p><strong>Date:</strong> ${new Date(enquiry.created_at).toLocaleString()}</p>
                        <p><strong>Report Generated:</strong> ${enquiry.report_generated ? 'Yes' : 'No'}</p>
                    </div>
                    <hr>
                    ${content}
                </div>
                <div class="modal-footer">
                    <button class="btn btn-primary" onclick="this.parentElement.parentElement.parentElement.remove()">Close</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
    }

    showError(message) {
        // Create or update error message element
        let errorElement = document.getElementById('admin-error-message');
        if (!errorElement) {
            errorElement = document.createElement('div');
            errorElement.id = 'admin-error-message';
            errorElement.className = 'error-message';
            document.querySelector('#dashboard .main-content').prepend(errorElement);
        }
        
        errorElement.textContent = message;
        errorElement.style.display = 'block';
        
        setTimeout(() => {
            errorElement.style.display = 'none';
        }, 5000);
    }

    showSuccess(message) {
        // Create or update success message element
        let successElement = document.getElementById('admin-success-message');
        if (!successElement) {
            successElement = document.createElement('div');
            successElement.id = 'admin-success-message';
            successElement.className = 'success-message';
            document.querySelector('#dashboard .main-content').prepend(successElement);
        }
        
        successElement.textContent = message;
        successElement.style.display = 'block';
        
        setTimeout(() => {
            successElement.style.display = 'none';
        }, 5000);
    }
}

// Initialize admin portal when DOM is loaded and auth is ready
document.addEventListener('DOMContentLoaded', () => {
    const initAdmin = () => {
        if (window.KIRO_AUTH_READY && document.getElementById('dashboard')) {
            window.adminPortal = new AdminPortal();
        } else if (!window.KIRO_AUTH_READY) {
            // Wait for auth to be ready
            setTimeout(initAdmin, 50);
        }
    };
    initAdmin();
});