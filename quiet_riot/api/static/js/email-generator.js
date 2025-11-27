/**
 * Email Generator Module
 * Handles email generation, preview, and search functionality
 */

class EmailGenerator {
    constructor() {
        this.generatedEmails = [];
        this.filteredEmails = [];
        this.displayedEmailCount = 0;
        this.emailsPerPage = 100;
    }

    /**
     * Generate emails using API
     */
    async generate(domain, pattern, maxEmails) {
        if (!domain || !domain.trim()) {
            throw new Error('Please enter a domain name');
        }

        const data = await window.apiClient.generateEmails(domain.trim(), pattern, maxEmails);
        this.generatedEmails = data.emails || [];
        this.filteredEmails = this.generatedEmails;
        this.displayedEmailCount = 0;
        return this.generatedEmails;
    }

    /**
     * Display email preview with pagination
     */
    displayPreview() {
        const preview = document.getElementById('emailPreview');
        const emailCount = document.getElementById('emailCount');
        const loadMoreBtn = document.getElementById('loadMoreEmails');

        if (!preview || !emailCount) return;

        const nextBatch = this.filteredEmails.slice(
            this.displayedEmailCount,
            this.displayedEmailCount + this.emailsPerPage
        );

        if (nextBatch.length === 0) {
            if (this.displayedEmailCount === 0) {
                preview.innerHTML = '<div style="color: #666;">No emails match your search.</div>';
            }
            if (loadMoreBtn) loadMoreBtn.style.display = 'none';
            return;
        }

        // Append to preview
        if (this.displayedEmailCount === 0) {
            preview.innerHTML = `<pre style="margin: 0; white-space: pre-wrap; word-wrap: break-word;">${nextBatch.join('\n')}</pre>`;
        } else {
            const pre = preview.querySelector('pre');
            if (pre) {
                pre.textContent += '\n' + nextBatch.join('\n');
            }
        }

        this.displayedEmailCount += nextBatch.length;

        // Update count and show/hide load more button
        const showing = Math.min(this.displayedEmailCount, this.filteredEmails.length);
        emailCount.textContent = `Showing ${showing.toLocaleString()} of ${this.filteredEmails.length.toLocaleString()} emails (${this.generatedEmails.length.toLocaleString()} total generated)`;

        if (loadMoreBtn) {
            loadMoreBtn.style.display = showing < this.filteredEmails.length ? 'inline-block' : 'none';
        }
    }

    /**
     * Filter emails by search term
     */
    filter(searchTerm) {
        const term = searchTerm.toLowerCase().trim();
        if (term === '') {
            this.filteredEmails = this.generatedEmails;
        } else {
            this.filteredEmails = this.generatedEmails.filter(email =>
                email.toLowerCase().includes(term)
            );
        }
        this.displayedEmailCount = 0;
        this.displayPreview();
    }

    /**
     * Load more emails
     */
    loadMore() {
        this.displayPreview();
        // Scroll to bottom
        const preview = document.getElementById('emailPreview');
        if (preview) {
            preview.scrollTop = preview.scrollHeight;
        }
    }

    /**
     * Clear generated emails
     */
    clear() {
        this.generatedEmails = [];
        this.filteredEmails = [];
        this.displayedEmailCount = 0;
    }

    /**
     * Get all generated emails
     */
    getEmails() {
        return this.generatedEmails;
    }
}

// Export singleton instance
window.emailGenerator = new EmailGenerator();
