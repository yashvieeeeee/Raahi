(function () {
    const page = document.body.dataset.page;
    const stack = document.getElementById("toast-stack");

    const showToast = (message) => {
        if (!stack) return;
        const item = document.createElement("div");
        item.className = "toast";
        item.textContent = message;
        stack.appendChild(item);
        window.setTimeout(() => item.remove(), 3200);
    };

    const gramsToKg = (value) => (Number(value || 0) / 1000).toFixed(2);
    
    const formatDuration = (minutes) => {
        const mins = Math.round(Number(minutes || 0));
        if (mins < 60) return `${mins} min`;
        const hours = Math.floor(mins / 60);
        const remainingMins = mins % 60;
        return remainingMins > 0 ? `${hours} hr ${remainingMins} min` : `${hours} hr`;
    };
    
    const chartPalette = ["#1A4D2E", "#2F7B4D", "#3B82F6", "#F59E0B", "#EF4444", "#9CA3AF"];
    const chartInstances = new Map();
    const prefersReducedMotion = window.matchMedia?.("(prefers-reduced-motion: reduce)")?.matches ?? false;
    const chartTooltipTheme = {
        backgroundColor: "rgba(15, 31, 20, 0.92)",
        titleColor: "#F1F5F0",
        bodyColor: "#F1F5F0",
        borderColor: "rgba(255, 255, 255, 0.08)",
        borderWidth: 1,
        padding: 12,
        displayColors: false
    };

    const markChartReady = (canvas) => {
        const shell = canvas?.closest("[data-chart-shell]");
        if (shell) {
            shell.classList.remove("is-loading");
            shell.classList.add("is-ready");
        }
    };

    const debounce = (callback, delay = 140) => {
        let timeoutId = null;
        return (...args) => {
            window.clearTimeout(timeoutId);
            timeoutId = window.setTimeout(() => callback(...args), delay);
        };
    };

    const createChart = (canvasId, config) => {
        const canvas = document.getElementById(canvasId);
        if (!canvas || !window.Chart) {
            markChartReady(canvas);
            return null;
        }

        const chart = new window.Chart(canvas, {
            ...config,
            options: {
                animation: false,
                normalized: true,
                responsive: true,
                maintainAspectRatio: false,
                ...config.options,
                plugins: {
                    ...config.options?.plugins,
                    tooltip: {
                        ...chartTooltipTheme,
                        ...config.options?.plugins?.tooltip
                    }
                }
            }
        });
        markChartReady(canvas);
        return chart;
    };

    const queueChart = (canvasId, configFactory) => {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return null;

        const createWhenVisible = () => {
            if (chartInstances.has(canvasId)) return chartInstances.get(canvasId);
            const config = typeof configFactory === "function" ? configFactory() : configFactory;
            const chart = createChart(canvasId, config);
            if (chart) chartInstances.set(canvasId, chart);
            return chart;
        };

        const shell = canvas.closest("[data-chart-shell]") || canvas;
        const rect = shell.getBoundingClientRect();
        const withinInitialViewport = rect.top <= (window.innerHeight + 220) && rect.bottom >= -220;
        if (withinInitialViewport) {
            return createWhenVisible();
        }

        if (!("IntersectionObserver" in window)) {
            return createWhenVisible();
        }

        const observer = new IntersectionObserver((entries) => {
            entries.forEach((entry) => {
                if (!entry.isIntersecting) return;
                observer.disconnect();
                createWhenVisible();
            });
        }, {
            threshold: 0.05,
            rootMargin: "220px 0px"
        });

        observer.observe(shell);
        window.setTimeout(() => {
            observer.disconnect();
            createWhenVisible();
        }, 900);
        return null;
    };

    const createVerticalGradient = (canvasId, start, end) => {
        const canvas = document.getElementById(canvasId);
        const context = canvas?.getContext("2d");
        if (!context) return end;
        const gradient = context.createLinearGradient(0, 0, 0, canvas.height || 260);
        gradient.addColorStop(0, start);
        gradient.addColorStop(1, end);
        return gradient;
    };

    const setButtonState = (button, state, labels = {}) => {
        if (!button) return;
        const idleLabel = labels.idle || button.dataset.idleLabel || button.textContent.trim();
        const loadingLabel = labels.loading || "Working...";
        const successLabel = labels.success || "Done";

        button.dataset.idleLabel = idleLabel;
        button.classList.remove("is-loading", "is-success");
        button.disabled = false;
        button.setAttribute("aria-busy", "false");

        if (state === "loading") {
            button.classList.add("is-loading");
            button.disabled = true;
            button.setAttribute("aria-busy", "true");
            button.textContent = loadingLabel;
            return;
        }

        if (state === "success") {
            button.classList.add("is-success");
            button.textContent = successLabel;
            return;
        }

        button.textContent = idleLabel;
    };

    const resetButtonStateLater = (button, labels = {}) => {
        window.setTimeout(() => setButtonState(button, "idle", labels), 1400);
    };

    const setCircularMetric = (ringId, valueNodeId, labelNodeId, label, value, displayValue, maxValue = 100) => {
        const ring = document.getElementById(ringId);
        const valueNode = document.getElementById(valueNodeId);
        const labelNode = document.getElementById(labelNodeId);
        if (labelNode) labelNode.textContent = label;
        if (valueNode) valueNode.textContent = displayValue;
        if (ring) {
            const progress = Math.max(0, Math.min(100, (Number(value || 0) / maxValue) * 100));
            ring.style.setProperty("--metric-progress", `${progress}%`);
        }
    };

    const revealElements = () => {
        if (prefersReducedMotion) {
            document.querySelectorAll(".reveal").forEach((element) => element.classList.add("is-visible"));
            return;
        }

        const observer = new IntersectionObserver((entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.classList.add("is-visible");
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.15 });

        document.querySelectorAll(".reveal").forEach((element, index) => {
            element.style.transitionDelay = `${index * 60}ms`;
            observer.observe(element);
        });
    };

    const downloadPdfReport = async (endpoint, filename) => {
        const response = await fetch(endpoint, {
            method: "GET",
            headers: { Accept: "application/pdf" }
        });

        if (!response.ok) {
            let message = "Download failed.";
            try {
                const errorData = await response.json();
                message = errorData.error || message;
            } catch (error) {
                message = response.statusText || message;
            }
            throw new Error(message);
        }

        const contentType = response.headers.get("Content-Type") || "";
        if (!contentType.includes("application/pdf")) {
            let message = "Export did not return a PDF.";
            try {
                const errorData = await response.json();
                message = errorData.error || message;
            } catch (error) {}
            throw new Error(message);
        }

        const buffer = await response.arrayBuffer();
        const signature = new TextDecoder("utf-8").decode(buffer.slice(0, 4));
        if (signature !== "%PDF") {
            throw new Error("Downloaded file is not a valid PDF.");
        }

        const blob = new Blob([buffer], { type: "application/pdf" });
        const blobUrl = window.URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = blobUrl;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.setTimeout(() => window.URL.revokeObjectURL(blobUrl), 1000);
    };

    const animateCounts = () => {
        if (prefersReducedMotion) return;
        document.querySelectorAll("[data-count-to]").forEach((element) => {
            const target = Number(element.dataset.countTo || 0);
            const prefix = element.dataset.prefix || "";
            const suffix = element.dataset.suffix || "";
            const decimals = Number(element.dataset.decimals || 0);
            let frame = 0;
            const steps = 30;

            const tick = () => {
                frame += 1;
                const value = target * (frame / steps);
                element.textContent = `${prefix}${value.toFixed(decimals)}${suffix}`;
                if (frame < steps) requestAnimationFrame(tick);
                else element.textContent = `${prefix}${target.toFixed(decimals)}${suffix}`;
            };

            tick();
        });
    };

    const animateProgress = () => {
        document.querySelectorAll("[data-progress]").forEach((element) => {
            const target = Math.max(0, Math.min(100, Number(element.dataset.progress || 0)));
            if (prefersReducedMotion) {
                element.style.width = `${target}%`;
                return;
            }
            window.setTimeout(() => {
                element.style.width = `${target}%`;
            }, 180);
        });
    };

    const initNav = () => {
        const toggle = document.querySelector("[data-nav-toggle]");
        if (toggle) toggle.addEventListener("click", () => document.body.classList.toggle("nav-open"));
    };

    const initModals = () => {
        document.querySelectorAll("[data-open-modal]").forEach((button) => {
            button.addEventListener("click", () => {
                const modal = document.getElementById(button.dataset.openModal);
                if (modal) modal.classList.add("is-open");
            });
        });

        document.querySelectorAll("[data-close-modal]").forEach((button) => {
            button.addEventListener("click", () => button.closest(".modal")?.classList.remove("is-open"));
        });

        document.querySelectorAll(".modal").forEach((modal) => {
            modal.addEventListener("click", (event) => {
                if (event.target === modal) modal.classList.remove("is-open");
            });
        });
    };

    const initAuthPage = () => {
        const authPanel = document.querySelector(".auth-panel");
        const loginView = document.getElementById("login-view");
        const registerView = document.getElementById("register-view");
        const loginTab = document.querySelector("[data-auth-tab='login']");
        const registerTab = document.querySelector("[data-auth-tab='register']");
        const initialUserView = authPanel?.dataset.initialUserView === "register" ? "register" : "login";

        const showView = (view) => {
            if (!loginView || !registerView || !loginTab || !registerTab) return;
            const loginActive = view === "login";
            loginView.hidden = !loginActive;
            registerView.hidden = loginActive;
            loginTab.classList.toggle("active", loginActive);
            registerTab.classList.toggle("active", !loginActive);
            loginTab.setAttribute("aria-selected", loginActive ? "true" : "false");
            registerTab.setAttribute("aria-selected", !loginActive ? "true" : "false");
        };

        loginTab?.addEventListener("click", () => showView("login"));
        registerTab?.addEventListener("click", () => showView("register"));
        showView(initialUserView);
    };

    const initHomePage = () => {
        const form = document.getElementById("planner-search-form");
        const dashboardDataNode = document.getElementById("home-dashboard-data");
        const dashboardData = dashboardDataNode ? JSON.parse(dashboardDataNode.textContent) : null;
        let userLat = Number(dashboardData?.user_origin?.lat) || null;
        let userLon = Number(dashboardData?.user_origin?.lon) || null;
        
        // Use default Mumbai location only if no saved location
        const defaultLat = 19.0760;
        const defaultLon = 72.8777;

        if (!userLat || !userLon) {
            // Try to detect browser location if not already saved
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(
                    async (position) => {
                        userLat = position.coords.latitude;
                        userLon = position.coords.longitude;
                        
                        // Save detected location to backend
                        try {
                            await fetch("/save-location", {
                                method: "POST",
                                headers: { "Content-Type": "application/json" },
                                body: JSON.stringify({
                                    latitude: userLat,
                                    longitude: userLon
                                })
                            });
                        } catch (e) {
                            console.log("Could not save detected location:", e);
                        }
                    },
                    () => {
                        // Fallback to default Mumbai location
                        userLat = defaultLat;
                        userLon = defaultLon;
                    },
                    {
                        enableHighAccuracy: true,
                        timeout: 8000,
                        maximumAge: 0
                    }
                );
            } else {
                // Geolocation not available, use default
                userLat = defaultLat;
                userLon = defaultLon;
            }
        } else {
            // User has saved location, try to update it in background
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(
                    async (position) => {
                        const newLat = position.coords.latitude;
                        const newLon = position.coords.longitude;
                        // Only update if significantly different (> 100m)
                        const dist = Math.sqrt(Math.pow(newLat - userLat, 2) + Math.pow(newLon - userLon, 2));
                        if (dist > 0.001) {
                            userLat = newLat;
                            userLon = newLon;
                            try {
                                await fetch("/save-location", {
                                    method: "POST",
                                    headers: { "Content-Type": "application/json" },
                                    body: JSON.stringify({
                                        latitude: userLat,
                                        longitude: userLon
                                    })
                                });
                            } catch (e) {
                                console.log("Could not update location:", e);
                            }
                        }
                    },
                    () => {},
                    { enableHighAccuracy: true, timeout: 5000, maximumAge: 30000 }
                );
            }
        }

        if (dashboardData) {
            queueChart("user-activity-chart", () => ({
                type: "line",
                data: {
                    labels: dashboardData.weekly_trip_activity.map((item) => item.label),
                    datasets: [
                        {
                            label: "Trips",
                            data: dashboardData.weekly_trip_activity.map((item) => item.value),
                            borderColor: chartPalette[0],
                            backgroundColor: createVerticalGradient("user-activity-chart", "rgba(26, 77, 46, 0.22)", "rgba(26, 77, 46, 0.03)"),
                            fill: true,
                            tension: 0.35,
                            borderWidth: 2
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        tooltip: chartTooltipTheme
                    },
                    scales: {
                        x: { grid: { display: false } },
                        y: { beginAtZero: true, ticks: { precision: 0 } }
                    }
                }
            }));

            queueChart("user-mode-chart", () => ({
                type: "doughnut",
                data: {
                    labels: dashboardData.mode_mix.map((item) => item.label),
                    datasets: [
                        {
                            data: dashboardData.mode_mix.map((item) => item.value),
                            backgroundColor: chartPalette,
                            borderWidth: 0
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    cutout: "70%",
                    plugins: {
                        legend: { position: "bottom" },
                        tooltip: chartTooltipTheme
                    }
                }
            }));
        }

        form?.addEventListener("submit", (event) => {
            event.preventDefault();
            const input = document.getElementById("destination-input");
            if (!input || !input.value.trim()) return;
            const query = new URLSearchParams({
                dest: input.value.trim(),
                lat: userLat,
                lon: userLon
            });
            window.location.href = `/route-planner?${query.toString()}`;
        });
    };

    const initLocationPage = () => {
        const button = document.getElementById("request-location-access");
        const statusNode = document.getElementById("location-permission-status");
        if (!button) return;

        button.addEventListener("click", () => {
            if (!navigator.geolocation) {
                if (statusNode) statusNode.textContent = "Browser geolocation is unavailable on this device.";
                showToast("Geolocation is unavailable.");
                return;
            }

            setButtonState(button, "loading", { loading: "Detecting location..." });
            if (statusNode) statusNode.textContent = "Requesting high-accuracy location from your browser.";

            navigator.geolocation.getCurrentPosition(async (position) => {
                try {
                    const response = await fetch("/save-location", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({
                            latitude: position.coords.latitude,
                            longitude: position.coords.longitude,
                        })
                    });
                    const data = await response.json();
                    if (!response.ok || !data.success) {
                        throw new Error(data.message || "Could not save location.");
                    }

                    setButtonState(button, "success", { success: "Location Saved" });
                    if (statusNode) statusNode.textContent = "Location saved successfully. Redirecting to your workspace.";
                    window.setTimeout(() => {
                        window.location.href = "/home";
                    }, 500);
                } catch (error) {
                    setButtonState(button, "idle");
                    if (statusNode) statusNode.textContent = error.message;
                    showToast(error.message);
                }
            }, (error) => {
                setButtonState(button, "idle");
                const message = error.code === 1
                    ? "Location permission was denied. You can continue without GPS."
                    : "Could not determine your location accurately. Please try again.";
                if (statusNode) statusNode.textContent = message;
                showToast(message);
            }, {
                enableHighAccuracy: true,
                timeout: 12000,
                maximumAge: 0
            });
        });
    };

    const initRoutePlannerPage = () => {
        const configNode = document.getElementById("route-planner-data");
        const mapFrame = document.getElementById("route-map");
        const summary = document.getElementById("comparison-summary");
        const searchForm = document.getElementById("destination-search-form");
        const config = configNode ? JSON.parse(configNode.textContent) : null;

        // Format all time displays on page load
        const formatTimeDisplays = () => {
            document.querySelectorAll(".route-card").forEach((card) => {
                const timeValue = Number(card.dataset.time) || 0;
                // Update metric card
                const metricValue = card.querySelector(".metric-value.small");
                if (metricValue) metricValue.textContent = formatDuration(timeValue);
                // Update comparison bar display
                const timeRow = Array.from(card.querySelectorAll(".comparison-bars .row")).find(r => r.textContent.includes("Time"));
                if (timeRow) {
                    const span = timeRow.querySelector(".mono");
                    if (span) span.textContent = formatDuration(timeValue);
                }
            });
        };
        formatTimeDisplays();

        if (config && mapFrame) {
            const bbox = `${config.dest_lon - 0.03},${config.dest_lat - 0.03},${config.dest_lon + 0.03},${config.dest_lat + 0.03}`;
            mapFrame.src = `https://www.openstreetmap.org/export/embed.html?bbox=${bbox}&layer=mapnik&marker=${config.dest_lat},${config.dest_lon}`;
        }

        document.querySelectorAll("[data-pref]").forEach((button) => {
            button.addEventListener("click", () => {
                document.querySelectorAll("[data-pref]").forEach((item) => item.classList.toggle("active", item === button));
                const cards = [...document.querySelectorAll(".route-card")];
                const preference = button.dataset.pref;
                const ordered = cards.sort((a, b) => Number(a.dataset[preference] || 0) - Number(b.dataset[preference] || 0));
                const container = document.getElementById("route-grid");
                ordered.forEach((card, index) => {
                    card.classList.toggle("recommended", index === 0);
                    container?.appendChild(card);
                });
            });
        });

        document.querySelectorAll("[data-compare-route]").forEach((button) => {
            button.addEventListener("click", () => {
                const card = button.closest(".route-card");
                if (!card || !summary) return;

                // Get all routes from the grid for full comparison
                const allCards = document.querySelectorAll(".route-card");
                const comparisonRows = Array.from(allCards)
                    .map((c) => `
                        <div class="comparison-row ${c === card ? "highlighted" : ""}">
                            <div class="col-vehicle"><strong>${c.dataset.vehicle}</strong></div>
                            <div class="col-time">${formatDuration(c.dataset.time)}</div>
                            <div class="col-cost">Rs.${Math.round(Number(c.dataset.cost))}</div>
                            <div class="col-co2">${gramsToKg(c.dataset.co2)} kg</div>
                        </div>
                    `)
                    .join("");

                summary.innerHTML = `
                    <div class="comparison-table">
                        <div class="comparison-header">
                            <div class="col-vehicle">Transport Mode</div>
                            <div class="col-time">Travel Time</div>
                            <div class="col-cost">Cost</div>
                            <div class="col-co2">CO₂ Emissions</div>
                        </div>
                        ${comparisonRows}
                    </div>
                `;
                document.getElementById("comparison-modal")?.classList.add("is-open");
            });
        });

        document.querySelectorAll("[data-select-route]").forEach((button) => {
            button.addEventListener("click", async () => {
                const card = button.closest(".route-card");
                if (!card || !config) return;
                try {
                    const response = await fetch("/api/save-trip", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({
                            destination: config.destination,
                            mode: card.dataset.vehicle,
                            distance_km: config.distance,
                            co2: Number(card.dataset.co2),
                            cost: Number(card.dataset.cost)
                        })
                    });
                    if (!response.ok) throw new Error("Trip save failed");
                    const query = new URLSearchParams({
                        destination: config.destination,
                        vehicle: card.dataset.vehicle,
                        dest_lat: config.dest_lat,
                        dest_lon: config.dest_lon,
                        distance: config.distance
                    });
                    window.location.href = `/map-navigation?${query.toString()}`;
                } catch (error) {
                    showToast("Could not save trip. Please try again.");
                }
            });
        });

        searchForm?.addEventListener("submit", (event) => {
            event.preventDefault();
            const input = document.getElementById("new-destination-input");
            if (!input || !input.value.trim() || !config) return;
            const query = new URLSearchParams({
                dest: input.value.trim(),
                lat: config.user_lat,
                lon: config.user_lon
            });
            window.location.href = `/route-planner?${query.toString()}`;
        });
    };

    const initProfilePage = () => {
        const configNode = document.getElementById("profile-data");
        const chartRoot = document.getElementById("impact-chart-bars");
        const details = document.getElementById("profile-details-panel");
        const shareButton = document.getElementById("share-profile");
        const data = configNode ? JSON.parse(configNode.textContent) : null;

        const renderBars = (series, labels) => {
            if (!chartRoot) return;
            const max = Math.max(...series, 1);
            chartRoot.innerHTML = series.map((value, index) => `
                <div class="chart-bar">
                    <div class="chart-bar-column"><div class="chart-bar-value" style="height:${Math.max(12, (value / max) * 100)}%"></div></div>
                    <div class="chart-bar-label">${labels[index]}</div>
                </div>
            `).join("");
        };

        if (data) {
            renderBars(data.weekly, ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]);
            document.querySelectorAll("[data-chart-view]").forEach((button) => {
                button.addEventListener("click", () => {
                    document.querySelectorAll("[data-chart-view]").forEach((item) => item.classList.toggle("active", item === button));
                    if (button.dataset.chartView === "monthly") renderBars(data.monthly, ["W1", "W2", "W3", "W4"]);
                    else renderBars(data.weekly, ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]);
                });
            });

            document.querySelectorAll("[data-trip-index]").forEach((button) => {
                button.addEventListener("click", () => {
                    const trip = data.trips[Number(button.dataset.tripIndex)];
                    if (!trip || !details) return;
                    details.innerHTML = `
                        <div class="mini-grid">
                            <div class="metric-card"><div class="meta-label">Destination</div><div class="metric-value small">${trip.destination}</div></div>
                            <div class="metric-card"><div class="meta-label">Mode</div><div class="metric-value small">${trip.mode}</div></div>
                            <div class="metric-card"><div class="meta-label">Cost</div><div class="metric-value small">Rs.${Math.round(trip.cost)}</div></div>
                            <div class="metric-card"><div class="meta-label">CO2</div><div class="metric-value small">${gramsToKg(trip.co2_emitted)} kg</div></div>
                        </div>
                    `;
                });
            });
        }

        shareButton?.addEventListener("click", async () => {
            try {
                await navigator.clipboard.writeText(window.location.href);
                showToast("Profile link copied.");
            } catch (error) {
                showToast("Could not copy link.");
            }
        });
    };

    const initAdminPage = () => {
        const dashboardDataNode = document.getElementById("admin-dashboard-data");
        const dashboardData = dashboardDataNode ? JSON.parse(dashboardDataNode.textContent) : null;
        const selector = document.getElementById("model-selector");
        const defaultModel = selector?.dataset.defaultModel || "model";
        const retrainButton = document.getElementById("retrain-model");
        const refreshButton = document.getElementById("refresh-metrics");
        const retrainSidebarButton = document.getElementById("retrain-sidebar");
        const refreshSidebarButton = document.getElementById("refresh-sidebar");
        const userSearch = document.getElementById("user-search");
        const userStatusFilter = document.getElementById("user-status-filter");
        const userRows = [...document.querySelectorAll("#admin-users-table tbody tr")];
        const metricNodes = [
            {
                label: document.getElementById("model-metric-1-label"),
                value: document.getElementById("model-metric-1-value")
            },
            {
                label: document.getElementById("model-metric-2-label"),
                value: document.getElementById("model-metric-2-value")
            },
            {
                label: document.getElementById("model-metric-3-label"),
                value: document.getElementById("model-metric-3-value")
            },
            {
                label: document.getElementById("model-metric-4-label"),
                value: document.getElementById("model-metric-4-value")
            }
        ];
        const versionNode = document.getElementById("model-version-value");
        const samplesNode = document.getElementById("model-training-samples-value");
        const trainedNode = document.getElementById("model-last-trained-value");
        const selectedNameNode = document.getElementById("model-selected-name");
        const taskTypeNode = document.getElementById("model-task-type");

        const formatPercent = (value) => `${Number(value || 0).toFixed(1)}%`;
        const formatDecimal = (value) => Number(value || 0).toFixed(3);
        const formatInteger = (value) => Number(value || 0).toLocaleString();

        const renderMetrics = (metrics) => {
            if (!metrics) return;

            const cards = metrics.task_type === "regression"
                ? [
                    { label: "R² Score", value: formatDecimal(metrics.r2) },
                    { label: "MAE", value: formatDecimal(metrics.mae) },
                    { label: "RMSE", value: formatDecimal(metrics.rmse) },
                    { label: "Training Samples", value: formatInteger(metrics.training_samples) }
                ]
                : [
                    { label: "Accuracy", value: formatPercent(metrics.accuracy) },
                    { label: "Precision", value: formatPercent(metrics.precision) },
                    { label: "Recall", value: formatPercent(metrics.recall) },
                    { label: "F1 Score", value: formatPercent(metrics.f1_score) }
                ];

            if (metrics.task_type === "regression" && cards[0]) {
                cards[0].label = "R\u00B2 Score";
                cards[0].label = "R² Score";
            }

            if (metrics.task_type === "regression" && cards[0]) {
                cards[0].label = "R\u00B2 Score";
            }

            metricNodes.forEach((node, index) => {
                const card = cards[index];
                if (!node.label || !node.value || !card) return;
                node.label.textContent = card.label;
                node.value.textContent = card.value;
                const numericValue = Number(card.value.replace(/[^0-9.]/g, "")) || 0;
                let maxValue = 100;
                const label = card.label;
                if (label.includes("\u00B2")) maxValue = 1;
                if (card.label.includes("\u00B2")) maxValue = 1;
                if (card.label.includes("R²") || card.label.includes("R2")) maxValue = 1;
                else if (card.label.includes("MAE") || card.label.includes("RMSE")) maxValue = Math.max(numericValue * 1.5, 5);
                else if (card.label.includes("Training")) maxValue = Math.max(numericValue, 1);
                setCircularMetric(`model-metric-ring-${index + 1}`, node.value.id, node.label.id, card.label, numericValue, card.value, maxValue);
            });

            if (versionNode) versionNode.textContent = metrics.version || "N/A";
            if (samplesNode) samplesNode.textContent = formatInteger(metrics.training_samples);
            if (trainedNode) trainedNode.textContent = metrics.last_trained || "N/A";
            if (selectedNameNode) selectedNameNode.textContent = metrics.name || selector?.value || defaultModel;
            if (taskTypeNode) taskTypeNode.textContent = metrics.task_type === "regression" ? "Regression" : "Classification";
        };

        const applyMetrics = (metrics) => {
            if (!metrics) return;

            const cards = metrics.task_type === "regression"
                ? [
                    { label: "R\u00B2 Score", value: formatDecimal(metrics.r2) },
                    { label: "MAE", value: formatDecimal(metrics.mae) },
                    { label: "RMSE", value: formatDecimal(metrics.rmse) },
                    { label: "Training Samples", value: formatInteger(metrics.training_samples) }
                ]
                : [
                    { label: "Accuracy", value: formatPercent(metrics.accuracy) },
                    { label: "Precision", value: formatPercent(metrics.precision) },
                    { label: "Recall", value: formatPercent(metrics.recall) },
                    { label: "F1 Score", value: formatPercent(metrics.f1_score) }
                ];

            metricNodes.forEach((node, index) => {
                const card = cards[index];
                if (!node.label || !node.value || !card) return;

                node.label.textContent = card.label;
                node.value.textContent = card.value;

                const numericValue = Number(card.value.replace(/[^0-9.]/g, "")) || 0;
                let maxValue = 100;
                if (card.label.includes("\u00B2") || card.label.includes("R2")) maxValue = 1;
                else if (card.label.includes("MAE") || card.label.includes("RMSE")) maxValue = Math.max(numericValue * 1.5, 5);
                else if (card.label.includes("Training")) maxValue = Math.max(numericValue, 1);

                setCircularMetric(
                    `model-metric-ring-${index + 1}`,
                    node.value.id,
                    node.label.id,
                    card.label,
                    numericValue,
                    card.value,
                    maxValue
                );
            });

            if (versionNode) versionNode.textContent = metrics.version || "N/A";
            if (samplesNode) samplesNode.textContent = formatInteger(metrics.training_samples);
            if (trainedNode) trainedNode.textContent = metrics.last_trained || "N/A";
            if (selectedNameNode) selectedNameNode.textContent = metrics.name || selector?.value || defaultModel;
            if (taskTypeNode) taskTypeNode.textContent = metrics.task_type === "regression" ? "Regression" : "Classification";
        };

        const fetchMetrics = async (modelName, announce = false) => {
            const response = await fetch(`/api/ml/metrics/${encodeURIComponent(modelName)}`);
            const data = await response.json();
            if (!response.ok || data.error) {
                throw new Error(data.error || "Metrics update failed.");
            }
            applyMetrics(data);
            if (announce) showToast("Metrics updated.");
            return data;
        };

        const loadModelOptions = async () => {
            if (!selector) return;
            const response = await fetch("/api/ml/health");
            const data = await response.json();
            if (!response.ok || data.error || !Array.isArray(data.models)) {
                throw new Error(data.error || "Could not load model options.");
            }

            const selectedValue = selector.value || data.default_model || defaultModel;
            selector.innerHTML = data.models.map((modelName) => {
                const selected = modelName === selectedValue ? " selected" : "";
                return `<option value="${modelName}"${selected}>${modelName}</option>`;
            }).join("");
            selector.value = data.models.includes(selectedValue) ? selectedValue : (data.default_model || defaultModel);
            if (selectedNameNode) selectedNameNode.textContent = selector.value;
        };

        loadModelOptions()
            .then(() => fetchMetrics(selector?.value || defaultModel))
            .catch(() => {});

        selector?.addEventListener("change", async () => {
            try {
                if (selectedNameNode) selectedNameNode.textContent = selector.value;
                setButtonState(refreshButton, "loading", { loading: "Refreshing..." });
                await fetchMetrics(selector.value);
                setButtonState(refreshButton, "success", { success: "Updated" });
                resetButtonStateLater(refreshButton);
            } catch (error) {
                setButtonState(refreshButton, "idle");
                showToast(error.message);
            }
        });

        document.getElementById("retrain-model")?.addEventListener("click", async () => {
            const selectedModel = selector?.value || defaultModel;
            try {
                setButtonState(retrainButton, "loading", { loading: "Retraining..." });
                const response = await fetch(`/api/ml/retrain/${encodeURIComponent(selectedModel)}`, { method: "POST" });
                const data = await response.json();
                if (!response.ok || data.error) {
                    throw new Error(data.error || "Model retrain failed.");
                }
                applyMetrics(data);
                setButtonState(retrainButton, "success", { success: "Retrained" });
                resetButtonStateLater(retrainButton);
                showToast(`${selectedModel} retrained.`);
            } catch (error) {
                setButtonState(retrainButton, "idle");
                showToast(error.message);
            }
        });

        document.getElementById("refresh-metrics")?.addEventListener("click", async () => {
            const selectedModel = selector?.value || defaultModel;
            try {
                setButtonState(refreshButton, "loading", { loading: "Refreshing..." });
                await fetchMetrics(selectedModel, true);
                setButtonState(refreshButton, "success", { success: "Updated" });
                resetButtonStateLater(refreshButton);
            } catch (error) {
                setButtonState(refreshButton, "idle");
                showToast(error.message);
            }
        });

        document.getElementById("export-analytics")?.addEventListener("click", async () => {
            try {
                const button = document.getElementById("export-analytics");
                setButtonState(button, "loading", { loading: "Exporting..." });
                await downloadPdfReport("/api/export-analytics", "raahi-analytics-report.pdf");
                setButtonState(button, "success", { success: "Downloaded" });
                resetButtonStateLater(button);
                showToast("Analytics report downloaded.");
            } catch (error) {
                setButtonState(document.getElementById("export-analytics"), "idle");
                showToast(error.message);
            }
        });

        document.getElementById("export-users")?.addEventListener("click", async () => {
            try {
                const button = document.getElementById("export-users");
                setButtonState(button, "loading", { loading: "Exporting..." });
                await downloadPdfReport("/api/export-users", "raahi-users-report.pdf");
                setButtonState(button, "success", { success: "Downloaded" });
                resetButtonStateLater(button);
                showToast("Users report downloaded.");
            } catch (error) {
                setButtonState(document.getElementById("export-users"), "idle");
                showToast(error.message);
            }
        });

        const syncMetricRings = () => {
            metricNodes.forEach((node, index) => {
                if (!node.label || !node.value) return;
                const label = node.label.textContent || "";
                const displayValue = node.value.textContent || "";
                const numericValue = Number(displayValue.replace(/[^0-9.]/g, "")) || 0;
                let maxValue = 100;
                if (label.includes("R2") || label.includes("R²")) maxValue = 1;
                else if (label.includes("MAE") || label.includes("RMSE")) maxValue = Math.max(numericValue * 1.5, 5);
                else if (label.includes("Training")) maxValue = Math.max(numericValue, 1);
                setCircularMetric(`model-metric-ring-${index + 1}`, node.value.id, node.label.id, label, numericValue, displayValue, maxValue);
            });
        };

        if (dashboardData) {
            queueChart("admin-user-growth-chart", () => ({
                type: "line",
                data: {
                    labels: dashboardData.user_growth.map((item) => item.label),
                    datasets: [
                        {
                            label: "Total users",
                            data: dashboardData.user_growth.map((item) => item.value),
                            borderColor: chartPalette[0],
                            backgroundColor: createVerticalGradient("admin-user-growth-chart", "rgba(26, 77, 46, 0.18)", "rgba(20, 47, 50, 0.04)"),
                            fill: true,
                            tension: 0.35,
                            borderWidth: 2,
                            pointRadius: 4,
                            pointHoverRadius: 5,
                            pointBackgroundColor: chartPalette[0],
                            pointBorderColor: "#FFFFFF",
                            pointBorderWidth: 2
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        tooltip: chartTooltipTheme
                    },
                    scales: {
                        x: { grid: { display: false } },
                        y: { beginAtZero: true, ticks: { precision: 0 } }
                    }
                }
            }));

            queueChart("admin-transport-mode-chart", () => ({
                type: "doughnut",
                data: {
                    labels: dashboardData.transport_mode_mix.map((item) => item.label),
                    datasets: [
                        {
                            data: dashboardData.transport_mode_mix.map((item) => item.value),
                            backgroundColor: chartPalette,
                            borderWidth: 0
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    cutout: "70%",
                    plugins: {
                        legend: { position: "bottom" },
                        tooltip: chartTooltipTheme
                    }
                }
            }));

            queueChart("admin-prediction-chart", () => ({
                type: "bar",
                data: {
                    labels: dashboardData.prediction_distribution.map((item) => item.label),
                    datasets: [
                        {
                            label: "Predictions",
                            data: dashboardData.prediction_distribution.map((item) => item.value),
                            backgroundColor: createVerticalGradient("admin-prediction-chart", "rgba(59, 130, 246, 0.85)", "rgba(59, 130, 246, 0.35)"),
                            borderRadius: 10
                        }
                    ]
                },
                options: {
                    indexAxis: "y",
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        tooltip: chartTooltipTheme
                    },
                    scales: {
                        x: { beginAtZero: true, ticks: { precision: 0 } },
                        y: { grid: { display: false } }
                    }
                }
            }));

            queueChart("admin-feature-chart", () => ({
                type: "bar",
                data: {
                    labels: dashboardData.feature_importance.map((item) => item.label),
                    datasets: [
                        {
                            label: "Importance",
                            data: dashboardData.feature_importance.map((item) => item.value),
                            backgroundColor: createVerticalGradient("admin-feature-chart", "rgba(26, 77, 46, 0.9)", "rgba(47, 123, 77, 0.4)"),
                            borderRadius: 10
                        }
                    ]
                },
                options: {
                    indexAxis: "y",
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        tooltip: chartTooltipTheme
                    },
                    scales: {
                        x: { beginAtZero: true },
                        y: { grid: { display: false } }
                    }
                }
            }));
        }

        const filterUsers = () => {
            const query = (userSearch?.value || "").trim().toLowerCase();
            const status = userStatusFilter?.value || "all";
            let visibleCount = 0;
            userRows.forEach((row) => {
                const matchesQuery = !query || row.dataset.userName.includes(query) || row.dataset.userContact.includes(query);
                const matchesStatus = status === "all" || row.dataset.userStatus === status;
                const isVisible = matchesQuery && matchesStatus;
                row.hidden = !isVisible;
                if (isVisible) visibleCount += 1;
            });
            const resultsNode = document.getElementById("user-results-count");
            if (resultsNode) resultsNode.textContent = `Showing ${visibleCount}`;
        };

        const debouncedFilterUsers = debounce(filterUsers, 120);

        userSearch?.addEventListener("input", debouncedFilterUsers);
        userStatusFilter?.addEventListener("change", filterUsers);
        document.querySelectorAll("[data-table-action]").forEach((button) => {
            button.addEventListener("click", () => {
                const action = button.dataset.tableAction || "view";
                const row = button.closest("tr");
                const userName = row?.querySelector("td")?.textContent?.trim() || "user";
                showToast(`${action.charAt(0).toUpperCase() + action.slice(1)} action for ${userName} is ready for wiring.`);
            });
        });

        retrainSidebarButton?.addEventListener("click", () => document.getElementById("retrain-model")?.click());
        refreshSidebarButton?.addEventListener("click", () => document.getElementById("refresh-metrics")?.click());

        syncMetricRings();
        filterUsers();
    };

    const initNavigationPage = () => {
        const configNode = document.getElementById("navigation-data");
        const frame = document.getElementById("navigation-map");
        const config = configNode ? JSON.parse(configNode.textContent) : null;
        if (!config) return;

        if (frame) {
            const bbox = `${config.dest_lon - 0.02},${config.dest_lat - 0.02},${config.dest_lon + 0.02},${config.dest_lat + 0.02}`;
            frame.src = `https://www.openstreetmap.org/export/embed.html?bbox=${bbox}&layer=mapnik&marker=${config.dest_lat},${config.dest_lon}`;
        }

        let watchId = null;
        let active = true;
        let travelled = 0;
        let lastPosition = null;
        const speedNode = document.getElementById("current-speed");
        const distanceNode = document.getElementById("current-distance");
        const etaNode = document.getElementById("current-eta");
        const progressNode = document.getElementById("route-progress-fill");
        const statusNode = document.getElementById("tracking-status");

        const distanceBetween = (lat1, lon1, lat2, lon2) => {
            const r = 6371;
            const dLat = (lat2 - lat1) * Math.PI / 180;
            const dLon = (lon2 - lon1) * Math.PI / 180;
            const a = Math.sin(dLat / 2) ** 2 + Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * Math.sin(dLon / 2) ** 2;
            return r * (2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a)));
        };

        if (navigator.geolocation) {
            watchId = navigator.geolocation.watchPosition((position) => {
                if (!active) return;
                const { latitude, longitude, speed } = position.coords;
                if (lastPosition) travelled += distanceBetween(lastPosition.lat, lastPosition.lon, latitude, longitude);
                lastPosition = { lat: latitude, lon: longitude };
                if (speedNode) speedNode.textContent = `${((speed || 0) * 3.6).toFixed(1)} km/h`;
                if (distanceNode) distanceNode.textContent = `${travelled.toFixed(1)} km`;
                const total = Math.max(config.distance, 0.1);
                const progress = Math.min(100, (travelled / total) * 100);
                if (progressNode) progressNode.style.width = `${progress}%`;
                if (etaNode && speed && speed > 0) {
                    const eta = new Date(Date.now() + ((Math.max(total - travelled, 0) / (speed * 3.6)) * 60 * 60000));
                    etaNode.textContent = eta.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
                }
            }, () => {
                if (statusNode) statusNode.textContent = "Tracking unavailable";
            }, { enableHighAccuracy: true });
        }

        document.getElementById("pause-tracking")?.addEventListener("click", () => {
            active = !active;
            const pauseButton = document.getElementById("pause-tracking");
            if (pauseButton) pauseButton.textContent = active ? "Pause Tracking" : "Resume Tracking";
            if (statusNode) statusNode.textContent = active ? "Live tracking active" : "Tracking paused";
        });

        document.getElementById("end-navigation")?.addEventListener("click", () => {
            if (watchId !== null) navigator.geolocation.clearWatch(watchId);
            window.location.href = "/home";
        });

        document.getElementById("share-location")?.addEventListener("click", async () => {
            const url = `https://www.openstreetmap.org/?mlat=${config.dest_lat}&mlon=${config.dest_lon}&zoom=14`;
            try {
                if (navigator.share) await navigator.share({ title: "Raahi trip", text: `Tracking route to ${config.destination}`, url });
                else {
                    await navigator.clipboard.writeText(url);
                    showToast("Location link copied.");
                }
            } catch (error) {
                showToast("Could not share location.");
            }
        });
    };

    initNav();
    initModals();
    revealElements();
    animateCounts();
    animateProgress();

    if (page === "auth") initAuthPage();
    if (page === "home") initHomePage();
    if (page === "location") initLocationPage();
    if (page === "route-planner") initRoutePlannerPage();
    if (page === "profile") initProfilePage();
    if (page === "admin") initAdminPage();
    if (page === "map-navigation") initNavigationPage();

    window.RaahiUI = { showToast };
})();
