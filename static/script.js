function show(id) {
    document.querySelectorAll(".content > div").forEach(x => x.style.display = "none");
    document.getElementById(id).style.display = "block";
}

function previewImage() {
    const input = document.getElementById("thermalInput");
    if (!input.files[0]) {
        return;
    }

    const reader = new FileReader();
    reader.onload = function(e) {
        document.querySelector(".upload-zone").style.display = "none";
        const img = document.getElementById("previewImage");
        img.src = e.target.result;
        img.style.display = "block";
        document.getElementById("imageActions").style.display = "flex";
    };
    reader.readAsDataURL(input.files[0]);
}

function replaceImage() {
    document.getElementById("thermalInput").click();
}

function removeImage() {
    document.getElementById("thermalInput").value = "";
    document.getElementById("previewImage").style.display = "none";
    document.querySelector(".upload-zone").style.display = "flex";
    document.getElementById("imageActions").style.display = "none";
    document.getElementById("result").innerHTML = "";
    document.getElementById("assistantResult").innerHTML = "";
}

// --- FIXED & DYNAMIC ANALYSIS FUNCTION ---
function analyzeImage() {
    const input = document.getElementById("thermalInput");
    if (!input.files[0]) {
        alert("Please upload a footprint image first.");
        return;
    }

    // Show a loading status to the user
    document.getElementById("result").innerHTML = `
        <div class="final-result" style="color: #666;">
            Processing thermal signatures... Please wait.
        </div>
    `;
    document.getElementById("assistantResult").innerHTML = "";

    // Prepare the image file packet to send to Python backend
    const formData = new FormData();
    formData.append("file", input.files[0]);

    // Send the image to the backend for real machine learning evaluation
    fetch("/predict", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            document.getElementById("result").innerHTML = `
                <div class="final-result" style="color: red;">
                    Error: ${data.error}
                </div>
            `;
            return;
        }

        // Dynamically update the results based on the model output
        document.getElementById("result").innerHTML = `
            <div class="metric">
                Scan Profile
                <span>Footprint Detected</span>
            </div>
            <div class="metric">
                Diagnostic Output
                <span style="color: ${data.prediction === 'Diabetic' ? '#e74c3c' : '#2ecc71'}; font-weight: bold;">
                    ${data.prediction}
                </div>
            </div>
        `;

        document.getElementById("assistantResult").innerHTML = `
            <h3>AI Summary</h3>
            <ul>
                <li>Image successfully loaded into matrix array.</li>
                <li>Zonal features (Toes, Arch, Heel) extracted.</li>
                <li>Classification profile calculated: <strong>${data.prediction} Footprint Type</strong>.</li>
            </ul>
        `;
    })
    .catch(err => {
        console.error(err);
        document.getElementById("result").innerHTML = `
            <div class="final-result" style="color: red;">
                Failed to contact prediction gateway server.
            </div>
        `;
    });
}