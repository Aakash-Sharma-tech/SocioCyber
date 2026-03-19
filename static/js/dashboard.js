// Dashboard JavaScript - AI Campaign Detection System

class DashboardManager {
    constructor() {
        this.charts = {};
        this.isLoading = false;
        this.autoRefreshInterval = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadDashboardData();
        this.setupAutoRefresh();
        this.animateCounters();
    }

    setupEventListeners() {
        // Collect data button
        const collectBtn = document.getElementById('collectDataBtn');
        if (collectBtn) {
            collectBtn.addEventListener('click', () => this.collectNewData());
        }

        // Refresh button
        const refreshBtn = document.getElementById('refreshBtn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.refreshDashboard());
        }

        // View all activity button
        const viewAllBtn = document.getElementById('viewAllActivity');
        if (viewAllBtn) {
            viewAllBtn.addEventListener('click', () => this.viewAllActivity());
        }

        // Chart download buttons
        document.addEventListener('click', (e) => {
            if (e.target.closest('[onclick*="downloadChart"]')) {
                const chartId = e.target.closest('[onclick*="downloadChart"]').onclick.toString().match(/'([^']+)'/)[1];
                this.downloadChart(chartId);
            }
        });
    }

    async loadDashboardData() {
        if (this.isLoading) return;
        
        this.isLoading = true;
        this.showLoadingState();

        try {
            const response = await fetch('/api/dashboard-stats');
            if (!response.ok) throw new Error('Failed to fetch dashboard data');
            
            const data = await response.json();
            this.updateStats(data);
            this.createCharts(data);
            this.updateThreatLevel(data);

            // Load recent posts/activity feed in parallel
            this.loadRecentActivity();
        } catch (error) {
            console.error('Error loading dashboard data:', error);
            this.showError('Failed to load dashboard data');
        } finally {
            this.isLoading = false;
            this.hideLoadingState();
        }
    }

    async loadRecentActivity() {
        try {
            const resp = await fetch('/api/recent-posts?limit=15');
            if (!resp.ok) throw new Error('Failed to fetch recent posts');
            const items = await resp.json();
            const container = document.getElementById('activityFeed');
            if (!container) return;
            container.innerHTML = '';
            items.forEach(item => {
                const score = (item.analysis?.propaganda ?? 0).toFixed(2);
                const scoreClass = (item.analysis?.propaganda ?? 0) > 0.7 ? 'danger' : 'success';
                const icon = item.platform === 'Twitter' ? 'fab fa-twitter' : (item.platform === 'Reddit' ? 'fab fa-reddit' : 'fas fa-newspaper');
                const time = this.formatRelativeTime(new Date(item.timestamp));
                const el = document.createElement('div');
                el.className = 'activity-item';
                el.innerHTML = `
                    <div class="activity-icon">
                        <i class="${icon}"></i>
                    </div>
                    <div class="activity-content">
                        <div class="activity-title">${this.escapeHtml(item.content.slice(0, 120))}${item.content.length > 120 ? '…' : ''}</div>
                        <div class="activity-meta">${item.platform} • ${time}</div>
                    </div>
                    <div class="activity-score ${scoreClass}">${score}</div>
                `;
                el.addEventListener('click', () => {
                    if (item.url) window.open(item.url, '_blank');
                });
                container.appendChild(el);
            });
        } catch (e) {
            console.error('Activity load error', e);
        }
    }

    formatRelativeTime(date) {
        const diff = (Date.now() - date.getTime()) / 1000;
        if (diff < 60) return `${Math.floor(diff)}s ago`;
        if (diff < 3600) return `${Math.floor(diff/60)}m ago`;
        if (diff < 86400) return `${Math.floor(diff/3600)}h ago`;
        return `${Math.floor(diff/86400)}d ago`;
    }

    escapeHtml(str) {
        return str.replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
    }

    updateStats(data) {
        // Update stat cards with animation
        const stats = [
            { id: 'totalPosts', value: data.total_posts },
            { id: 'propagandaPercentage', value: `${data.propaganda_percentage}%` },
            { id: 'negativeSentiment', value: `${data.negative_sentiment}%` },
            { id: 'suspiciousPosts', value: data.suspicious_posts }
        ];

        stats.forEach(stat => {
            const element = document.getElementById(stat.id);
            if (element) {
                this.animateValue(element, stat.value);
            }
        });

        // Update change indicators
        this.updateChangeIndicators(data);
    }

    animateValue(element, targetValue) {
        const isNumber = typeof targetValue === 'number';
        const isPercentage = typeof targetValue === 'string' && targetValue.includes('%');
        
        let startValue = 0;
        const endValue = isNumber ? targetValue : parseInt(targetValue);
        const duration = 2000;
        const increment = endValue / (duration / 16);

        const timer = setInterval(() => {
            startValue += increment;
            if (startValue >= endValue) {
                startValue = endValue;
                clearInterval(timer);
            }

            if (isPercentage) {
                element.textContent = Math.floor(startValue) + '%';
            } else if (isNumber) {
                element.textContent = Math.floor(startValue);
            } else {
                element.textContent = targetValue;
            }
        }, 16);
    }

    updateChangeIndicators(data) {
        // Update change percentages (in a real app, this would come from historical data)
        const changes = {
            'postsChange': '+12%',
            'propagandaChange': '+5%',
            'sentimentChange': '+8%',
            'suspiciousChange': '-3%'
        };

        Object.entries(changes).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = value;
                element.className = `stat-change ${value.startsWith('-') ? 'positive' : 'negative'}`;
            }
        });
    }

    createCharts(data) {
        this.createSentimentChart(data.sentiment_distribution);
        this.createPlatformChart(data.platform_activity);
        this.createThreatChart(data);
    }

    createSentimentChart(sentimentData) {
        const ctx = document.getElementById('sentimentChart');
        if (!ctx) return;

        const isLight = document.body.classList.contains('light-mode');
        const textColor = isLight ? '#1a202c' : '#F7FAFC';
        const gridColor = isLight ? 'rgba(0,0,0,0.1)' : 'rgba(255, 255, 255, 0.1)';
        const tooltipBg = isLight ? 'rgba(255,255,255,0.95)' : 'rgba(26, 32, 44, 0.9)';
        const tooltipTitle = isLight ? '#1a202c' : '#F7FAFC';
        const tooltipBody = isLight ? '#2d3748' : '#E2E8F0';
        const tooltipBorder = isLight ? 'rgba(0,0,0,0.1)' : 'rgba(255, 255, 255, 0.1)';

        if (this.charts.sentiment) {
            this.charts.sentiment.destroy();
        }

        this.charts.sentiment = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Positive', 'Neutral', 'Negative'],
                datasets: [{
                    data: [
                        sentimentData.positive || 0,
                        sentimentData.neutral || 0,
                        sentimentData.negative || 0
                    ],
                    backgroundColor: [
                        'rgba(16, 185, 129, 0.8)',
                        'rgba(245, 158, 11, 0.8)',
                        'rgba(239, 68, 68, 0.8)'
                    ],
                    borderColor: [
                        'rgba(16, 185, 129, 1)',
                        'rgba(245, 158, 11, 1)',
                        'rgba(239, 68, 68, 1)'
                    ],
                    borderWidth: 2,
                    hoverOffset: 10
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: textColor,
                            padding: 20,
                            usePointStyle: true,
                            pointStyle: 'circle'
                        }
                    },
                    tooltip: {
                        backgroundColor: tooltipBg,
                        titleColor: tooltipTitle,
                        bodyColor: tooltipBody,
                        borderColor: tooltipBorder,
                        borderWidth: 1,
                        cornerRadius: 8,
                        displayColors: true
                    }
                },
                animation: {
                    animateScale: true,
                    animateRotate: true,
                    duration: 1000,
                    easing: 'easeOutBounce'
                }
            }
        });
    }

    createPlatformChart(platformData) {
        const ctx = document.getElementById('platformChart');
        if (!ctx) return;

        const isLight = document.body.classList.contains('light-mode');
        const textColor = isLight ? '#1a202c' : '#F7FAFC';
        const gridColor = isLight ? 'rgba(0,0,0,0.1)' : 'rgba(255, 255, 255, 0.1)';
        const tooltipBg = isLight ? 'rgba(255,255,255,0.95)' : 'rgba(26, 32, 44, 0.9)';
        const tooltipTitle = isLight ? '#1a202c' : '#F7FAFC';
        const tooltipBody = isLight ? '#2d3748' : '#E2E8F0';
        const tooltipBorder = isLight ? 'rgba(0,0,0,0.1)' : 'rgba(255, 255, 255, 0.1)';

        if (this.charts.platform) {
            this.charts.platform.destroy();
        }

        this.charts.platform = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Twitter', 'Reddit', 'News'],
                datasets: [{
                    label: 'Posts',
                    data: [
                        platformData.Twitter || 0,
                        platformData.Reddit || 0,
                        platformData.News || 0
                    ],
                    backgroundColor: [
                        'rgba(29, 161, 242, 0.8)',
                        'rgba(255, 69, 0, 0.8)',
                        'rgba(0, 209, 0, 0.8)'
                    ],
                    borderColor: [
                        'rgba(29, 161, 242, 1)',
                        'rgba(255, 69, 0, 1)',
                        'rgba(0, 209, 0, 1)'
                    ],
                    borderWidth: 2,
                    borderRadius: 8,
                    borderSkipped: false,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: tooltipBg,
                        titleColor: tooltipTitle,
                        bodyColor: tooltipBody,
                        borderColor: tooltipBorder,
                        borderWidth: 1,
                        cornerRadius: 8
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: gridColor
                        },
                        ticks: {
                            color: textColor
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            color: textColor
                        }
                    }
                },
                animation: {
                    duration: 1000,
                    easing: 'easeOutQuart'
                },
                interaction: {
                    intersect: false,
                    mode: 'index'
                }
            }
        });
    }

    createThreatChart(data) {
        const ctx = document.getElementById('threatChart');
        if (!ctx) return;

        if (this.charts.threat) {
            this.charts.threat.destroy();
        }

        // Generate sample threat timeline data
        const hours = [];
        const threatLevels = [];
        const now = new Date();
        
        for (let i = 23; i >= 0; i--) {
            const time = new Date(now.getTime() - (i * 60 * 60 * 1000));
            hours.push(time.getHours() + ':00');
            // Simulate threat level with some peaks
            let threat = Math.sin(i * 0.3) * 0.3 + 0.5;
            if (i < 5) threat += 0.3; // Recent spike
            threatLevels.push(Math.max(0, Math.min(1, threat + (Math.random() - 0.5) * 0.2)));
        }

        this.charts.threat = new Chart(ctx, {
            type: 'line',
            data: {
                labels: hours,
                datasets: [{
                    label: 'Threat Level',
                    data: threatLevels,
                    borderColor: 'rgba(245, 158, 11, 1)',
                    backgroundColor: 'rgba(245, 158, 11, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: 'rgba(245, 158, 11, 1)',
                    pointBorderColor: '#FFFFFF',
                    pointBorderWidth: 2,
                    pointRadius: 5,
                    pointHoverRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: 'rgba(26, 32, 44, 0.9)',
                        titleColor: '#F7FAFC',
                        bodyColor: '#E2E8F0',
                        borderColor: 'rgba(255, 255, 255, 0.1)',
                        borderWidth: 1,
                        cornerRadius: 8,
                        callbacks: {
                            label: function(context) {
                                return `Threat Level: ${(context.parsed.y * 100).toFixed(1)}%`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 1,
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        ticks: {
                            color: '#A0AEC0',
                            callback: function(value) {
                                return (value * 100).toFixed(0) + '%';
                            }
                        }
                    },
                    x: {
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        ticks: {
                            color: '#A0AEC0'
                        }
                    }
                },
                animation: {
                    duration: 2000,
                    easing: 'easeInOutQuart'
                }
            }
        });
    }

    updateThreatLevel(data) {
        const threatElement = document.getElementById('threatLevel');
        if (!threatElement) return;

        let level = 'LOW';
        let className = 'low';

        if (data.propaganda_percentage > 50) {
            level = 'HIGH';
            className = 'high';
        } else if (data.propaganda_percentage > 25) {
            level = 'MEDIUM';
            className = 'medium';
        }

        threatElement.textContent = level;
        threatElement.className = `threat-level ${className}`;
    }

    async collectNewData() {
        const collectBtn = document.getElementById('collectDataBtn');
        if (!collectBtn || this.isLoading) return;

        const originalText = collectBtn.innerHTML;
        collectBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Collecting...';
        collectBtn.disabled = true;

        try {
            const response = await fetch('/api/collect-data', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ query: 'anti-india propaganda' })
            });

            if (!response.ok) throw new Error('Failed to collect data');

            const result = await response.json();
            
            if (result.success) {
                this.showAlert(`Successfully collected ${result.posts_collected} posts. ${result.high_risk_posts} high-risk posts detected.`, 'success');
                await this.loadDashboardData(); // Refresh dashboard
            } else {
                throw new Error(result.error || 'Unknown error occurred');
            }
        } catch (error) {
            console.error('Error collecting data:', error);
            this.showAlert('Failed to collect new data: ' + error.message, 'error');
        } finally {
            collectBtn.innerHTML = originalText;
            collectBtn.disabled = false;
        }
    }

    async refreshDashboard() {
        this.showAlert('Refreshing dashboard data...', 'info');
        await this.loadDashboardData();
        this.showAlert('Dashboard refreshed successfully!', 'success');
    }

    viewAllActivity() {
        // Navigate to the History page where full activity/flagged posts are shown
        window.location.href = '/history#flaggedFeed';
    }

    downloadChart(chartId) {
        const chart = this.charts[chartId.replace('Chart', '')];
        if (!chart) {
            this.showAlert('Chart not found', 'error');
            return;
        }

        try {
            const url = chart.toBase64Image();
            const link = document.createElement('a');
            link.download = `${chartId}-${new Date().toISOString().split('T')[0]}.png`;
            link.href = url;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            this.showAlert('Chart downloaded successfully!', 'success');
        } catch (error) {
            console.error('Error downloading chart:', error);
            this.showAlert('Failed to download chart', 'error');
        }
    }

    setupAutoRefresh() {
        // Auto-refresh every 5 minutes
        this.autoRefreshInterval = setInterval(() => {
            this.loadDashboardData();
        }, 5 * 60 * 1000);
    }

    animateCounters() {
        // Animate stat counters on page load
        const counters = document.querySelectorAll('.stat-number');
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const target = entry.target;
                    const text = target.textContent;
                    if (text && !isNaN(parseInt(text))) {
                        this.animateValue(target, text);
                    }
                    observer.unobserve(target);
                }
            });
        }, { threshold: 0.5 });

        counters.forEach(counter => observer.observe(counter));
    }

    showLoadingState() {
        const loadingElements = document.querySelectorAll('.chart-container');
        loadingElements.forEach(el => {
            el.style.opacity = '0.6';
            el.style.pointerEvents = 'none';
        });
    }

    hideLoadingState() {
        const loadingElements = document.querySelectorAll('.chart-container');
        loadingElements.forEach(el => {
            el.style.opacity = '1';
            el.style.pointerEvents = 'auto';
        });
    }

    showAlert(message, type = 'info') {
        // Use the global alert function from base.html
        if (typeof showAlert === 'function') {
            showAlert(message, type);
        } else {
            console.log(`${type.toUpperCase()}: ${message}`);
        }
    }

    showError(message) {
        this.showAlert(message, 'error');
    }

    destroy() {
        // Cleanup method
        if (this.autoRefreshInterval) {
            clearInterval(this.autoRefreshInterval);
        }

        Object.values(this.charts).forEach(chart => {
            if (chart && typeof chart.destroy === 'function') {
                chart.destroy();
            }
        });
    }
}

// Utility functions
window.downloadChart = function(chartId) {
    if (window.dashboardManager) {
        window.dashboardManager.downloadChart(chartId);
    }
};

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.dashboardManager = new DashboardManager();
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (window.dashboardManager) {
        window.dashboardManager.destroy();
    }
});

// Export for module usage (if needed)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DashboardManager;
}