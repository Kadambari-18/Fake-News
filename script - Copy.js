// =============================
// 🎤 VOICE INPUT FUNCTION
// =============================
function startVoice() {
    try {
        const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();

        const langSelect = document.getElementById("langSelect");
        recognition.lang = langSelect ? langSelect.value : "en-US";

        recognition.onresult = function(event) {
            document.getElementById("newsBox").value =
                event.results[0][0].transcript;
        };

        recognition.onerror = function(event) {
            alert("Voice recognition error: " + event.error);
        };

        recognition.start();
    } catch (err) {
        alert("Voice feature not supported in your browser");
    }
}


// =============================
// 📧 CONTACT FORM + VALIDATION
// =============================
document.addEventListener("DOMContentLoaded", function () {

    const form = document.getElementById("contactForm");

    if (form) {
        form.addEventListener("submit", function (e) {
            e.preventDefault();

            let name = form.name.value.trim();
            let email = form.email.value.trim();
            let message = form.message.value.trim();

            // ---------------- VALIDATION ----------------
            if (name.length < 3) {
                showPopup("❌ Name must be at least 3 characters", "error");
                return;
            }

            if (!validateEmail(email)) {
                showPopup("❌ Enter a valid email address", "error");
                return;
            }

            if (message.length < 10) {
                showPopup("❌ Message must be at least 10 characters", "error");
                return;
            }

            // ---------------- SEND DATA ----------------
            let formData = new FormData(form);

            fetch("/submit_contact", {
                method: "POST",
                body: formData
            })
            .then(res => res.text())
            .then(data => {
                if (data === "success") {
                    showPopup("✅ Message sent successfully!", "success");
                    form.reset();
                } else {
                    showPopup("❌ Failed to send message", "error");
                }
            })
            .catch(() => {
                showPopup("❌ Server error. Try again later.", "error");
            });
        });
    }
});


// =============================
// 📩 EMAIL VALIDATION FUNCTION
// =============================
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}


// =============================
// 🎉 POPUP FUNCTION
// =============================
function showPopup(message, type) {

    let popup = document.getElementById("popup");

    // Create popup if not exists
    if (!popup) {
        popup = document.createElement("div");
        popup.id = "popup";
        document.body.appendChild(popup);
    }

    popup.innerText = message;

    popup.style.position = "fixed";
    popup.style.bottom = "20px";
    popup.style.right = "20px";
    popup.style.padding = "15px 25px";
    popup.style.borderRadius = "10px";
    popup.style.fontWeight = "bold";
    popup.style.zIndex = "9999";
    popup.style.transition = "0.3s";

    if (type === "success") {
        popup.style.background = "#00ff99";
        popup.style.color = "black";
    } else {
        popup.style.background = "#ff4d4d";
        popup.style.color = "white";
    }

    popup.style.display = "block";

    setTimeout(() => {
        popup.style.display = "none";
    }, 3000);
}