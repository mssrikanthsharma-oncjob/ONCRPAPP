/**
 * Customer Portal JavaScript
 * Handles property search and advisory functionality
 */

class CustomerPortal {
    constructor() {
        this.isEmailVerified = false;
        this.currentEnquiries = [];
        this.init();
    }

    init() {
        this.bindEvents();
        this.checkEmailVerification();
        // Enable search and advice forms by default
        this.enableForms();
        // Load activity summary
        this.loadActivitySummary();
    }

    bindEvents() {
        // Email verification
        document.getElementById('send-otp-btn')?.addEventListener('click', () => this.sendOTP());
        document.getElementById('verify-otp-btn')?.addEventListener('click', () => this.verifyOTP());
        
        // Property search
        document.getElementById('search-properties-btn')?.addEventListener('click', () => this.searchProperties());
        document.getElementById('get-advice-btn')?.addEventListener('click', () => this.getPropertyAdvice());
        
        // Report generation
        document.getElementById('generate-pdf-report-btn')?.addEventListener('click', () => this.generatePDFReport());
        document.getElementById('download-report-btn')?.addEventListener('click', () => this.downloadReport());
        
        // Customer logout
        document.getElementById('customer-logout-btn')?.addEventListener('click', () => this.logout());
        
        // Tab switching
        document.querySelectorAll('#customer-portal .nav-tab').forEach(tab => {
            tab.addEventListener('click', (e) => this.switchTab(e.target.dataset.tab));
        });
    }

    checkEmailVerification() {
        // Check if user email is already verified
        const user = JSON.parse(localStorage.getItem('user') || '{}');
        if (user.is_email_verified) {
            this.isEmailVerified = true;
            document.getElementById('verification-status').style.display = 'block';
            document.getElementById('email-verification').style.display = 'none';
            // Enable report generation
            this.enableReportGeneration();
        }
    }

    async sendOTP() {
        const email = document.getElementById('customer-email').value;
        
        if (!email) {
            this.showError('Please enter your email address');
            return;
        }

        try {
            const response = await fetch('/api/customer/send-otp', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('jwt_token')}`
                },
                body: JSON.stringify({ email })
            });

            const data = await response.json();

            if (response.ok) {
                document.getElementById('otp-section').style.display = 'flex';
                this.showSuccess(`OTP sent to ${email}. Demo OTP: ${data.otp}`);
            } else {
                this.showError(data.error || 'Failed to send OTP');
            }
        } catch (error) {
            this.showError('Network error. Please try again.');
        }
    }

    async verifyOTP() {
        const otpCode = document.getElementById('otp-code').value;
        
        if (!otpCode) {
            this.showError('Please enter the OTP code');
            return;
        }

        try {
            const response = await fetch('/api/customer/verify-otp', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('jwt_token')}`
                },
                body: JSON.stringify({ otp_code: otpCode })
            });

            const data = await response.json();

            if (response.ok) {
                this.isEmailVerified = true;
                document.getElementById('verification-status').style.display = 'block';
                document.getElementById('email-verification').style.display = 'none';
                this.showSuccess('Email verified successfully!');
                
                // Enable report generation
                this.enableReportGeneration();
                
                // Update user data in localStorage
                const user = JSON.parse(localStorage.getItem('user') || '{}');
                user.is_email_verified = true;
                localStorage.setItem('user', JSON.stringify(user));
            } else {
                this.showError(data.error || 'Invalid OTP');
            }
        } catch (error) {
            this.showError('Network error. Please try again.');
        }
    }

    enableForms() {
        // Always enable search and advice forms - no email verification required
        document.getElementById('search-form').style.opacity = '1';
        document.getElementById('search-form').style.pointerEvents = 'auto';
        document.getElementById('advice-form').style.opacity = '1';
        document.getElementById('advice-form').style.pointerEvents = 'auto';
    }

    enableReportGeneration() {
        // Enable report generation section
        document.getElementById('report-generation').style.opacity = '1';
        document.getElementById('report-generation').style.pointerEvents = 'auto';
        document.getElementById('generate-pdf-report-btn').disabled = false;
    }

    async loadActivitySummary() {
        try {
            const response = await fetch('/api/customer/get-activity-summary', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('jwt_token')}`
                }
            });

            if (response.ok) {
                const data = await response.json();
                document.getElementById('search-count').textContent = data.search_count || 0;
                document.getElementById('advice-count').textContent = data.advice_count || 0;
                document.getElementById('total-enquiries').textContent = data.total_enquiries || 0;
            }
        } catch (error) {
            console.error('Error loading activity summary:', error);
        }
    }

    async searchProperties() {
        const searchCriteria = {
            location: document.getElementById('search-location').value,
            property_type: document.getElementById('search-property-type').value,
            budget_min: parseInt(document.getElementById('search-budget-min').value) || 0,
            budget_max: parseInt(document.getElementById('search-budget-max').value) || 0
        };

        if (!searchCriteria.location) {
            this.showError('Please enter a location');
            return;
        }

        try {
            document.getElementById('search-properties-btn').disabled = true;
            document.getElementById('search-properties-btn').textContent = 'Searching...';

            const response = await fetch('/api/customer/search-properties', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('jwt_token')}`
                },
                body: JSON.stringify({ search_criteria: searchCriteria })
            });

            const data = await response.json();

            if (response.ok) {
                this.displaySearchResults(data.results);
                this.currentEnquiries.push(data.enquiry_id);
                this.showSuccess('Properties found! Scroll down to see results.');
                // Update activity summary
                this.loadActivitySummary();
            } else {
                this.showError(data.error || 'Search failed');
            }
        } catch (error) {
            this.showError('Network error. Please try again.');
        } finally {
            document.getElementById('search-properties-btn').disabled = false;
            document.getElementById('search-properties-btn').textContent = 'Search Properties';
        }
    }

    displaySearchResults(results) {
        const resultsContainer = document.getElementById('search-results');
        
        if (!results || results.length === 0) {
            resultsContainer.innerHTML = '<p>No properties found matching your criteria.</p>';
            return;
        }

        let html = '<h3>Search Results</h3><div class="property-grid">';
        
        results.forEach(property => {
            html += `
                <div class="property-card">
                    <img src="${property.image_url}" alt="${property.title}" class="property-image">
                    <div class="property-details">
                        <h4>${property.title}</h4>
                        <p class="property-location">${property.location}</p>
                        <p class="property-price">₹${property.price.toLocaleString()}</p>
                        <p class="property-area">${property.area} | ${property.bedrooms}BHK | ${property.bathrooms} Bath</p>
                        <p class="property-description">${property.description}</p>
                        <p class="property-contact">Contact: ${property.contact}</p>
                    </div>
                </div>
            `;
        });
        
        html += '</div>';
        resultsContainer.innerHTML = html;
    }

    async getPropertyAdvice() {
        const adviceRequest = document.getElementById('advice-request').value;
        
        if (!adviceRequest.trim()) {
            this.showError('Please describe your requirements');
            return;
        }

        try {
            document.getElementById('get-advice-btn').disabled = true;
            document.getElementById('get-advice-btn').textContent = 'Getting Advice...';

            const response = await fetch('/api/customer/get-property-advice', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('jwt_token')}`
                },
                body: JSON.stringify({ advice_request: adviceRequest })
            });

            const data = await response.json();

            if (response.ok) {
                this.displayAdviceResults(data.advice);
                this.currentEnquiries.push(data.enquiry_id);
                this.showSuccess('Advice generated! Scroll down to see recommendations.');
                // Update activity summary
                this.loadActivitySummary();
            } else {
                this.showError(data.error || 'Failed to get advice');
            }
        } catch (error) {
            this.showError('Network error. Please try again.');
        } finally {
            document.getElementById('get-advice-btn').disabled = false;
            document.getElementById('get-advice-btn').textContent = 'Get Property Advice';
        }
    }

    displayAdviceResults(advice) {
        const resultsContainer = document.getElementById('advice-results');
        
        resultsContainer.innerHTML = `
            <div class="advice-card">
                <h3>Property Advisory</h3>
                <div class="advice-content">
                    ${advice.replace(/\n/g, '<br>')}
                </div>
            </div>
        `;
    }

    async generatePDFReport() {
        // Check if email is verified for report generation
        if (!this.isEmailVerified) {
            this.showError('Please verify your email address to generate reports');
            return;
        }

        const reportType = document.getElementById('report-type').value;
        const reportFormat = document.getElementById('report-format').value;

        try {
            const button = document.getElementById('generate-pdf-report-btn');
            button.disabled = true;
            button.textContent = 'Generating PDF...';

            const response = await fetch('/api/customer/generate-pdf-report', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('jwt_token')}`
                },
                body: JSON.stringify({ 
                    report_type: reportType,
                    enquiry_ids: this.currentEnquiries 
                })
            });

            if (response.ok) {
                // Handle PDF download
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.style.display = 'none';
                a.href = url;
                
                // Get filename from response headers or create default
                const contentDisposition = response.headers.get('Content-Disposition');
                let filename = 'ONC_Property_Report.pdf';
                if (contentDisposition) {
                    const filenameMatch = contentDisposition.match(/filename="(.+)"/);
                    if (filenameMatch) {
                        filename = filenameMatch[1];
                    }
                }
                
                a.download = filename;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);

                this.showSuccess('PDF report generated and downloaded successfully!');
                
                // Show report status
                document.getElementById('report-status').style.display = 'block';
                document.getElementById('report-status').innerHTML = `
                    <div class="success-message">
                        <h4>Report Generated Successfully!</h4>
                        <p>Your ${reportType.replace('-', ' ')} report has been generated and downloaded.</p>
                        <p><strong>Filename:</strong> ${filename}</p>
                        <p><strong>Generated:</strong> ${new Date().toLocaleString()}</p>
                    </div>
                `;
            } else {
                const errorData = await response.json();
                this.showError(errorData.error || 'Failed to generate report');
            }
        } catch (error) {
            this.showError('Network error. Please try again.');
        } finally {
            const button = document.getElementById('generate-pdf-report-btn');
            button.disabled = false;
            button.textContent = 'Generate PDF Report';
        }
    }

    downloadReport() {
        // This method can be used for additional download functionality if needed
        this.showSuccess('Report download initiated');
    }

    showReportPreview(preview) {
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.style.display = 'block';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Report Preview</h3>
                    <span class="close" onclick="this.parentElement.parentElement.parentElement.remove()">&times;</span>
                </div>
                <div class="modal-body">
                    <pre style="white-space: pre-wrap; font-family: Arial, sans-serif;">${preview}</pre>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-primary" onclick="this.parentElement.parentElement.parentElement.remove()">Close</button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
    }

    switchTab(tabName) {
        // Hide all tab contents
        document.querySelectorAll('#customer-portal .tab-content').forEach(tab => {
            tab.classList.remove('active');
        });
        
        // Remove active class from all tabs
        document.querySelectorAll('#customer-portal .nav-tab').forEach(tab => {
            tab.classList.remove('active');
        });
        
        // Show selected tab content
        document.getElementById(`${tabName}-tab`).classList.add('active');
        
        // Add active class to clicked tab
        document.querySelector(`#customer-portal .nav-tab[data-tab="${tabName}"]`).classList.add('active');
    }

    logout() {
        localStorage.removeItem('jwt_token');
        localStorage.removeItem('user');
        window.location.reload();
    }

    showError(message) {
        // Create or update error message element
        let errorElement = document.getElementById('customer-error-message');
        if (!errorElement) {
            errorElement = document.createElement('div');
            errorElement.id = 'customer-error-message';
            errorElement.className = 'error-message';
            document.querySelector('#customer-portal .main-content').prepend(errorElement);
        }
        
        errorElement.textContent = message;
        errorElement.style.display = 'block';
        
        setTimeout(() => {
            errorElement.style.display = 'none';
        }, 5000);
    }

    showSuccess(message) {
        // Create or update success message element
        let successElement = document.getElementById('customer-success-message');
        if (!successElement) {
            successElement = document.createElement('div');
            successElement.id = 'customer-success-message';
            successElement.className = 'success-message';
            document.querySelector('#customer-portal .main-content').prepend(successElement);
        }
        
        successElement.textContent = message;
        successElement.style.display = 'block';
        
        setTimeout(() => {
            successElement.style.display = 'none';
        }, 5000);
    }
}

// Initialize customer portal when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('customer-portal')) {
        window.customerPortal = new CustomerPortal();
    }
});