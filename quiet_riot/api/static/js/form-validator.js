/**
 * Form Validation Module
 * Handles form validation logic
 */

class FormValidator {
    /**
     * Validate configuration step based on scan type
     */
    validateConfigStep(scanType) {
        if (!scanType || scanType.requires_config === false) {
            return true;
        }

        // Email-based validation
        if (scanType.email_based) {
            return this.validateEmailConfig();
        }

        // IAM-based validation
        if (scanType.iam_based) {
            return this.validateIAMConfig();
        }

        // Domain validation (Microsoft 365 Domains)
        if (scanType.id === 2) {
            return this.validateDomainConfig();
        }

        // Account ID validation
        if (scanType.id === 1) {
            return this.validateAccountIdConfig();
        }

        return false;
    }

    /**
     * Validate email configuration
     */
    validateEmailConfig() {
        const emailSource = document.querySelector('input[name="emailSource"]:checked')?.value;

        if (emailSource === 'custom') {
            const emailList = document.getElementById('emailList');
            if (!emailList) return false;
            return emailList.value.trim().length > 0;
        } else {
            // Generate source - need domain and generated emails
            const domain = document.getElementById('emailDomain')?.value.trim();
            const generatedEmails = window.emailGenerator?.getEmails() || [];
            const hasGeneratedEmails = generatedEmails.length > 0;
            return domain && domain.length > 0 && hasGeneratedEmails;
        }
    }

    /**
     * Validate IAM configuration
     */
    validateIAMConfig() {
        const iamSource = document.querySelector('input[name="iamSource"]:checked')?.value;

        if (iamSource === 'custom') {
            const iamList = document.getElementById('iamList');
            if (!iamList) return false;
            return iamList.value.trim().length > 0;
        } else {
            // Vendor list is always valid
            return true;
        }
    }

    /**
     * Validate domain configuration
     */
    validateDomainConfig() {
        const domainList = document.getElementById('domainList');
        if (!domainList) return false;
        return domainList.value.trim().length > 0;
    }

    /**
     * Validate account ID configuration
     */
    validateAccountIdConfig() {
        const accountIdSource = document.querySelector('input[name="accountIdSource"]:checked')?.value;

        if (accountIdSource === 'custom') {
            const accountIdList = document.getElementById('accountIdList');
            if (!accountIdList) return false;
            return accountIdList.value.trim().length > 0;
        } else {
            // Generation is always valid
            return true;
        }
    }

    /**
     * Validate advanced settings step
     */
    validateAdvancedSettings() {
        const threads = document.getElementById('threads');
        const awsProfile = document.getElementById('awsProfile');

        if (!threads || !awsProfile) return false;

        const threadsValue = parseInt(threads.value);
        if (isNaN(threadsValue) || threadsValue < 1 || threadsValue > 1000) {
            return false;
        }

        return awsProfile.value.trim().length > 0;
    }

    /**
     * Get validation error message
     */
    getValidationError(scanType) {
        if (!scanType || scanType.requires_config === false) {
            return null;
        }

        if (scanType.email_based) {
            const emailSource = document.querySelector('input[name="emailSource"]:checked')?.value;
            if (emailSource === 'custom') {
                return 'Please provide at least one email address';
            } else {
                return 'Please enter a domain and generate the email list';
            }
        }

        if (scanType.iam_based) {
            return 'Please provide at least one IAM principal ARN';
        }

        if (scanType.id === 2) {
            return 'Please provide at least one domain name';
        }

        if (scanType.id === 1) {
            return 'Please provide at least one account ID or enable generation';
        }

        return 'Please complete all required fields';
    }
}

// Export singleton instance
window.formValidator = new FormValidator();
