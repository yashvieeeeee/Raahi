// Chart helper functions for Raahi application

// Common chart configuration
const chartDefaults = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            display: false
        }
    },
    scales: {
        y: {
            beginAtZero: true,
            grid: {
                color: 'rgba(255, 255, 255, 0.1)'
            },
            ticks: {
                color: '#8a8d94',
                font: {
                    family: "'DM Mono', monospace"
                }
            }
        },
        x: {
            grid: {
                display: false
            },
            ticks: {
                color: '#8a8d94',
                font: {
                    family: "'DM Mono', monospace"
                }
            }
        }
    }
};

// Create weekly CO2 chart
function createWeeklyChart(ctx, data) {
    const labels = [];
    for (let i = 6; i >= 0; i--) {
        const date = new Date();
        date.setDate(date.getDate() - i);
        labels.push(date.toLocaleDateString('en-US', { weekday: 'short' }));
    }

    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: 'rgba(31, 205, 138, 0.6)',
                borderColor: 'rgba(31, 205, 138, 1)',
                borderWidth: 1,
                borderRadius: 4
            }]
        },
        options: {
            ...chartDefaults,
            plugins: {
                ...chartDefaults.plugins,
                tooltip: {
                    backgroundColor: 'rgba(22, 23, 25, 0.9)',
                    titleColor: '#e8e9eb',
                    bodyColor: '#e8e9eb',
                    borderColor: 'rgba(255, 255, 255, 0.1)',
                    borderWidth: 1,
                    padding: 12,
                    displayColors: false,
                    callbacks: {
                        label: function(context) {
                            return `CO₂: ${context.parsed.y.toFixed(1)}g`;
                        }
                    }
                }
            }
        }
    });
}

// Create monthly trend chart
function createMonthlyChart(ctx, data) {
    const labels = [];
    for (let i = 3; i >= 0; i--) {
        labels.push('Week ' + (4-i));
    }

    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                borderColor: '#a78bfa',
                backgroundColor: 'rgba(167, 139, 250, 0.2)',
                borderWidth: 2,
                tension: 0.4,
                fill: true,
                pointBackgroundColor: '#a78bfa',
                pointBorderColor: '#1e2128',
                pointBorderWidth: 2,
                pointRadius: 4,
                pointHoverRadius: 6
            }]
        },
        options: {
            ...chartDefaults,
            plugins: {
                ...chartDefaults.plugins,
                tooltip: {
                    backgroundColor: 'rgba(22, 23, 25, 0.9)',
                    titleColor: '#e8e9eb',
                    bodyColor: '#e8e9eb',
                    borderColor: 'rgba(255, 255, 255, 0.1)',
                    borderWidth: 1,
                    padding: 12,
                    displayColors: false,
                    callbacks: {
                        label: function(context) {
                            return `CO₂: ${context.parsed.y.toFixed(1)}g`;
                        }
                    }
                }
            }
        }
    });
}

// Create user growth chart for admin
function createUserGrowthChart(ctx) {
    const labels = [];
    const data = [];
    for (let i = 6; i >= 0; i--) {
        const date = new Date();
        date.setDate(date.getDate() - i);
        labels.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));
        data.push(Math.floor(Math.random() * 10) + 1);
    }

    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                borderColor: '#1fcd8a',
                backgroundColor: 'rgba(31, 205, 138, 0.2)',
                borderWidth: 2,
                tension: 0.4,
                fill: true,
                pointBackgroundColor: '#1fcd8a',
                pointBorderColor: '#1e2128',
                pointBorderWidth: 2,
                pointRadius: 4,
                pointHoverRadius: 6
            }]
        },
        options: {
            ...chartDefaults,
            plugins: {
                ...chartDefaults.plugins,
                tooltip: {
                    backgroundColor: 'rgba(22, 23, 25, 0.9)',
                    titleColor: '#e8e9eb',
                    bodyColor: '#e8e9eb',
                    borderColor: 'rgba(255, 255, 255, 0.1)',
                    borderWidth: 1,
                    padding: 12,
                    displayColors: false,
                    callbacks: {
                        label: function(context) {
                            return `New Users: ${context.parsed.y}`;
                        }
                    }
                }
            }
        }
    });
}

// Create AQI by zone chart for admin
function createAqiChart(ctx, stationStats) {
    const labels = Object.keys(stationStats).slice(0, 5);
    const data = labels.map(station => stationStats[station].congestion_perc);

    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: 'rgba(245, 166, 35, 0.6)',
                borderColor: 'rgba(245, 166, 35, 1)',
                borderWidth: 1,
                borderRadius: 4
            }]
        },
        options: {
            ...chartDefaults,
            plugins: {
                ...chartDefaults.plugins,
                tooltip: {
                    backgroundColor: 'rgba(22, 23, 25, 0.9)',
                    titleColor: '#e8e9eb',
                    bodyColor: '#e8e9eb',
                    borderColor: 'rgba(255, 255, 255, 0.1)',
                    borderWidth: 1,
                    padding: 12,
                    displayColors: false,
                    callbacks: {
                        label: function(context) {
                            return `Congestion: ${context.parsed.y.toFixed(1)}%`;
                        }
                    }
                }
            }
        }
    });
}

// Utility function to format numbers
function formatNumber(num, decimals = 1) {
    return num.toFixed(decimals);
}

// Utility function to format currency
function formatCurrency(amount) {
    return '₹' + Math.round(amount).toLocaleString('en-IN');
}

// Utility function to get CO2 color based on value
function getCo2Color(value) {
    if (value < 50) return '#1fcd8a';  // green
    if (value < 100) return '#f5a623'; // amber
    return '#ff5a5a'; // red
}

// Export functions for use in templates
window.RaahiCharts = {
    createWeeklyChart,
    createMonthlyChart,
    createUserGrowthChart,
    createAqiChart,
    formatNumber,
    formatCurrency,
    getCo2Color
};
