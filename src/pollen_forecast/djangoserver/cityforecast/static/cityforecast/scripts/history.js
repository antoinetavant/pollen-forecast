let chartjsChart = null;

async function fetchAndRenderChartJS() {
    const polenType = document.getElementById('polen_type').value;

    const spinner = document.getElementById('loading-spinner');
    spinner.classList.remove('d-none'); // Show the spinner

    try {
        const response = await fetch(`/api/pollen-history-data/?pollen_type=${polenType}`);
        const data = await response.json();
        spinner.classList.add('d-none'); // Hide the spinner

        if (data.error) {
            alert(data.error);
            return;
        }

        console.log("Chart Data for Chart.js:", data); // Debug the data passed to Chart.js

        // Prepare the data for Chart.js
        const labels = data.map(item => {
            const date = new Date(item.time);
            return new Intl.DateTimeFormat('fr-FR', { month: 'long', day: 'numeric' }).format(date); // Format as day and month in French
        }); // Extract time labels
        const values = data.map(item => item[polenType]); // Extract values for the selected pollen type
        const colors = data.map(item => {
            switch (item[`${polenType}_niveau`]) {
                case "faible": return "green";
                case "moderé": return "gold";
                case "modéré-fort": return "orange";
                case "fort": return "red";
                case "très fort": return "purple";
                default: return "gray";
            }
        });

        if (chartjsChart) {
            // Update the existing chart data
            chartjsChart.data.labels = labels;
            chartjsChart.data.datasets[0].data = values;
            chartjsChart.data.datasets[0].backgroundColor = colors;
            chartjsChart.data.datasets[0].borderColor = colors.map(color => color); // Update border colors

            // Update chart options
            chartjsChart.options.plugins.tooltip.callbacks.label = function (context) {
                const index = context.dataIndex;
                const riskLevel = data[index][`${polenType}_niveau`];
                return `${context.dataset.label}: ${context.raw} (${riskLevel})`;
            };
            chartjsChart.options.scales.y.title.text = polenType; // Update y-axis label
            chartjsChart.options.plugins.title.text = `Pollen Forecast for ${polenType}`; // Update chart title
            chartjsChart.options.plugins.legend.display = false; // Disable default legend
            updateCustomLegend(); // Update custom legend

            chartjsChart.update(); // Update the chart
            
        } else {
            // Create the Chart.js chart if it doesn't exist
            const ctx = document.getElementById('chartjs-canvas').getContext('2d');
            chartjsChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: polenType,
                        data: values,
                        backgroundColor: colors,
                        borderColor: colors.map(color => color), // Use the same color for borders
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: {
                            title: {
                                display: true,
                                text: 'Date'
                            },
                            ticks: {
                                maxRotation: 0, // Disable text rotation
                                minRotation: 0 // Ensure text is horizontal
                            }
                        },
                        y: {
                            title: {
                                display: true,
                                text: polenType // Set initial y-axis label
                            },
                            beginAtZero: true
                        }
                    },
                    plugins: {
                        title: {
                            display: true,
                            text: `Pollen Forecast for ${polenType}` // Set initial chart title
                        },
                        tooltip: {
                            callbacks: {
                                label: function (context) {
                                    const index = context.dataIndex;
                                    const riskLevel = data[index][`${polenType}_niveau`];
                                    return `${context.dataset.label}: ${context.raw} (${riskLevel})`;
                                }
                            }
                        },
                        legend: {
                            display: false // Disable default legend
                        }
                    }
                }
            });

            updateCustomLegend(); // Create custom legend
        }
    } catch (error) {
        spinner.classList.add('d-none'); // Hide spinner
        console.error('Error fetching data for Chart.js:', error);
        alert('An error occurred while fetching data.');
    }
}

// Function to create or update the custom legend
function updateCustomLegend() {
    const legendContainer = document.getElementById('custom-legend');
    legendContainer.innerHTML = ''; // Clear existing legend

    const legendItems = [
        { label: 'faible', color: 'green' },
        { label: 'moderé', color: 'gold' },
        { label: 'modéré-fort', color: 'orange' },
        { label: 'fort', color: 'red' },
        { label: 'très fort', color: 'purple' }
    ];

    legendItems.forEach(item => {
        const legendItem = document.createElement('div');
        legendItem.style.display = 'flex';
        legendItem.style.alignItems = 'center';
        legendItem.style.marginBottom = '5px';

        const colorBox = document.createElement('span');
        colorBox.style.width = '20px';
        colorBox.style.height = '20px';
        colorBox.style.backgroundColor = item.color;
        colorBox.style.marginRight = '10px';

        const label = document.createElement('span');
        label.textContent = item.label;

        legendItem.appendChild(colorBox);
        legendItem.appendChild(label);
        legendContainer.appendChild(legendItem);
    });
}

