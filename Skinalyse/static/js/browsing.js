const img = document.getElementById("img");
const preview = document.getElementById("preview");
const uploadBtn = document.getElementById("uploadBtn");
uploadBtn.style.display = "none"; // hide upload button initially



alert("choose the image from the device")


img.onchange = () => {
    const file = img.files[0];
    if (file) {

        console.log("FILE OBJECT:", file);   // 👈 shows file info
        console.log("FILE NAME:", file.name);
        console.log("FILE SIZE:", file.size);


        preview.src = URL.createObjectURL(file);
        uploadBtn.style.display = "block";
        uploadBtn.disabled = false;
    }

};

uploadBtn.onclick = () => {

    const file = img.files[0];

    if(!file){
        alert("please select image first");
        return;
    }

    // console.log("IMAGE READY FOR ANALYSIS:", file);


    alert("image uploaded successfully ✔");

};



