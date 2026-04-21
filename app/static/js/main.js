document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('analyze-form').addEventListener('submit', async function (e) {
        e.preventDefault();

        const formData = new FormData(this);
        document.getElementById('loading').style.display = 'block';
        document.getElementById('welcome-message').style.display = 'none';
        document.getElementById('result-area').style.display = 'none';

        try {
            const response = await fetch('/analyze', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.success) {
                updateDashboard(data);
            } else {
                alert('Error: ' + data.error);
            }
        } catch (error) {
            console.error(error);
            alert('An error occurred during analysis.');
        } finally {
            document.getElementById('loading').style.display = 'none';
        }
    });

    // Live Monitor Logic
    let liveInterval = null;
    const liveBtn = document.getElementById('live-btn');

    if (liveBtn) {
        liveBtn.addEventListener('click', function () {
            if (liveInterval) {
                // Stop
                clearInterval(liveInterval);
                liveInterval = null;
                liveBtn.innerText = "🔴 Start Live Monitor";
                liveBtn.style.background = "var(--danger)";
                document.getElementById('live-status').style.display = 'none';
            } else {
                // Start
                liveBtn.innerText = "⏹ Stop Monitor";
                liveBtn.style.background = "var(--success)";
                document.getElementById('live-status').style.display = 'block';

                // Run immediately then interval
                fetchLatest();
                liveInterval = setInterval(fetchLatest, 10000); // Check every 10s
            }
        });
    }

    async function fetchLatest() {
        try {
            // Visual feedback of scanning
            const statusEl = document.getElementById('live-status');
            if (statusEl) statusEl.innerText = "Scanning for new files...";

            const stateSelect = document.getElementById('state');
            const selectedState = stateSelect ? stateSelect.value : 'All India';

            const response = await fetch('/latest_analysis?state=' + encodeURIComponent(selectedState));
            const data = await response.json();

            if (data.success) {
                if (statusEl) statusEl.innerText = "Processing: " + data.filename;

                // Update Dropdown to match if possible
                const select = document.getElementById('filename');
                if (select) select.value = data.filename;

                // Update Results UI
                updateDashboard(data);
            }
        } catch (e) {
            console.error("Monitor Error:", e);
        }
    }

    function updateDashboard(data) {
        document.getElementById('result-area').style.display = 'block';
        const welcomeMsg = document.getElementById('welcome-message');
        if (welcomeMsg) welcomeMsg.style.display = 'none';

        const pred = data.prediction;
        const statusEl = document.getElementById('pred-status');
        if (statusEl) {
            statusEl.innerText = pred.status;
            statusEl.className = 'metric-value';
            if (pred.status.includes("High")) statusEl.classList.add('status-high');
            else if (pred.status.includes("Moderate")) statusEl.classList.add('status-mod');
            else statusEl.classList.add('status-low');
        }

        const msgEl = document.getElementById('pred-message');
        if (msgEl) msgEl.innerText = pred.message;

        const confEl = document.getElementById('pred-confidence');
        if (confEl) confEl.innerText = pred.confidence + '%';

        const ratioEl = document.getElementById('pred-storm-ratio');
        if (ratioEl) ratioEl.innerText = pred.storm_ratio + '%';

        const imgEl = document.getElementById('xai-image');
        if (imgEl) imgEl.src = 'data:image/png;base64,' + data.image_data;

        // Weather
        if (data.live_weather) {
            const w = data.live_weather;
            const subtitleEl = document.getElementById('weather-subtitle');
            if (subtitleEl) subtitleEl.innerText = "Live weather from " + data.state_city;

            const contentEl = document.getElementById('live-weather-content');
            if (contentEl) {
                contentEl.innerHTML = `
                    <div style="font-size:2rem; font-weight:bold; color:var(--accent)">${w.main.temp}°C</div>
                    <div style="text-transform:capitalize; margin-top:4px;">${w.weather[0].description}</div>
                    <div style="color:var(--text-muted); margin-top:4px;">Humidity: ${w.main.humidity}%</div>
                `;
            }
        }

        // Forecast
        if (data.forecast) {
            const f = data.forecast;
            let forecastHTML = '<div class="forecast-grid">';
            f.list.slice(0, 3).forEach(item => { // Show next 3 points
                const time = new Date(item.dt * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
                forecastHTML += `
                    <div class="forecast-item">
                        <div style="color:var(--text-muted)">${time}</div>
                        <div style="font-weight:bold; font-size:1.1rem; margin:4px 0">${item.main.temp}°C</div>
                        <div>${item.weather[0].main}</div>
                    </div>
                `;
            });
            forecastHTML += '</div>';

            const forecastContainer = document.getElementById('forecast-container');
            if (forecastContainer) {
                forecastContainer.innerHTML = `
                    <div style="margin-top:20px; border-top:1px solid var(--border); padding-top:16px;">
                        <small style="color:var(--text-muted); text-transform:uppercase; letter-spacing:1px; font-weight:600;">Forecast Projection (External API)</small>
                        ${forecastHTML}
                    </div>
                `;
            }
        }
    }
});
