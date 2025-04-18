// Element distribution visualization

function initializeElementChart() {
    console.log("Initializing element chart visualization");

    const container = document.getElementById('elementPieChart');
    if (!container) {
        console.error("Element pie chart container not found");
        return;
    }

    // Fetch element distribution data
    fetch('/api/element-distribution')
        .then(response => {
            console.log("Element distribution response status:", response.status);
            return response.json();
        })
        .then(data => {
            console.log("Element distribution data received", data);

            // Extract basic data for pie chart
            const values = data.map(d => d.count);
            const labels = data.map(d => d.element);

            // Generate colors with purple/violet theme
            const purpleColors = [
                '#8a2be2', '#9370db', '#6a5acd', '#483d8b', '#7b68ee',
                '#9932cc', '#ba55d3', '#dda0dd', '#d8bfd8', '#ee82ee'
            ];

            // Create the pie chart
            const trace = {
                type: 'pie',
                values: values,
                labels: labels,
                textinfo: 'label+percent',
                textposition: 'inside',
                marker: {
                    colors: purpleColors.slice(0, values.length),
                    line: {
                        color: '#1e1e1e',
                        width: 2
                    }
                },
                hoverinfo: 'label+value+percent',
                hole: 0.4,
                hovertemplate: '<b>%{label}</b><br>Count: %{value}<br>%{percent}<extra></extra>'
            };

            // Layout configuration
            const layout = {
                paper_bgcolor: 'rgba(0,0,0,0)',
                plot_bgcolor: 'rgba(0,0,0,0)',
                font: {
                    family: 'Arial, sans-serif',
                    color: '#e0e0e0'
                },
                legend: {
                    font: {
                        family: 'Arial, sans-serif',
                        color: '#e0e0e0'
                    },
                    orientation: 'h',
                    y: -0.2
                },
                margin: {
                    l: 20,
                    r: 20,
                    t: 20,
                    b: 20
                },
                annotations: [{
                    text: 'Elements',
                    showarrow: false,
                    font: {
                        size: 16,
                        color: '#e0e0e0'
                    }
                }]
            };

            Plotly.newPlot('elementPieChart', [trace], layout, {responsive: true});

            // Add click event
            container.on('plotly_click', function(data) {
                const elementName = data.points[0].label;

                // Find the element data
                const elementData = data.find(item => item.element === elementName);

                // Show element details
                const elementDetailsEl = document.getElementById('elementDetails');
                if (elementDetailsEl) {
                    // Format element details
                    let detailsHTML = `
                        <h4>${elementName}</h4>
                        <p><strong>Symbol count:</strong> ${data.points[0].value}</p>
                    `;

                    // Add description if available
                    if (elementData && elementData.description) {
                        detailsHTML += `<p>${elementData.description}</p>`;
                    }

                    // Add associated symbols if available
                    if (elementData && elementData.symbols && elementData.symbols.length > 0) {
                        detailsHTML += `
                            <h5>Associated Symbols</h5>
                            <ul>
                                ${elementData.symbols.map(symbol => `<li>${symbol}</li>`).join('')}
                            </ul>
                        `;
                    }

                    elementDetailsEl.innerHTML = detailsHTML;
                    elementDetailsEl.classList.remove('d-none');
                }
            });
        })
        .catch(error => {
            console.error("Error loading element distribution data:", error);
            container.innerHTML = `<div class="alert alert-danger">Error loading element data: ${error.message}</div>`;
        });
}