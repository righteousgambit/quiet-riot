/**
 * Scan Manager Module
 * Handles scan execution and status polling
 */

class ScanManager {
    constructor() {
        this.currentScanId = null;
        this.pollInterval = null;
    }

    /**
     * Start a new scan
     */
    async start(scanConfig) {
        try {
            const result = await window.apiClient.startScan(scanConfig);
            this.currentScanId = result.scan_id;

            // Show results panel
            window.uiState.showScanResults();

            // Hide empty state
            const resultsEmpty = document.getElementById('resultsEmpty');
            if (resultsEmpty) {
                resultsEmpty.style.display = 'none';
            }

            // Start polling
            this.startPolling(result.scan_id);

            return result;
        } catch (error) {
            window.uiState.showError(`Error starting scan: ${error.message}`);
            throw error;
        }
    }

    /**
     * Start polling scan status
     */
    startPolling(scanId) {
        // Clear any existing interval
        this.stopPolling();

        // Poll immediately
        this.poll(scanId);

        // Then poll every 2 seconds
        this.pollInterval = setInterval(() => {
            this.poll(scanId);
        }, 2000);
    }

    /**
     * Stop polling
     */
    stopPolling() {
        if (this.pollInterval) {
            clearInterval(this.pollInterval);
            this.pollInterval = null;
        }
    }

    /**
     * Poll scan status
     */
    async poll(scanId) {
        try {
            const data = await window.apiClient.getScanStatus(scanId);
            this.updateStatus(data);

            // Stop polling if scan is complete
            if (data.status === 'completed' || data.status === 'failed') {
                this.stopPolling();
                this.updateStartButton(true);
            }
        } catch (error) {
            console.error('Error polling scan status:', error);
            this.stopPolling();
            window.uiState.showError(`Error checking scan status: ${error.message}`);
        }
    }

    /**
     * Update scan status display
     */
    updateStatus(data) {
        const statusDiv = document.getElementById('scanStatus');
        const statsDiv = document.getElementById('scanStats');
        const resultsEmpty = document.getElementById('resultsEmpty');

        // Hide empty state when results exist
        if (resultsEmpty && data && data.status) {
            resultsEmpty.style.display = 'none';
        }

        if (!statusDiv || !statsDiv) return;

        // Update status
        statusDiv.className = `status ${data.status}`;
        statusDiv.textContent = `Status: ${data.status.toUpperCase()}`;
        if (data.error) {
            statusDiv.textContent += ` - Error: ${data.error}`;
        }

        // Update stats
        statsDiv.innerHTML = `
            <div class="stat-card">
                <div class="stat-value">${data.valid_principals_count || 0}</div>
                <div class="stat-label">Valid Principals</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${data.total_scanned || 0}</div>
                <div class="stat-label">Total Scanned</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${(data.success_rate || 0).toFixed(2)}%</div>
                <div class="stat-label">Success Rate</div>
            </div>
            ${data.duration_seconds ? `
            <div class="stat-card">
                <div class="stat-value">${data.duration_seconds.toFixed(1)}s</div>
                <div class="stat-label">Duration</div>
            </div>
            ` : ''}
        `;
    }

    /**
     * Update start button state
     */
    updateStartButton(enabled = false) {
        const btn = document.getElementById('startScanBtn');
        if (!btn) return;

        btn.disabled = !enabled;
        if (enabled) {
            btn.textContent = 'Start New Scan';
            // When starting a new scan, go back to scan tab and reset to step 1
            btn.onclick = () => {
                window.uiState.switchTab('scan');
                window.uiState.showStep(1);
                this.currentScanId = null;
                // Reset form
                const scanTypeSelect = document.getElementById('scanType');
                if (scanTypeSelect) scanTypeSelect.value = '';
                document.getElementById('nextBtn1').disabled = true;
            };
        }
    }

    /**
     * Collect scan configuration from form
     */
    collectScanConfig(scanType) {
        const config = {
            scan_type: scanType.id,
            threads: parseInt(document.getElementById('threads')?.value) || 100,
            aws_profile: document.getElementById('awsProfile')?.value || 'default',
        };

        // Collect step 2 configuration if needed
        if (scanType && scanType.requires_config !== false) {
            const step2Config = window.scanConfig.collectConfig(scanType);
            Object.assign(config, step2Config);
        }

        return config;
    }
}

// Export singleton instance
window.scanManager = new ScanManager();
