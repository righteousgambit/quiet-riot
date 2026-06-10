/**
 * Scan Configuration Module
 * Handles rendering and managing scan configuration forms
 */

class ScanConfig {
    constructor() {
        this.templates = {
            email: this.getEmailConfigTemplate(),
            iam: this.getIAMConfigTemplate(),
            domain: this.getDomainConfigTemplate(),
            accountId: this.getAccountIdConfigTemplate(),
        };
    }

    /**
     * Render configuration step based on scan type
     */
    render(scanType) {
        const configContent = document.getElementById('configContent');
        const step2Title = document.getElementById('step2Title');

        if (!configContent || !step2Title || !scanType) return;

        configContent.innerHTML = '';
        step2Title.textContent = 'Configuration';

        // Email-based scans
        if (scanType.email_based) {
            this.renderEmailConfig(configContent, step2Title);
        }
        // IAM-based scans
        else if (scanType.iam_based) {
            this.renderIAMConfig(configContent, step2Title);
        }
        // Microsoft 365 Domains
        else if (scanType.id === 2) {
            this.renderDomainConfig(configContent, step2Title);
        }
        // AWS Account IDs
        else if (scanType.id === 1) {
            this.renderAccountIdConfig(configContent, step2Title);
        }

        // Attach validation listener
        configContent.addEventListener('input', () => {
            this.validate();
        });
    }

    /**
     * Render email configuration
     */
    renderEmailConfig(container, title) {
        title.textContent = 'Email Configuration';
        container.innerHTML = this.templates.email;

        this.attachEmailListeners();
    }

    /**
     * Render IAM configuration
     */
    renderIAMConfig(container, title) {
        title.textContent = 'IAM Principal Configuration';
        container.innerHTML = this.templates.iam;

        this.attachIAMListeners();
    }

    /**
     * Render domain configuration
     */
    renderDomainConfig(container, title) {
        title.textContent = 'Domain Configuration';
        container.innerHTML = this.templates.domain;
    }

    /**
     * Render account ID configuration
     */
    renderAccountIdConfig(container, title) {
        title.textContent = 'Account ID Configuration';
        container.innerHTML = this.templates.accountId;

        this.attachAccountIdListeners();
    }

    /**
     * Attach email configuration listeners
     */
    attachEmailListeners() {
        // Use event delegation on configContent for all dynamic elements
        const configContent = document.getElementById('configContent');
        if (!configContent) return;

        // Radio button changes - use event delegation
        configContent.addEventListener('change', (e) => {
            if (e.target.name === 'emailSource') {
                const isCustom = e.target.value === 'custom';
                this.toggleEmailGroups(!isCustom);

                if (isCustom) {
                    window.emailGenerator.clear();
                    // Reset Next button text
                    const nextBtn2 = document.getElementById('nextBtn2');
                    if (nextBtn2) {
                        nextBtn2.textContent = 'Next →';
                    }
                }
                // Listener will be attached via click delegation below
                this.validate();
            }
        });

        // Generate button clicks - use event delegation so it works even when button is hidden/shown
        configContent.addEventListener('click', async (e) => {
            // Check if clicked element is the generate button or a child of it
            const generateBtn = e.target.id === 'generateEmailsBtn'
                ? e.target
                : e.target.closest('#generateEmailsBtn');

            if (generateBtn) {
                e.preventDefault();
                e.stopPropagation();

                // Check if button is disabled or in a hidden container
                if (generateBtn.disabled ||
                    generateBtn.classList.contains('disabled') ||
                    generateBtn.closest('.hidden')) {
                    return;
                }

                await this.handleGenerateEmails();
            }
        });
    }

    /**
     * Attach generate button listener
     * NOTE: This is now handled via event delegation in attachEmailListeners()
     * Kept for backwards compatibility but no longer needed
     */
    attachGenerateButtonListener() {
        // Event delegation is now used, so this method is not needed
        // But we keep it for any code that might call it
        return;
    }

    /**
     * Handle email generation
     */
    async handleGenerateEmails() {
        const generateBtn = document.getElementById('generateEmailsBtn');
        if (!generateBtn || generateBtn.disabled) return;

        const domain = document.getElementById('emailDomain')?.value.trim();
        const pattern = document.getElementById('emailPattern')?.value;
        const maxEmails = parseInt(document.getElementById('maxEmails')?.value) || 1000;

        if (!domain) {
            alert('Please enter a domain name');
            return;
        }

        window.uiState.setButtonLoading('generateEmailsBtn', true, 'Generating...');

        try {
            await window.emailGenerator.generate(domain, pattern, maxEmails);
            window.emailGenerator.displayPreview();
            this.setupEmailSearch();
            this.setupLoadMoreButton();
            this.validate(); // This will update the button text
        } catch (error) {
            alert('Error generating emails: ' + error.message);
        } finally {
            window.uiState.setButtonLoading('generateEmailsBtn', false);
        }
    }

    /**
     * Setup email search functionality
     */
    setupEmailSearch() {
        const searchInput = document.getElementById('emailSearch');
        const searchResults = document.getElementById('searchResults');

        if (!searchInput) return;

        // Remove old listener
        const newInput = searchInput.cloneNode(true);
        searchInput.parentNode.replaceChild(newInput, searchInput);

        document.getElementById('emailSearch').addEventListener('input', (e) => {
            const term = e.target.value.trim();
            window.emailGenerator.filter(term);

            if (searchResults) {
                const count = window.emailGenerator.filteredEmails.length;
                const total = window.emailGenerator.generatedEmails.length;
                if (term === '') {
                    searchResults.textContent = `Showing all ${total.toLocaleString()} emails`;
                } else {
                    searchResults.textContent = `${count.toLocaleString()} emails match "${term}"`;
                }
            }
        });
    }

    /**
     * Setup load more button
     */
    setupLoadMoreButton() {
        const loadMoreBtn = document.getElementById('loadMoreEmails');
        if (!loadMoreBtn) return;

        // Remove old listener
        const newBtn = loadMoreBtn.cloneNode(true);
        loadMoreBtn.parentNode.replaceChild(newBtn, loadMoreBtn);

        document.getElementById('loadMoreEmails').addEventListener('click', () => {
            window.emailGenerator.loadMore();
        });
    }

    /**
     * Toggle email configuration groups
     */
    toggleEmailGroups(showGenerate) {
        const groups = {
            custom: ['customEmailGroup'],
            generate: [
                'generateEmailGroup',
                'emailPatternGroup',
                'maxEmailsGroup',
                'generateButtonGroup',
                'emailPreviewGroup',
            ],
        };

        groups.custom.forEach(id => {
            const el = document.getElementById(id);
            if (el) el.classList.toggle('hidden', showGenerate);
        });

        groups.generate.forEach(id => {
            const el = document.getElementById(id);
            if (el) {
                el.classList.toggle('hidden', !showGenerate);
                // Event delegation handles button clicks, so no need to re-attach listeners
            }
        });
    }

    /**
     * Attach IAM configuration listeners
     */
    attachIAMListeners() {
        document.querySelectorAll('input[name="iamSource"]').forEach(radio => {
            radio.addEventListener('change', (e) => {
                const isCustom = e.target.value === 'custom';
                const customGroup = document.getElementById('customIamGroup');
                if (customGroup) {
                    customGroup.classList.toggle('hidden', !isCustom);
                }
                this.validate();
            });
        });
    }

    /**
     * Attach account ID configuration listeners
     */
    attachAccountIdListeners() {
        document.querySelectorAll('input[name="accountIdSource"]').forEach(radio => {
            radio.addEventListener('change', (e) => {
                const isCustom = e.target.value === 'custom';
                const customGroup = document.getElementById('customAccountIdGroup');
                const generateGroup = document.getElementById('generateAccountIdGroup');

                if (customGroup) customGroup.classList.toggle('hidden', !isCustom);
                if (generateGroup) generateGroup.classList.toggle('hidden', isCustom);

                this.validate();
            });
        });
    }

    /**
     * Validate current configuration
     */
    validate() {
        const scanTypeSelect = document.getElementById('scanType');
        if (!scanTypeSelect) return false;

        const selectedOption = scanTypeSelect.options[scanTypeSelect.selectedIndex];
        if (!selectedOption || !selectedOption.value) return false;

        // Find scan type from window.scanTypes
        const scanType = window.scanTypes?.find(
            t => t.id === parseInt(selectedOption.value)
        );

        if (!scanType) return false;

        const isValid = window.formValidator.validateConfigStep(scanType);
        const nextBtn = document.getElementById('nextBtn2');
        if (nextBtn) {
            nextBtn.disabled = !isValid;

            // Update button text for email-based scans with generated emails
            if (isValid && scanType.email_based) {
                const emailSource = document.querySelector('input[name="emailSource"]:checked')?.value;
                if (emailSource === 'generate') {
                    const generatedEmails = window.emailGenerator?.getEmails() || [];
                    if (generatedEmails.length > 0) {
                        nextBtn.textContent = 'Next → Start Scan';
                    } else {
                        nextBtn.textContent = 'Next →';
                    }
                } else {
                    nextBtn.textContent = 'Next →';
                }
            } else {
                nextBtn.textContent = 'Next →';
            }
        }
        return isValid;
    }

    /**
     * Collect configuration data
     */
    collectConfig(scanType) {
        const config = {};

        if (scanType.email_based) {
            const emailSource = document.querySelector('input[name="emailSource"]:checked')?.value;
            if (emailSource === 'custom') {
                const emailList = document.getElementById('emailList');
                if (emailList) {
                    config.email_list = emailList.value
                        .split('\n')
                        .map(e => e.trim())
                        .filter(e => e);
                }
            } else {
                config.email_list = window.emailGenerator.getEmails();
            }
        } else if (scanType.iam_based) {
            const iamSource = document.querySelector('input[name="iamSource"]:checked')?.value;
            if (iamSource === 'custom') {
                const iamList = document.getElementById('iamList');
                if (iamList) {
                    config.iam_list = iamList.value
                        .split('\n')
                        .map(a => a.trim())
                        .filter(a => a);
                }
            } else {
                config.use_vendor_principals = true;
            }
        } else if (scanType.id === 2) {
            const domainList = document.getElementById('domainList');
            if (domainList) {
                config.domain_list = domainList.value
                    .split('\n')
                    .map(d => d.trim())
                    .filter(d => d);
            }
        } else if (scanType.id === 1) {
            const accountIdSource = document.querySelector('input[name="accountIdSource"]:checked')?.value;
            if (accountIdSource === 'custom') {
                const accountIdList = document.getElementById('accountIdList');
                if (accountIdList) {
                    config.account_id_list = accountIdList.value
                        .split('\n')
                        .map(a => a.trim())
                        .filter(a => a);
                }
            } else {
                const countInput = document.getElementById('accountIdCount');
                config.generate_account_ids = true;
                config.account_id_count = parseInt(countInput?.value) || 1000;
            }
        }

        return config;
    }

    // Template getters (HTML strings)
    getEmailConfigTemplate() {
        return `
            <div class="form-group">
                <label>Email Source</label>
                <div class="radio-group">
                    <div class="radio-option">
                        <input type="radio" name="emailSource" id="emailSourceCustom" value="custom" checked>
                        <label for="emailSourceCustom" class="radio-label">Supply My Own Emails</label>
                        <div class="radio-description">Provide a list of email addresses</div>
                    </div>
                    <div class="radio-option">
                        <input type="radio" name="emailSource" id="emailSourceGenerate" value="generate">
                        <label for="emailSourceGenerate" class="radio-label">Generate from Pattern</label>
                        <div class="radio-description">Generate emails from domain and name patterns</div>
                    </div>
                </div>
            </div>
            <div class="form-group" id="customEmailGroup">
                <label for="emailList">Email Addresses (one per line)</label>
                <textarea id="emailList" name="email_list" placeholder="user1@example.com&#10;user2@example.com&#10;user3@example.com"></textarea>
                <div class="form-help">Enter email addresses, one per line</div>
            </div>
            <div class="form-group hidden" id="generateEmailGroup">
                <label for="emailDomain">Domain</label>
                <input type="text" id="emailDomain" name="email_domain" placeholder="example.com">
                <div class="form-help">Domain name for email generation</div>
            </div>
            <div class="form-group hidden" id="emailPatternGroup">
                <label for="emailPattern">Email Pattern</label>
                <select id="emailPattern" name="email_pattern">
                    <option value="firstname.lastname">firstname.lastname@domain.com</option>
                    <option value="firstnamelastname">firstnamelastname@domain.com</option>
                    <option value="firstname_lastname">firstname_lastname@domain.com</option>
                    <option value="f.lastname">f.lastname@domain.com (first initial)</option>
                    <option value="firstname.l">firstname.l@domain.com (last initial)</option>
                    <option value="flastname">flastname@domain.com (first initial + lastname)</option>
                    <option value="firstname">firstname@domain.com</option>
                    <option value="lastname">lastname@domain.com</option>
                    <option value="firstinitial.lastname">firstinitial.lastname@domain.com</option>
                    <option value="firstname.lastinitial">firstname.lastinitial@domain.com</option>
                </select>
                <div class="form-help">Select the email naming pattern to use</div>
            </div>
            <div class="form-group hidden" id="maxEmailsGroup">
                <label for="maxEmails">Maximum Emails to Generate</label>
                <input type="number" id="maxEmails" name="max_emails" value="1000" min="1" max="20000000">
                <div class="form-help">Maximum number of email addresses to generate (1-20,000,000)</div>
            </div>
            <div class="form-group hidden" id="generateButtonGroup">
                <button type="button" class="btn-secondary" id="generateEmailsBtn">Generate Email List</button>
            </div>
            <div class="form-group hidden" id="emailPreviewGroup">
                <label>Generated Email List Preview</label>
                <div class="form-group" style="margin-bottom: 12px;">
                    <input type="text" id="emailSearch" placeholder="Search emails..." style="width: 100%; padding: 8px 12px; border: 2px solid #e0e0e0; border-radius: 6px; font-size: 14px;">
                    <div class="form-help" style="margin-top: 4px; font-size: 0.85em;" id="searchResults">Type to filter emails...</div>
                </div>
                <div id="emailPreview" style="max-height: 400px; overflow-y: auto; background: #f8f9fa; padding: 16px; border-radius: 8px; border: 1px solid #e0e0e0; font-family: 'Monaco', 'Menlo', 'Courier New', monospace; font-size: 12px; line-height: 1.6;">
                    <div style="color: #666; margin-bottom: 8px;">No emails generated yet. Click "Generate Email List" to preview.</div>
                </div>
                <div style="margin-top: 12px; text-align: center;">
                    <button type="button" class="btn-secondary" id="loadMoreEmails" style="display: none; padding: 10px 20px; font-size: 14px;">Load More</button>
                </div>
                <div class="form-help" id="emailCount">0 emails generated</div>
            </div>
        `;
    }

    getIAMConfigTemplate() {
        return `
            <div class="form-group">
                <label>Principal Source</label>
                <div class="radio-group">
                    <div class="radio-option">
                        <input type="radio" name="iamSource" id="iamSourceCustom" value="custom" checked>
                        <label for="iamSourceCustom" class="radio-label">Supply My Own ARNs</label>
                        <div class="radio-description">Provide a list of IAM principal ARNs</div>
                    </div>
                    <div class="radio-option">
                        <input type="radio" name="iamSource" id="iamSourceVendor" value="vendor">
                        <label for="iamSourceVendor" class="radio-label">Common Third-Party Vendor Principals</label>
                        <div class="radio-description">Use built-in list of common vendor ARNs</div>
                    </div>
                </div>
            </div>
            <div class="form-group" id="customIamGroup">
                <label for="iamList">IAM Principal ARNs (one per line)</label>
                <textarea id="iamList" name="iam_list" placeholder="arn:aws:iam::123456789012:role/ExampleRole&#10;arn:aws:iam::123456789012:user/ExampleUser"></textarea>
                <div class="form-help">Enter IAM principal ARNs, one per line</div>
            </div>
        `;
    }

    getDomainConfigTemplate() {
        return `
            <div class="form-group">
                <label for="domainList">Microsoft 365 Domains (one per line)</label>
                <textarea id="domainList" name="domain_list" placeholder="example.com&#10;company.org&#10;test.net" required></textarea>
                <div class="form-help">Enter domain names to check, one per line</div>
            </div>
        `;
    }

    getAccountIdConfigTemplate() {
        return `
            <div class="form-group">
                <label>Account ID Source</label>
                <div class="radio-group">
                    <div class="radio-option">
                        <input type="radio" name="accountIdSource" id="accountIdSourceCustom" value="custom" checked>
                        <label for="accountIdSourceCustom" class="radio-label">Supply My Own Account IDs</label>
                        <div class="radio-description">Provide a list of 12-digit account IDs</div>
                    </div>
                    <div class="radio-option">
                        <input type="radio" name="accountIdSource" id="accountIdSourceGenerate" value="generate">
                        <label for="accountIdSourceGenerate" class="radio-label">Generate Programmatically</label>
                        <div class="radio-description">Automatically generate account IDs to test</div>
                    </div>
                </div>
            </div>
            <div class="form-group" id="customAccountIdGroup">
                <label for="accountIdList">AWS Account IDs (one per line, 12 digits each)</label>
                <textarea id="accountIdList" name="account_id_list" placeholder="123456789012&#10;987654321098&#10;111222333444"></textarea>
                <div class="form-help">Enter 12-digit AWS account IDs, one per line</div>
            </div>
            <div class="form-group hidden" id="generateAccountIdGroup">
                <label for="accountIdCount">Number of Account IDs to Generate</label>
                <input type="number" id="accountIdCount" name="account_id_count" value="1000" min="1" max="100000">
                <div class="form-help">Number of random 12-digit account IDs to generate and test</div>
            </div>
        `;
    }
}

// Export singleton instance
window.scanConfig = new ScanConfig();
