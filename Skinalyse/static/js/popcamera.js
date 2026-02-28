
let stream;

function openCameraModal() {
    document.getElementById("overlay").style.display = "block";
    document.getElementById("cameraModal").style.display = "block";

    navigator.mediaDevices.getUserMedia({ video: true })
        .then(s => {
            stream = s;
            document.getElementById("video").srcObject = stream;
        })
        .catch(() => {
            alert("Camera access denied");
        });
}

function closeCameraModal() {
    document.getElementById("overlay").style.display = "none";
    document.getElementById("cameraModal").style.display = "none";

    if (stream) {
        stream.getTracks().forEach(track => track.stop());
    }
}


// capture photo    
const snapbtn = document.getElementById("snap");
const video = document.getElementById("video");
const canvas = document.getElementById("canvas");
const uploadBtn = document.getElementById("uploadBtn");
uploadBtn.style.display = "none"; // hide upload button initially



snapbtn.addEventListener("click", () => {
    const context = canvas.getContext("2d");

    video.style.display = "none"; // hide video after capture

    // set canvas size same as video
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    // draw current video frame onto canvas
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    // show canvas after capture
    canvas.style.display = "block";

    uploadBtn.style.display = "block"; // show upload button after capture

    uploadBtn.disabled = false;
});

let capturedImage = null;


uploadBtn.addEventListener("click", () => {

    // convert canvas image into base64 string
    capturedImage = canvas.toDataURL("image/png");



    canvas.style.display = "none"; // hide canvas after upload

    canvas.style.display = "block";

    console.log("IMAGE STORED:", capturedImage);

    alert("📸 Image uploaded successfully.")
    // optional next step navigation
    // window.location.href = "result.html";

});


