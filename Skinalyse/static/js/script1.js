let stream;

const overlay = document.getElementById("overlay");
const modal = document.getElementById("cameraModal");
const video = document.getElementById("video");
const canvas = document.getElementById("canvas");
const snapBtn = document.getElementById("snap");
const uploadBtn = document.getElementById("uploadBtn");

/* =========================
   OPEN CAMERA
========================= */
function openCameraModal() {
    overlay.style.display = "block";
    modal.style.display = "block";

    // Smooth animation
    setTimeout(() => {
        modal.classList.add("show");
    }, 10);

    navigator.mediaDevices.getUserMedia({ video: true })
        .then(s => {
            stream = s;
            video.srcObject = stream;
        })
        .catch(() => {
            alert("Camera access denied");
        });
}

/* =========================
   CLOSE CAMERA
========================= */
function closeCameraModal() {
    modal.classList.remove("show");

    setTimeout(() => {
        overlay.style.display = "none";
        modal.style.display = "none";
    }, 300);

    if (stream) {
        stream.getTracks().forEach(track => track.stop());
    }

    resetCamera();
}

/* =========================
   CAPTURE IMAGE
========================= */
snapBtn.addEventListener("click", () => {

    // Flash effect
    const flash = document.createElement("div");
    flash.style.position = "fixed";
    flash.style.inset = "0";
    flash.style.background = "#fff";
    flash.style.opacity = "0.8";
    flash.style.zIndex = "999";
    flash.style.transition = "opacity 0.4s ease";
    document.body.appendChild(flash);

    setTimeout(() => {
        flash.style.opacity = "0";
        setTimeout(() => {
            document.body.removeChild(flash);
        }, 400);
    }, 100);

    const context = canvas.getContext("2d");

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    video.style.display = "none";
    canvas.style.display = "block";

    uploadBtn.disabled = false;
});

/* =========================
   UPLOAD IMAGE
========================= */
uploadBtn.addEventListener("click", () => {

    const capturedImage = canvas.toDataURL("image/png");

    console.log("Captured Image:", capturedImage);

    alert("📸 Image uploaded successfully!");
});

/* =========================
   RESET CAMERA
========================= */
function resetCamera() {
    video.style.display = "block";
    canvas.style.display = "none";
    uploadBtn.disabled = true;
}
