/**
 * UI State Management Module
 * Manages step navigation, indicators, and UI state
 */

class UIState {
    constructor() {
        this.currentStep = 1;
        this.maxSteps = 3;
        this.currentTab = 'scan';
    }

    /**
     * Update step indicator visualization
     */
    updateStepIndicator(step) {
        for (let i = 1; i <= this.maxSteps; i++) {
            const indicator = document.getElementById(`indicator${i}`);
            const stepContent = document.getElementById(`step${i}`);

            if (!indicator || !stepContent) continue;

            if (i < step) {
                indicator.classList.add('completed');
                indicator.classList.remove('active');
            } else if (i === step) {
                indicator.classList.add('active');
                indicator.classList.remove('completed');
            } else {
                indicator.classList.remove('active', 'completed');
            }

            stepContent.classList.toggle('active', i === step);
        }
    }

    /**
     * Navigate to a specific step
     */
    showStep(step) {
        if (step < 1 || step > this.maxSteps) {
            console.warn(`Invalid step: ${step}`);
            return;
        }

        this.currentStep = step;
        this.updateStepIndicator(step);
    }

    /**
     * Go to next step
     */
    nextStep() {
        if (this.currentStep < this.maxSteps) {
            this.showStep(this.currentStep + 1);
        }
    }

    /**
     * Go to previous step
     */
    previousStep() {
        if (this.currentStep > 1) {
            this.showStep(this.currentStep - 1);
        }
    }

    /**
     * Switch to a specific tab
     */
    switchTab(tabName) {
        // Update tab buttons
        document.querySelectorAll('.tab-button').forEach(btn => {
            if (btn.dataset.tab === tabName) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });

        // Update tab content
        document.querySelectorAll('.tab-content').forEach(content => {
            if (content.id === `${tabName}-tab`) {
                content.classList.add('active');
            } else {
                content.classList.remove('active');
            }
        });

        this.currentTab = tabName;

        // Load infrastructure when switching to infrastructure tab
        if (tabName === 'infrastructure') {
            window.infrastructureManager.load();
        }

        // Handle results tab empty state
        if (tabName === 'results') {
            const statusDiv = document.getElementById('scanStatus');
            const resultsEmpty = document.getElementById('resultsEmpty');

            if (resultsEmpty && statusDiv) {
                // Show empty state if no scan status exists
                if (!statusDiv.textContent || statusDiv.textContent.trim() === '') {
                    resultsEmpty.style.display = 'block';
                } else {
                    resultsEmpty.style.display = 'none';
                }
            }
        }
    }

    /**
     * Show scan results - switch to results tab
     */
    showScanResults() {
        this.switchTab('results');
        // Hide empty state if results exist
        const resultsEmpty = document.getElementById('resultsEmpty');
        if (resultsEmpty) {
            resultsEmpty.style.display = 'none';
        }
    }

    /**
     * Hide scan results - switch back to scan tab
     */
    hideScanResults() {
        this.switchTab('scan');
    }

    /**
     * Show loading state on button
     */
    setButtonLoading(buttonId, loading = true, loadingText = 'Loading...') {
        const button = document.getElementById(buttonId);
        if (!button) return;

        if (loading) {
            button.disabled = true;
            button.dataset.originalText = button.textContent;
            button.innerHTML = `<span class="loading"></span> ${loadingText}`;
        } else {
            button.disabled = false;
            button.textContent = button.dataset.originalText || button.textContent;
        }
    }

    /**
     * Show error message
     */
    showError(message, containerId = 'wizard') {
        const container = document.getElementById(containerId);
        if (!container) return;

        // Remove existing error messages
        const existingError = container.querySelector('.error-message');
        if (existingError) existingError.remove();

        // Create new error message
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.textContent = message;

        container.insertBefore(errorDiv, container.firstChild);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            errorDiv.remove();
        }, 5000);
    }
}

// Export singleton instance
window.uiState = new UIState();
