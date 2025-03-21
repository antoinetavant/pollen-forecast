
let chartjsChart = null;

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

        console.log("Chart Data for Chart.js:", data); // Debug the data passed to Chart.js

        // Prepare the data for Chart.js
        const labels = data.map(item => item.time); // Extract time labels
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
                            }
                        },
                        y: {
                            title: {
                                display: true,
                                text: polenType
                            },
                            beginAtZero: true
                        }
                    },
                    plugins: {
                        tooltip: {
                            callbacks: {
                                label: function (context) {
                                    const index = context.dataIndex;
                                    const riskLevel = data[index][`${polenType}_niveau`];
                                    return `${context.dataset.label}: ${context.raw} (${riskLevel})`;
                                }
                            }
                        }
                    }
                }
            });
        }
    } catch (error) {
        spinner.classList.add('d-none'); // Hide spinner
        console.error('Error fetching data for Chart.js:', error);
        alert('An error occurred while fetching data.');
    }
}

