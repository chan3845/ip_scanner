// Toggle dark mode and store preference in localStorage
function toggleDarkMode() {
    const body = document.body;
    body.classList.toggle("dark");

    // Get the dark mode toggle button
    const toggleButton = document.querySelector(".dark-mode-toggle");
    
    // Check if the body has the 'dark' class and update the button accordingly
    const isDarkMode = body.classList.contains("dark");
    if (isDarkMode) {
        toggleButton.innerHTML = "☀️ Light Mode";
    } else {
        toggleButton.innerHTML = "🌙 Dark Mode";
    }

    // Save the user's preference in localStorage for persistence
    localStorage.setItem("darkMode", isDarkMode);
}


// Load preference on page load
window.addEventListener('load', () => {
    const savedMode = localStorage.getItem('darkMode');
    const toggleButton = document.querySelector(".dark-mode-toggle");
    
    if (savedMode === "true") {
        document.body.classList.add("dark");
        if (toggleButton) {
            toggleButton.innerHTML = "☀️ Light Mode";
        }
    } else {
        document.body.classList.remove("dark");
        if (toggleButton) {
            toggleButton.innerHTML = "🌙 Dark Mode";
        }
    }
});


function toggleEmailPopup() {
    const popup = document.getElementById('emailPopup');
    if (popup.style.display === 'block') {
        popup.style.display = 'none';
    } else {
        popup.style.display = 'block';
    }
}

// Copy email text to clipboard
function copyEmail() {
    const emailText = document.getElementById('emailAddress').textContent;
    navigator.clipboard.writeText(emailText).then(() => {
        alert('Email copied to clipboard!');
    });
}

