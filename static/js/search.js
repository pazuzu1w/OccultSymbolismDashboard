// Search functionality

function initializeSearch() {
    const searchInput = document.getElementById('searchInput');
    const searchButton = document.getElementById('searchButton');
    const resultsDiv = document.getElementById('searchResults');

    if (!searchInput || !searchButton || !resultsDiv) return;

    // Set up event listeners
    searchButton.addEventListener('click', performSearch);
    searchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            performSearch();
        }
    });

    function performSearch() {
        const query = searchInput.value;
        if (!query) return;

        // Show loading indicator
        resultsDiv.innerHTML = '<div class="text-center"><div class="loading-spinner"></div><p>Searching...</p></div>';

        // Fetch search results
        fetch(`/api/search?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                if (data.length === 0) {
                    resultsDiv.innerHTML = '<p class="text-muted">No results found.</p>';
                    return;
                }

                // Display results
                resultsDiv.innerHTML = '';
                data.forEach(symbol => {
                    const resultItem = document.createElement('div');
                    resultItem.className = 'search-result-item';

                    // Format century as BCE/CE
                    const century = symbol.century_origin;
                    const centuryText = century < 0
                        ? Math.abs(century) + ' BCE'
                        : century + ' CE';

                    resultItem.innerHTML = `
                        <h6>${symbol.name}</h6>
                        <p>Tradition: ${symbol.tradition}<br>
                        Element: ${symbol.element}<br>
                        Origin: ${centuryText}</p>
                    `;

                    // Click to show details
                    resultItem.addEventListener('click', () => {
                        showSymbolDetails(symbol);
                    });

                    resultsDiv.appendChild(resultItem);
                });
            })
            .catch(error => {
                resultsDiv.innerHTML = `<p class="text-danger">Error: ${error.message}</p>`;
            });
    }
}

// Show symbol details in the details panel
function showSymbolDetails(symbol) {
    // Get the details panel
    const detailsPanel = document.getElementById('symbolDetails');
    if (!detailsPanel) return;

    // Format century as BCE/CE
    const century = symbol.century_origin;
    const centuryText = century < 0
        ? Math.abs(century) + ' BCE'
        : century + ' CE';

    // Update details panel with symbol info
    detailsPanel.innerHTML = `
        <h4>${symbol.name}</h4>
        <p><strong>Tradition:</strong> ${symbol.tradition}</p>
        <p><strong>Element:</strong> ${symbol.element}</p>
        <p><strong>Origin:</strong> ${centuryText}</p>
        ${symbol.description ? `<p>${symbol.description}</p>` : ''}
        <h5>Connected Symbols</h5>
        <div id="connectedSymbols" class="connected-symbols">
            <p>Loading...</p>
        </div>
    `;

    // Fetch connected symbols
    fetch(`/api/symbols/${symbol.id}/connections`)
        .then(response => response.json())
        .then(data => {
            const connectedSymbolsEl = document.getElementById('connectedSymbols');
            if (!connectedSymbolsEl) return;

            if (data.length === 0) {
                connectedSymbolsEl.innerHTML = '<p>No connected symbols found.</p>';
                return;
            }

            connectedSymbolsEl.innerHTML = '';
            data.forEach(connected => {
                connectedSymbolsEl.innerHTML += `
                    <div class="connected-symbol-item">
                        <span class="symbol-name">${connected.name}</span>
                        <span class="symbol-tradition">${connected.tradition}</span>
                    </div>
                `;
            });
        })
        .catch(error => {
            console.error('Error loading connected symbols:', error);
            const connectedSymbolsEl = document.getElementById('connectedSymbols');
            if (connectedSymbolsEl) {
                connectedSymbolsEl.innerHTML = `<p class="text-danger">Error loading connected symbols</p>`;
            }
        });

    // Show the panel if it's hidden
    detailsPanel.classList.remove('d-none');
}