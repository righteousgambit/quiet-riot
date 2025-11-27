/**
 * API Client Module
 * Handles all API communication with the backend
 */

class APIClient {
    constructor() {
        this.baseURL = '';
    }

    async getScanTypes() {
        const response = await fetch('/api/scan-types');
        if (!response.ok) {
            throw new Error(`Failed to load scan types: ${response.statusText}`);
        }
        const data = await response.json();
        return data.scan_types;
    }

    async startScan(scanConfig) {
        const response = await fetch('/api/scans', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(scanConfig),
        });

        if (!response.ok) {
            let errorMessage = 'Failed to start scan';
            try {
                const errorData = await response.json();
                errorMessage = errorData.detail || errorMessage;
            } catch {
                const errorText = await response.text();
                errorMessage = errorText || errorMessage;
            }

            // Provide more helpful error messages
            if (response.status === 503) {
                if (errorMessage.includes('credentials')) {
                    errorMessage = 'AWS credentials are required. Please configure your AWS credentials first.';
                } else if (errorMessage.includes('Scanner not initialized')) {
                    errorMessage = 'Scanner not initialized. Please check your AWS credentials configuration.';
                }
            }

            const error = new Error(errorMessage);
            error.status = response.status;
            throw error;
        }

        return await response.json();
    }

    async getScanStatus(scanId) {
        const response = await fetch(`/api/scans/${scanId}`);
        if (!response.ok) {
            throw new Error(`Failed to get scan status: ${response.statusText}`);
        }
        return await response.json();
    }

    async getInfrastructure() {
        const response = await fetch('/api/infrastructure');
        if (!response.ok) {
            throw new Error(`Failed to load infrastructure: ${response.statusText}`);
        }
        return await response.json();
    }

    async cleanupInfrastructure() {
        const response = await fetch('/api/infrastructure/cleanup', {
            method: 'POST',
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(errorText || 'Failed to cleanup infrastructure');
        }

        return await response.json();
    }

    async generateEmails(domain, pattern, maxEmails) {
        const params = new URLSearchParams({
            domain,
            pattern,
            max_emails: maxEmails.toString(),
        });

        const response = await fetch(`/api/generate-emails?${params}`);
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(errorText || 'Failed to generate emails');
        }

        return await response.json();
    }

    async getCredentialsStatus() {
        const response = await fetch('/api/credentials');
        if (!response.ok) {
            throw new Error(`Failed to get credentials status: ${response.statusText}`);
        }
        return await response.json();
    }

    async setCredentials(profile, arn) {
        const response = await fetch('/api/credentials', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ profile, arn }),
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(errorText || 'Failed to set credentials');
        }

        return await response.json();
    }
}

// Export singleton instance
window.apiClient = new APIClient();
