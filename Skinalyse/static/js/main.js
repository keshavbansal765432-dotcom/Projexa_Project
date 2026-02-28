document.addEventListener("DOMContentLoaded", () => {

    // CTA BUTTON POPUP 
    const startBtn = document.getElementById("startBtn");

    if (startBtn) {
        startBtn.addEventListener("click", () => {

            alert("📸 Opening camera for instant skin analysis...");

            // navigate after popup
            window.location.href = "camera.html";
        });
    }


    //CONTACT FORM POPUP 
    const contactForm = document.querySelector(".contact-form");

    if (contactForm) {
        contactForm.addEventListener("submit", (e) => {
            e.preventDefault();

            alert("✅ Thank you! Your message has been sent.");

            contactForm.reset();
        });
    }


    //NAVBAR CLICK POPUP
    const navLinks = document.querySelectorAll(".nav-links a");

    navLinks.forEach(link => {
        link.addEventListener("click", () => {
            console.log("Navigating section...");
        });
    });

});
