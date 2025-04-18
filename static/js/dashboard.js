// Main dashboard initialization script

// Wait for document to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all visualizations
    initializeNetworkGraph();
    initializeSymbolTimeline();
    initializeElementChart();
    initializeTraditionTimeline();
    initializeTraditionHeatmap();
    initializeRegionBarChart();
    initializeSearch();

    // Load dashboard summary data
    loadDashboardSummary();
});

// Load summary data for dashboard header
function loadDashboardSummary() {
    fetch('/api/dashboard/summary')
        .then(response => response.json())
        .then(data => {
            document.getElementById('totalSymbols').textContent = data.total_symbols;
            document.getElementById('totalTraditions').textContent = data.total_traditions;
            document.getElementById('timeSpan').textContent = `${formatYear(data.time_span.earliest)} to ${formatYear(data.time_span.latest)}`;

            // Display top traditions
            const traditionsEl = document.getElementById('topTraditions');
            traditionsEl.innerHTML = '';
            data.top_traditions.forEach(tradition => {
                traditionsEl.innerHTML += `<span class="badge bg-secondary me-1">${tradition.tradition} (${tradition.count})</span>`;
            });
        })
        .catch(error => console.error('Error loading dashboard summary:', error));
}

// Format year as BCE/CE
function formatYear(year) {
    if (year < 0) {
        return `${Math.abs(year)} BCE`;
    }
    return `${year} CE`;
}