// Network graph visualization of symbol connections

function initializeNetworkGraph() {
    console.log("Initializing network graph visualization");

    const container = document.getElementById('networkGraph');
    if (!container) {
        console.error("Network graph container not found");
        return;
    }

    const width = container.clientWidth;
    const height = container.clientHeight || 500;

    // Create SVG container
    const svg = d3.select(container)
        .append('svg')
        .attr('width', width)
        .attr('height', height);

    // Add a group for zoom/pan behavior
    const g = svg.append('g');

    // Add zoom behavior
    const zoom = d3.zoom()
        .scaleExtent([0.1, 4])
        .on('zoom', (event) => {
            g.attr('transform', event.transform);
        });

    svg.call(zoom);

    // Create a tooltip
    const tooltip = d3.select('body')
        .append('div')
        .attr('class', 'network-tooltip')
        .style('opacity', 0)
        .style('position', 'absolute')
        .style('background-color', 'rgba(30, 30, 30, 0.9)')
        .style('color', '#e0e0e0')
        .style('padding', '10px')
        .style('border-radius', '5px')
        .style('pointer-events', 'none')
        .style('max-width', '300px')
        .style('font-size', '14px')
        .style('border', '1px solid #8a2be2')
        .style('z-index', '1000');

    // Load data
    fetch('/api/network')
        .then(response => {
            console.log("Network data response status:", response.status);
            return response.json();
        })
        .then(data => {
            console.log("Network data received", data);
            const nodes = data.nodes;
            const links = data.links;

            // Create force simulation
            const simulation = d3.forceSimulation(nodes)
                .force('link', d3.forceLink(links)
                    .id(d => d.id)
                    .distance(d => 150 - (d.strength * 50))
                    .strength(d => d.strength))
                .force('charge', d3.forceManyBody().strength(-200))
                .force('center', d3.forceCenter(width / 2, height / 2))
                .force('collision', d3.forceCollide().radius(20));

            // Create links
            const link = g.append('g')
                .attr('class', 'links')
                .selectAll('line')
                .data(links)
                .enter()
                .append('line')
                .attr('class', 'link')
                .attr('stroke-width', d => d.strength * 3)
                .attr('stroke', 'rgba(170, 93, 249, 0.5)')
                .on('mouseover', function(event, d) {
                    tooltip.transition()
                        .duration(200)
                        .style('opacity', 0.9);

                    const sourceNode = nodes.find(n => n.id === d.source.id || n.id === d.source);
                    const targetNode = nodes.find(n => n.id === d.target.id || n.id === d.target);

                    tooltip.html(`
                        <strong>${sourceNode?.name} → ${targetNode?.name}</strong><br>
                        <span>${d.description}</span><br>
                        <small>Strength: ${d.strength.toFixed(1)}</small>
                    `)
                    .style('left', (event.pageX + 10) + 'px')
                    .style('top', (event.pageY - 28) + 'px');
                })
                .on('mouseout', function() {
                    tooltip.transition()
                        .duration(500)
                        .style('opacity', 0);
                });

            // Create nodes
            const node = g.append('g')
                .attr('class', 'nodes')
                .selectAll('circle')
                .data(nodes)
                .enter()
                .append('circle')
                .attr('class', 'node')
                .attr('r', d => 8 + (links.filter(l =>
                    l.source.id === d.id ||
                    l.target.id === d.id ||
                    l.source === d.id ||
                    l.target === d.id
                ).length / 2))
                .attr('fill', d => d.color || '#8a2be2')
                .call(d3.drag()
                    .on('start', dragstarted)
                    .on('drag', dragged)
                    .on('end', dragended))
                .on('mouseover', function(event, d) {
                    // Highlight connected nodes and links
                    const connectedLinks = links.filter(l =>
                        l.source.id === d.id ||
                        l.target.id === d.id ||
                        l.source === d.id ||
                        l.target === d.id
                    );

                    const connectedNodeIds = new Set();
                    connectedLinks.forEach(l => {
                        if (l.source.id) {
                            connectedNodeIds.add(l.source.id);
                            connectedNodeIds.add(l.target.id);
                        } else {
                            connectedNodeIds.add(l.source);
                            connectedNodeIds.add(l.target);
                        }
                    });

                    // Highlight connected nodes
                    node.classed('highlighted', n => connectedNodeIds.has(n.id));

                    // Highlight connected links
                    link.classed('highlighted', l =>
                        (l.source.id === d.id || l.target.id === d.id) ||
                        (l.source === d.id || l.target === d.id)
                    )
                    .classed('dimmed', l =>
                        (l.source.id !== d.id && l.target.id !== d.id) &&
                        (l.source !== d.id && l.target !== d.id)
                    );

                    // Show tooltip
                    tooltip.transition()
                        .duration(200)
                        .style('opacity', 0.9);

                    let yearText = d.century < 0
                        ? Math.abs(d.century * 100) + " BCE"
                        : d.century * 100 + " CE";

                    tooltip.html(`
                        <strong>${d.name}</strong><br>
                        <span>Tradition: ${d.tradition}</span><br>
                        <span>Element: ${d.element}</span><br>
                        <span>Origin: ~${yearText}</span><br>
                        <span class="text-muted">${d.description || ''}</span>
                    `)
                    .style('left', (event.pageX + 10) + 'px')
                    .style('top', (event.pageY - 28) + 'px');
                })
                .on('mouseout', function() {
                    // Remove highlighting
                    node.classed('highlighted', false);
                    link.classed('highlighted', false)
                        .classed('dimmed', false);

                    // Hide tooltip
                    tooltip.transition()
                        .duration(500)
                        .style('opacity', 0);
                })
                .on('click', function(event, d) {
                    // Show detailed info and fetch connected symbols
                    showSymbolDetails(d);
                });

            // Add node labels
            const labels = g.append('g')
                .attr('class', 'labels')
                .selectAll('text')
                .data(nodes)
                .enter()
                .append('text')
                .text(d => d.name)
                .attr('font-size', '10px')
                .attr('fill', 'white')
                .attr('text-anchor', 'middle')
                .attr('dy', '0.35em')
                .attr('opacity', 0.7);

            // Update positions on simulation tick
            simulation.on('tick', () => {
                link
                    .attr('x1', d => d.source.x)
                    .attr('y1', d => d.source.y)
                    .attr('x2', d => d.target.x)
                    .attr('y2', d => d.target.y);

                node
                    .attr('cx', d => d.x)
                    .attr('cy', d => d.y);

                labels
                    .attr('x', d => d.x)
                    .attr('y', d => d.y + 20);
            });

            // Drag functions
            function dragstarted(event, d) {
                if (!event.active) simulation.alphaTarget(0.3).restart();
                d.fx = d.x;
                d.fy = d.y;
            }

            function dragged(event, d) {
                d.fx = event.x;
                d.fy = event.y;
            }

            function dragended(event, d) {
                if (!event.active) simulation.alphaTarget(0);
                d.fx = null;
                d.fy = null;
            }

            // Add a simple legend
            const traditionsSet = new Set(nodes.map(n => n.tradition.split('/')[0]));
            const traditions = Array.from(traditionsSet);

            const legendContainer = d3.select(container)
                .append('div')
                .attr('class', 'network-legend')
                .style('position', 'absolute')
                .style('bottom', '10px')
                .style('left', '10px')
                .style('background-color', 'rgba(0, 0, 0, 0.7)')
                .style('padding', '10px')
                .style('border-radius', '5px')
                .style('max-width', '200px')
                .style('max-height', '150px')
                .style('overflow-y', 'auto')
                .style('z-index', '10');

            traditions.forEach(tradition => {
                const node = nodes.find(n => n.tradition.split('/')[0] === tradition);
                if (node) {
                    const color = node.color;

                    legendContainer.append('div')
                        .style('display', 'flex')
                        .style('align-items', 'center')
                        .style('margin-bottom', '5px')
                        .style('font-size', '12px')
                        .html(`
                            <span style="display: inline-block; width: 12px; height: 12px; border-radius: 50%; background-color: ${color}; margin-right: 5px;"></span>
                            <span>${tradition}</span>
                        `);
                }
            });
        })
        .catch(error => {
            console.error("Error loading network data:", error);
            container.innerHTML = `<div class="alert alert-danger">Error loading network data: ${error.message}</div>`;
        });
}