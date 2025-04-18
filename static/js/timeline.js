// Symbol timeline visualization

function initializeSymbolTimeline() {
    console.log("Initializing symbol timeline visualization");

    const container = document.getElementById('timelineChart');
    if (!container) {
        console.error("Timeline chart container not found");
        return;
    }

    // Fetch timeline data
    fetch('/api/timeline')
        .then(response => {
            console.log("Timeline data response status:", response.status);
            return response.json();
        })
        .then(data => {
            console.log("Timeline data received", data);

            // Sort by year
            data.sort((a, b) => a.year - b.year);

            // Prepare data for Plotly
            const traces = [];

            // Group by tradition
            const traditionGroups = {};
            data.forEach(item => {
                // Handle multi-tradition entries
                const traditions = item.tradition.split('/');
                const primaryTradition = traditions[0]; // Use the first one as primary

                if (!traditionGroups[primaryTradition]) {
                    traditionGroups[primaryTradition] = [];
                }
                traditionGroups[primaryTradition].push(item);
            });

            // Create a trace for each tradition
            Object.keys(traditionGroups).forEach((tradition, i) => {
                const items = traditionGroups[tradition];
                traces.push({
                    type: 'scatter',
                    mode: 'markers+text',
                    name: tradition,
                    x: items.map(d => d.year),
                    y: Array(items.length).fill(i + 1),  // Stack traditions vertically
                    text: items.map(d => d.name),
                    textposition: 'top center',
                    marker: {
                        size: 10,
                        opacity: 0.8
                    },
                    hovertemplate: '<b>%{text}</b><br>Year: %{x}<br>Tradition: ' + tradition + '<extra></extra>'
                });
            });

            // Layout configuration
            const layout = {
                paper_bgcolor: 'rgba(0,0,0,0)',
                plot_bgcolor: 'rgba(0,0,0,0)',
                font: {
                    family: 'Arial, sans-serif',
                    size: 12,
                    color: '#e0e0e0'
                },
                title: {
                    text: 'Symbol Timeline',
                    font: {
                        family: 'Arial, sans-serif',
                        size: 18,
                        color: '#e0e0e0'
                    }
                },
                xaxis: {
                    title: 'Year',
                    showgrid: true,
                    gridcolor: 'rgba(255,255,255,0.1)',
                    zeroline: true,
                    zerolinecolor: 'rgba(255,255,255,0.2)',
                    showline: true,
                    linecolor: 'rgba(255,255,255,0.2)',
                    tickcolor: 'rgba(255,255,255,0.2)',
                    tickfont: {
                        color: '#e0e0e0'
                    }
                },
                yaxis: {
                    showgrid: false,
                    zeroline: false,
                    showticklabels: false
                },
                showlegend: true,
                legend: {
                    x: 0,
                    y: 1,
                    font: {
                        family: 'Arial, sans-serif',
                        size: 10,
                        color: '#e0e0e0'
                    },
                    bgcolor: 'rgba(0,0,0,0.5)',
                    bordercolor: 'rgba(255,255,255,0.2)'
                },
                margin: {
                    l: 40,
                    r: 40,
                    t: 40,
                    b: 40
                },
                hovermode: 'closest'
            };

            Plotly.newPlot('timelineChart', traces, layout, {responsive: true});

            // Add click event
            container.on('plotly_click', function(data) {
                const symbolName = data.points[0].text;
                const symbolData = data.find(item => item.name === symbolName);

                if (symbolData) {
                    showSymbolDetails(symbolData);
                }
            });
        })
        .catch(error => {
            console.error("Error loading timeline data:", error);
            container.innerHTML = `<div class="alert alert-danger">Error loading timeline data: ${error.message}</div>`;
        });
}