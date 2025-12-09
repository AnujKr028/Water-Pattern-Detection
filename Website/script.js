async function predictCluster() {
    let usage = document.getElementById("usage").value;

    if (!usage) {
        document.getElementById("result").innerHTML =
            "<div class='error'>⚠️ Please enter a value.</div>";
        return;
    }

    try {
        const response = await fetch("http://127.0.0.1:8000/predict", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ usage: Number(usage) })
        });

        const data = await response.json();

        const clusterId = data.cluster.cluster;
        const description = data.cluster.description;

        let colorClass = "";
        let title = "";

        if (clusterId === 0) {
            colorClass = "green-card";
            title = "Low / Efficient Usage";
        } 
        else if (clusterId === 1) {
            colorClass = "blue-card";
            title = "Normal / Balanced Usage";
        }
        else if (clusterId === 2) {
            colorClass = "red-card";
            title = "High / Irregular Usage";
        }

        document.getElementById("result").innerHTML = `
            <div class="result-card ${colorClass}">
                <h3>Cluster ${clusterId}: ${title}</h3>
                <p>${description}</p>
            </div>
        `;
        
    } catch (error) {
        document.getElementById("result").innerHTML =
            "<div class='error'>❌ API Error: Check if FastAPI is running.</div>";
    }
}
