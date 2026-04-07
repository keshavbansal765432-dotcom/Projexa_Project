let stream;
const video = document.getElementById("video");
const canvas = document.getElementById("canvas");
const snapBtn = document.getElementById("snap");
const retakeBtn = document.getElementById("retake");
const cameraAnalyzeBtn = document.getElementById("cameraAnalyze");
const uploadAnalyzeBtn = document.getElementById("uploadAnalyze");
const fileInput = document.getElementById("fileInput");
const fileNameText = document.getElementById("fileName");
const modalOverlay = document.getElementById("modalOverlay");

/* =========================
   MODAL CONTROLS
========================= */
function openModal() {
    modalOverlay.classList.add("active");
    // Show selection by default
    showState("selection");
}

function closeModal() {
    modalOverlay.classList.remove("active");
    stopCamera();
    // Reset file input
    fileInput.value = "";
    fileNameText.textContent = "Drop image here or click to browse";
    uploadAnalyzeBtn.style.display = "none";
}

function showState(state) {
    const states = ["Selection", "Camera", "Upload", "Loading", "Result"];
    states.forEach(s => {
        document.getElementById(`state${s}`).classList.remove("active");
    });
    
    document.getElementById(`state${state.charAt(0).toUpperCase() + state.slice(1)}`).classList.add("active");

    // Camera Init
    if (state === "camera") {
        initCamera();
    } else {
        stopCamera();
    }
}

/* =========================
   CAMERA LOGIC
========================= */
async function initCamera() {
    try {
        stream = await navigator.mediaDevices.getUserMedia({ video: true });
        video.srcObject = stream;
        video.style.display = "block";
        canvas.style.display = "none";
        snapBtn.style.display = "block";
        retakeBtn.style.display = "none";
        cameraAnalyzeBtn.style.display = "none";
    } catch (err) {
        console.error("Camera access error:", err);
        alert("Unable to access camera. Please check permissions.");
        showState("selection");
    }
}

function stopCamera() {
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
    }
}

snapBtn.addEventListener("click", () => {
    const context = canvas.getContext("2d");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    video.style.display = "none";
    canvas.style.display = "block";
    snapBtn.style.display = "none";
    retakeBtn.style.display = "block";
    cameraAnalyzeBtn.style.display = "block";
});

retakeBtn.addEventListener("click", () => {
    video.style.display = "block";
    canvas.style.display = "none";
    snapBtn.style.display = "block";
    retakeBtn.style.display = "none";
    cameraAnalyzeBtn.style.display = "none";
});

/* =========================
   UPLOAD LOGIC
========================= */
fileInput.addEventListener("change", (e) => {
    if (e.target.files.length > 0) {
        fileNameText.textContent = `Selected: ${e.target.files[0].name}`;
        uploadAnalyzeBtn.style.display = "block";
    }
});

/* =========================
   AI ANALYSIS LOGIC
========================= */

// Analyze from Camera
cameraAnalyzeBtn.addEventListener("click", async () => {
    const imageData = canvas.toDataURL("image/png");
    await performAnalysis({ image: imageData });
});

// Analyze from Upload
uploadAnalyzeBtn.addEventListener("click", async () => {
    const formData = new FormData();
    formData.append("file", fileInput.files[0]);
    await performAnalysis(formData, true);
});

async function performAnalysis(data, isUpload = false) {
    showState("loading");

    const fetchOptions = {
        method: "POST",
        body: isUpload ? data : JSON.stringify(data)
    };
    
    if (!isUpload) {
        fetchOptions.headers = { "Content-Type": "application/json" };
    }

    try {
        const response = await fetch("/analyze", fetchOptions);
        if (response.ok) {
            const result = await response.json();
            displayResult(result);
        } else {
            throw new Error("Analysis failed");
        }
    } catch (err) {
        console.error(err);
        alert("Error during analysis. Please try again.");
        showState("selection");
    }
}

function displayResult(res) {
    document.getElementById("resultTitle").textContent = res.result;
    document.getElementById("resultImage").src = `/static/uploads/${res.image}`;
    document.getElementById("resultDesc").textContent = "Based on our AI model, we detected patterns indicating this condition. Please download the report for details.";
    
    // Result image is base basename in JSON
    showState("result");
}

/* =========================
   CONTACT FORM HANDLER
========================= */
const contactForm = document.getElementById("contactForm");
if (contactForm) {
    contactForm.addEventListener("submit", (e) => {
        e.preventDefault();
        const btn = contactForm.querySelector("button");
        const originalText = btn.textContent;
        
        btn.textContent = "✅ Message Sent!";
        btn.style.background = "#4CAF50";
        
        setTimeout(() => {
            btn.textContent = originalText;
            btn.style.background = "";
            contactForm.reset();
        }, 3000);
    });
}
