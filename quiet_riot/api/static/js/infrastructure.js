/**
 * Infrastructure Management Module
 * Handles infrastructure resource display and cleanup
 */

class InfrastructureManager {
    /**
     * Load and display infrastructure status
     */
    async load() {
        const content = document.getElementById('infrastructureContent');
        if (!content) return;

        // Show loading state
        content.innerHTML = `
            <div style="text-align: center; padding: 20px; color: #666;">
                <div class="loading" style="margin: 0 auto 10px;"></div>
                Loading infrastructure status...
            </div>
        `;

        try {
            const data = await window.apiClient.getInfrastructure();
            this.render(data, content);
        } catch (error) {
            console.error('Error loading infrastructure:', error);
            content.innerHTML = `
                <div style="text-align: center; padding: 20px; color: #dc3545;">
                    Error loading infrastructure status: ${error.message}
                </div>
            `;
        }
    }

    /**
     * Render infrastructure data
     */
    render(data, container) {
        if (data.current_resources && data.current_resources.length > 0) {
            container.innerHTML = this.renderCurrentResources(data.current_resources) +
                                  this.renderHistoricalResources(data.historical_resources);
        } else {
            container.innerHTML = this.renderEmptyState();
        }
    }

    /**
     * Render current resources
     */
    renderCurrentResources(resources) {
        let html = '<div style="margin-bottom: 20px;"><h3 style="color: #333; margin-bottom: 16px;">Current Resources</h3>';
        html += '<div style="display: grid; gap: 12px;">';

        resources.forEach(resource => {
            html += `
                <div style="background: #f8f9fa; padding: 16px; border-radius: 8px; border-left: 4px solid #28a745;">
                    <div style="font-weight: 600; color: #333; margin-bottom: 4px;">${resource.type}</div>
                    <div style="font-family: 'Monaco', 'Menlo', 'Courier New', monospace; font-size: 12px; color: #666;">
                        ${resource.name || resource.arn || resource.id || 'N/A'}
                    </div>
                    <div style="margin-top: 8px;">
                        <span style="background: #28a745; color: white; padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: 600;">${resource.status}</span>
                    </div>
                </div>
            `;
        });

        html += '</div></div>';
        return html;
    }

    /**
     * Render historical resources
     */
    renderHistoricalResources(historical) {
        if (!historical || historical.length === 0) {
            return '';
        }

        let html = '<div><h3 style="color: #333; margin-bottom: 16px;">Historical Resources</h3>';
        html += '<div style="display: grid; gap: 12px;">';

        historical.forEach(hist => {
            html += `
                <div style="background: #fff3cd; padding: 16px; border-radius: 8px; border-left: 4px solid #ffc107;">
                    <div style="font-weight: 600; color: #333; margin-bottom: 8px;">
                        Scan: ${hist.scan_type || 'Unknown'} (${hist.scan_id?.substring(0, 8)}...)
                    </div>
                    <div style="font-size: 12px; color: #666; margin-bottom: 12px;">
                        Created: ${new Date(hist.created_at).toLocaleString()}
                    </div>
                    <div style="display: grid; gap: 8px; font-size: 11px;">
                        ${hist.resources.ecr_public_repo ? `<div><strong>ECR Public:</strong> ${hist.resources.ecr_public_repo}</div>` : ''}
                        ${hist.resources.ecr_private_repo ? `<div><strong>ECR Private:</strong> ${hist.resources.ecr_private_repo}</div>` : ''}
                        ${hist.resources.sns_topic_arn ? `<div><strong>SNS Topic:</strong> ${hist.resources.sns_topic_arn}</div>` : ''}
                        ${hist.resources.s3_bucket ? `<div><strong>S3 Bucket:</strong> ${hist.resources.s3_bucket}</div>` : ''}
                    </div>
                </div>
            `;
        });

        html += '</div></div>';
        return html;
    }

    /**
     * Render empty state
     */
    renderEmptyState() {
        return `
            <div style="text-align: center; padding: 40px; color: #666;">
                <div style="font-size: 48px; margin-bottom: 16px;">☁️</div>
                <div style="font-size: 18px; font-weight: 600; margin-bottom: 8px; color: #333;">No Active Infrastructure</div>
                <div>No AWS resources are currently active. Resources will be created when you start a scan.</div>
            </div>
        `;
    }

    /**
     * Cleanup all infrastructure
     */
    async cleanup() {
        if (!confirm('Are you sure you want to clean up all AWS infrastructure resources? This cannot be undone.')) {
            return;
        }

        const btn = document.getElementById('cleanupInfrastructure');
        if (!btn) return;

        const originalText = btn.textContent;
        btn.disabled = true;
        btn.textContent = 'Cleaning up...';

        try {
            const data = await window.apiClient.cleanupInfrastructure();
            alert(data.message || 'Infrastructure cleaned up successfully');
            await this.load();
        } catch (error) {
            alert('Error cleaning up infrastructure: ' + error.message);
        } finally {
            btn.disabled = false;
            btn.textContent = originalText;
        }
    }

    /**
     * Setup event listeners
     */
    setupListeners() {
        const refreshBtn = document.getElementById('refreshInfrastructure');
        const cleanupBtn = document.getElementById('cleanupInfrastructure');

        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.load());
        }

        if (cleanupBtn) {
            cleanupBtn.addEventListener('click', () => this.cleanup());
        }
    }

    /**
     * Start auto-refresh
     */
    startAutoRefresh(intervalMs = 30000) {
        setInterval(() => this.load(), intervalMs);
    }
}

// Export singleton instance
window.infrastructureManager = new InfrastructureManager();
