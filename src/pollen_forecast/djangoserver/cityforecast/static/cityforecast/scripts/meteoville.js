let chartjsChart = null;
let currentDayIndex = 0; // Index to track the currently displayed day
let fetchedData = []; // Store the fetched data for navigation

async function fetchAndRenderChartJS() {
    const date = document.getElementById('date').value;
    const cityName = document.getElementById('city_name').value;
    const polenType = document.getElementById('polen_type').value;

    const spinner = document.getElementById('loading-spinner');
    spinner.classList.remove('d-none'); // Show the spinner

    try {
        const response = await fetch(`/api/pollen-data/?date=${date}&city_name=${cityName}&pollen_type=${polenType}`);
        const data = await response.json();
        spinner.classList.add('d-none'); // Hide the spinner

        if (data.error) {
            alert(data.error);
            return;
        }

        fetchedData = data; // Store the fetched data
        console.log('Fetched data:', fetchedData);
        currentDayIndex = 0; // Reset to the first day
        renderChartForDay(currentDayIndex); // Render the chart for the first day
    } catch (error) {
        spinner.classList.add('d-none'); // Hide spinner
        console.error('Error fetching data for Chart.js:', error);
        alert('An error occurred while fetching data.');
    }
}

function renderChartForDay(dayIndex) {
    console.log('Rendering chart for day index:', dayIndex);
    const pollen_type = document.getElementById('polen_type').value;
    const pollen_niveau = `${pollen_type}_niveau`;
    const dayData = fetchedData.slice(dayIndex, dayIndex + 24); // Get data for the selected day

    // Extract only the time portion (e.g., "14:00") from the full timestamp
    const labels = dayData.map(entry => entry.time.split('T')[1].substring(0, 5)); // Format: "HH:mm"

    const values = dayData.map(entry => entry[pollen_type]); // Use the pollen value as the data
    const colors = dayData.map(entry => getColorForRiskLevel(entry[pollen_niveau])); // Get colors based on risk level

    // Update the current day display
    document.getElementById('currentDay').textContent = dayData[0]?.time.split('T')[0]; // Display the date

    if (chartjsChart) {
        // Update the existing chart data
        chartjsChart.data.labels = labels;
        chartjsChart.data.datasets[0].data = values;
        chartjsChart.data.datasets[0].backgroundColor = colors;
        chartjsChart.data.datasets[0].borderColor = colors.map(color => color); // Update border colors
        chartjsChart.update(); // Update the chart
    } else {
        // Create the Chart.js chart if it doesn't exist
        const ctx = document.getElementById('chartjs-canvas').getContext('2d');
        chartjsChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: document.getElementById('polen_type').value,
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
                            text: 'Time (Hourly)' // Updated x-axis title
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: document.getElementById('polen_type').value
                        },
                        beginAtZero: true
                    }
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function (context) {
                                const riskLevel = dayData[context.dataIndex][`${document.getElementById('polen_type').value}_niveau`];
                                return `${context.dataset.label}: ${context.raw} (${riskLevel})`;
                            }
                        }
                    }
                }
            }
        });
    }
}

function getColorForRiskLevel(riskLevel) {
    switch (riskLevel) {
        case "faible": return "green";
        case "moderé": return "gold";
        case "modéré-fort": return "orange";
        case "fort": return "red";
        case "très fort": return "purple";
        default: return "gray";
    }
}

// Event listeners for navigation buttons
document.getElementById('prevDay').addEventListener('click', () => {
    if (currentDayIndex > 23) {
        currentDayIndex = currentDayIndex - 24;
        renderChartForDay(currentDayIndex);
    }
});

document.getElementById('nextDay').addEventListener('click', () => {
    if (currentDayIndex < fetchedData.length - 24) {
        currentDayIndex = currentDayIndex + 24;
        renderChartForDay(currentDayIndex);
    }
});

// Call fetchAndRenderChartJS when the page loads
document.addEventListener('DOMContentLoaded', fetchAndRenderChartJS);

