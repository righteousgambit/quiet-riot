/**
 * Main Application Module
 * Initializes and coordinates all modules
 */

class App {
    constructor() {
        this.scanTypes = [];
        this.selectedScanType = null;
    }

    /**
     * Initialize the application
     */
    async init() {
        try {
            // Load scan types
            await this.loadScanTypes();

            // Setup event listeners
            this.setupEventListeners();

            // Initialize infrastructure panel
            window.infrastructureManager.setupListeners();
            await window.infrastructureManager.load();
            window.infrastructureManager.startAutoRefresh();

            // Initialize UI state
            window.uiState.updateStepIndicator(1);
            window.uiState.switchTab('scan'); // Start on scan tab
        } catch (error) {
            console.error('Error initializing app:', error);
            window.uiState.showError(`Failed to initialize application: ${error.message}`);
        }
    }

    /**
     * Load scan types from API
     */
    async loadScanTypes() {
        try {
            this.scanTypes = await window.apiClient.getScanTypes();
            window.scanTypes = this.scanTypes; // Make available globally

            const select = document.getElementById('scanType');
            if (!select) return;

            this.scanTypes.forEach(type => {
                const option = document.createElement('option');
                option.value = type.id;
                option.textContent = type.name;
                option.dataset.description = type.description;
                option.dataset.requiresConfig = type.requires_config;
                option.dataset.emailBased = type.email_based || false;
                option.dataset.iamBased = type.iam_based || false;
                select.appendChild(option);
            });
        } catch (error) {
            console.error('Error loading scan types:', error);
            throw error;
        }
    }

    /**
     * Setup all event listeners
     */
    setupEventListeners() {
        // Tab navigation
        this.setupTabNavigation();

        // Scan type selection
        this.setupScanTypeSelection();

        // Navigation buttons
        this.setupNavigationButtons();

        // Start scan button
        this.setupStartScanButton();
    }

    /**
     * Setup tab navigation
     */
    setupTabNavigation() {
        document.querySelectorAll('.tab-button').forEach(button => {
            button.addEventListener('click', (e) => {
                const tabName = e.currentTarget.dataset.tab;
                window.uiState.switchTab(tabName);
            });
        });
    }

    /**
     * Setup scan type selection
     */
    setupScanTypeSelection() {
        const scanTypeSelect = document.getElementById('scanType');
        if (!scanTypeSelect) return;

        scanTypeSelect.addEventListener('change', (e) => {
            const option = e.target.options[e.target.selectedIndex];
            if (!option || !option.value) {
                this.selectedScanType = null;
                document.getElementById('nextBtn1').disabled = true;
                document.getElementById('scanTypeDescription').textContent = '';
                return;
            }

            // Find selected scan type
            this.selectedScanType = this.scanTypes.find(
                t => t.id === parseInt(option.value)
            );

            // Update description
            const description = document.getElementById('scanTypeDescription');
            if (description) {
                description.textContent = option.dataset.description || '';
            }

            // Enable/disable next button
            const nextBtn = document.getElementById('nextBtn1');
            if (nextBtn) {
                nextBtn.disabled = !this.selectedScanType;
            }
        });
    }

    /**
     * Setup navigation buttons
     */
    setupNavigationButtons() {
        // Step 1 -> Step 2 (or 3 if no config needed)
        const nextBtn1 = document.getElementById('nextBtn1');
        if (nextBtn1) {
            nextBtn1.addEventListener('click', () => {
                if (!this.selectedScanType) return;

                if (this.selectedScanType.requires_config === false) {
                    // Skip to step 3 if no config needed
                    window.uiState.showStep(3);
                } else {
                    // Show configuration step
                    window.scanConfig.render(this.selectedScanType);
                    window.uiState.showStep(2);
                }
            });
        }

        // Step 2 -> Step 3 (or start scan if emails generated)
        const nextBtn2 = document.getElementById('nextBtn2');
        if (nextBtn2) {
            nextBtn2.addEventListener('click', async (e) => {
                try {
                    e.preventDefault();
                    e.stopPropagation();

                    console.log('Next button clicked in step 2');

                    // Check if button is disabled
                    if (nextBtn2.disabled) {
                        console.log('Button is disabled, ignoring click');
                        return;
                    }

                    if (!window.scanConfig.validate()) {
                        console.log('Validation failed');
                        return;
                    }

                    // Get selected scan type - try multiple ways to ensure we get it
                    let selectedScanType = this.selectedScanType;
                    if (!selectedScanType && window.app) {
                        selectedScanType = window.app.selectedScanType;
                    }
                    if (!selectedScanType) {
                        // Fallback: get from select element
                        const scanTypeSelect = document.getElementById('scanType');
                        if (scanTypeSelect && scanTypeSelect.value) {
                            selectedScanType = window.scanTypes?.find(
                                t => t.id === parseInt(scanTypeSelect.value)
                            );
                        }
                    }
                    console.log('Selected scan type:', selectedScanType);

                    if (!selectedScanType) {
                        console.error('No scan type selected');
                        window.uiState.showError('Please select a scan type');
                        return;
                    }

                    // If email-based scan with generated emails, start scan directly
                    if (selectedScanType.email_based) {
                        const emailSource = document.querySelector('input[name="emailSource"]:checked')?.value;
                        console.log('Email source:', emailSource);

                        if (emailSource === 'generate') {
                            const generatedEmails = window.emailGenerator?.getEmails() || [];
                            console.log('Generated emails count:', generatedEmails.length);

                            if (generatedEmails.length > 0) {
                                console.log('Starting scan directly from step 2');

                                // Check credentials before starting scan
                                try {
                                    const credsStatus = await window.apiClient.getCredentialsStatus();
                                    console.log('Credentials status:', credsStatus);
                                    if (!credsStatus.configured && credsStatus.required) {
                                        window.uiState.showError('AWS credentials are required. Please configure your AWS credentials before starting a scan.');
                                        return;
                                    }
                                } catch (error) {
                                    console.warn('Could not check credentials status:', error);
                                    // Continue anyway - let the server handle it
                                }

                                // Start scan directly with current/default advanced settings
                                const scanConfig = window.scanManager.collectScanConfig(selectedScanType);
                                console.log('Scan config:', scanConfig);

                                // Validate advanced settings (use defaults if not set)
                                if (!window.formValidator.validateAdvancedSettings()) {
                                    // Use default values
                                    const threadsInput = document.getElementById('threads');
                                    const awsProfileInput = document.getElementById('awsProfile');
                                    if (threadsInput && !threadsInput.value) threadsInput.value = '100';
                                    if (awsProfileInput && !awsProfileInput.value) awsProfileInput.value = 'default';
                                }

                                window.uiState.setButtonLoading('nextBtn2', true, 'Starting Scan...');

                                try {
                                    console.log('Calling scanManager.start with config:', scanConfig);
                                    await window.scanManager.start(scanConfig);
                                    console.log('Scan started successfully');
                                    // Refresh infrastructure after scan starts
                                    window.infrastructureManager.load();
                                } catch (error) {
                                    console.error('Error starting scan:', error);
                                    // Show user-friendly error message
                                    let errorMessage = error.message;
                                    if (error.status === 503 && errorMessage.includes('credentials')) {
                                        errorMessage = 'AWS credentials are required. Please configure your AWS credentials before starting a scan.';
                                    }
                                    window.uiState.showError(`Failed to start scan: ${errorMessage}`);
                                } finally {
                                    window.uiState.setButtonLoading('nextBtn2', false);
                                }
                                return;
                            } else {
                                console.log('No generated emails, proceeding to step 3');
                            }
                        } else {
                            console.log('Not using generate source, proceeding to step 3');
                        }
                    } else {
                        console.log('Not email-based scan, proceeding to step 3');
                    }

                    // Otherwise, proceed to step 3
                    console.log('Proceeding to step 3');
                    window.uiState.showStep(3);
                } catch (error) {
                    console.error('Unexpected error in nextBtn2 click handler:', error);
                    window.uiState.showError(`An unexpected error occurred: ${error.message}`);
                }
            });
        } else {
            console.error('nextBtn2 button not found in DOM');
        }

        // Back buttons
        const backBtn2 = document.getElementById('backBtn2');
        if (backBtn2) {
            backBtn2.addEventListener('click', () => {
                window.uiState.showStep(1);
            });
        }

        const backBtn3 = document.getElementById('backBtn3');
        if (backBtn3) {
            backBtn3.addEventListener('click', () => {
                if (this.selectedScanType && this.selectedScanType.requires_config === false) {
                    window.uiState.showStep(1);
                } else {
                    window.uiState.showStep(2);
                }
            });
        }

        // Add input validation listeners for step 2
        document.addEventListener('input', (e) => {
            if (window.uiState.currentStep === 2) {
                window.scanConfig.validate();
            }
        });
    }

    /**
     * Setup start scan button
     */
    setupStartScanButton() {
        const startBtn = document.getElementById('startScanBtn');
        if (!startBtn) return;

        startBtn.addEventListener('click', async () => {
            if (!this.selectedScanType) {
                window.uiState.showError('Please select a scan type');
                return;
            }

            // Check credentials before starting scan
            try {
                const credsStatus = await window.apiClient.getCredentialsStatus();
                if (!credsStatus.configured && credsStatus.required) {
                    window.uiState.showError('AWS credentials are required. Please configure your AWS credentials before starting a scan.');
                    return;
                }
            } catch (error) {
                console.warn('Could not check credentials status:', error);
                // Continue anyway - let the server handle it
            }

            // Collect configuration
            const scanConfig = window.scanManager.collectScanConfig(this.selectedScanType);

            // Validate
            if (!window.formValidator.validateAdvancedSettings()) {
                window.uiState.showError('Please complete all required fields in Advanced Settings');
                return;
            }

            // Start scan
            window.uiState.setButtonLoading('startScanBtn', true, 'Starting Scan...');

            try {
                await window.scanManager.start(scanConfig);
                // Refresh infrastructure after scan starts
                window.infrastructureManager.load();
            } catch (error) {
                console.error('Error starting scan:', error);
                // Show user-friendly error message
                let errorMessage = error.message;
                if (error.status === 503 && errorMessage.includes('credentials')) {
                    errorMessage = 'AWS credentials are required. Please configure your AWS credentials before starting a scan.';
                }
                window.uiState.showError(`Failed to start scan: ${errorMessage}`);
            } finally {
                window.uiState.setButtonLoading('startScanBtn', false);
            }
        });
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.app = new App();
    window.app.init();
});
