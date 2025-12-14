let usageChart = null;

async function handleUsageSubmit() {
    const usageInput = document.getElementById("usage");
    const usage = Number(usageInput.value);

    if (!usage) {
        document.getElementById("result").innerHTML =
            "<div class='error'>⚠️ Please enter a value.</div>";
        return;
    }

    // 1) Predict cluster
    const predictRes = await fetch("https://water-pattern-detection.onrender.com/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ usage })
    });
    const predictData = await predictRes.json();

    const clusterId = predictData.cluster;
    const description = predictData.description;

    let colorClass = "";
    let title = "";

    if (clusterId === 0) {
        colorClass = "green-card";
        title = "Low / Efficient Usage";
    } else if (clusterId === 1) {
        colorClass = "blue-card";
        title = "Normal / Balanced Usage";
    } else {
        colorClass = "red-card";
        title = "High / Irregular Usage";
    }

    document.getElementById("result").innerHTML = `
        <div class="result-card ${colorClass}">
            <h3>Cluster ${clusterId}: ${title}</h3>
            <p>${description}</p>
        </div>
    `;

    // 2) Log usage with today's date
    await fetch("http://127.0.0.1:8000/log-usage", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ usage })
    });

    // 3) Refresh summary & chart
    await refreshSummary();
    await refreshHistoryChart();
}

async function refreshSummary() {
    const res = await fetch("https://water-pattern-detection.onrender.com/summary");
    const data = await res.json();

    const summaryEl = document.getElementById("summary-text");

    if (!data.has_data) {
        summaryEl.textContent = "No usage data logged yet.";
        return;
    }

    const avg = data.average_usage.toFixed(1);
    const latest = data.latest_usage.toFixed(1);
    const statusLines = [];

    statusLines.push(`Average usage: ${avg} L/day`);
    statusLines.push(`Latest usage: ${latest} L`);

    if (data.is_spike) {
        statusLines.push("⚠️ Recent spike detected compared to your average.");
    } else {
        statusLines.push("✅ No unusual spike detected.");
    }

    if (data.suspected_leak) {
        statusLines.push("🚨 Pattern suggests possible leakage or abnormal wastage.");
    }

    statusLines.push(`Efficiency: ${data.efficiency_level}`);

    summaryEl.innerHTML = statusLines.join("<br>");
}

async function refreshHistoryChart() {
    const res = await fetch("https://water-pattern-detection.onrender.com/history?limit=30");
    const data = await res.json();

    const history = data.history || [];
    const infoText = document.getElementById("trend-empty");

    if (history.length === 0) {
        infoText.style.display = "block";
        if (usageChart) {
            usageChart.destroy();
            usageChart = null;
        }
        return;
    }

    infoText.style.display = "none";

    const labels = history.map(item => item.date);
    const values = history.map(item => item.usage);

    const ctx = document.getElementById("usageChart").getContext("2d");

    if (usageChart) {
        usageChart.data.labels = labels;
        usageChart.data.datasets[0].data = values;
        usageChart.update();
        return;
    }

    usageChart = new Chart(ctx, {
        type: "line",
        data: {
            labels,
            datasets: [{
                label: "Daily Usage (L)",
                data: values,
                fill: false,
                tension: 0.25
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false }
            },
            scales: {
                x: {
                    ticks: { autoSkip: true, maxTicksLimit: 7 }
                },
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

// Load summary & history on page load
window.addEventListener("load", () => {
    refreshSummary();
    refreshHistoryChart();
});



async function getAiInsights() {
    const box = document.getElementById("ai-insights-text");
    box.innerHTML = "Analyzing your water usage…";

    try {
        const res = await fetch("https://water-pattern-detection.onrender.com/ai-insights");
        const data = await res.json();

        box.innerHTML = data.insight
            .replace(/\n\n/g, "<br><br>")
            .replace(/(\d\.\s[A-Z ]+)/g, "<br><b>$1</b><br>");
      
    } catch (err) {
        box.innerHTML = "⚠️ Unable to generate AI insights right now.";
        console.error(err);
    }
}





function toggleAiInsights() {
    const box = document.getElementById("ai-insights-text");
    const btn = document.querySelector(".ai-expand-btn");

    if (!box.classList.contains("expanded")) {
        box.classList.add("expanded");
        btn.textContent = "Collapse";
    } else {
        box.classList.remove("expanded");
        btn.textContent = "Expand";
    }
}











async function askUsageQuestion() {
    const input = document.getElementById("ai-question-input");
    const output = document.getElementById("ai-question-answer");

    const question = input.value.trim();
    if (!question) {
        output.innerHTML = "Please enter a question.";
        return;
    }

    output.innerHTML = "Thinking…";

    try {
        const res = await fetch("https://water-pattern-detection.onrender.com/ai-question", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ question })
        });

        const data = await res.json();
        output.innerHTML = data.answer;
    } catch (err) {
        output.innerHTML = "Unable to answer right now.";
        console.error(err);
    }
}
