// Toggle dark mode and store preference in localStorage
function toggleDarkMode() {
    document.body.classList.toggle('dark');
    if (document.body.classList.contains('dark')) {
        localStorage.setItem('darkMode', 'enabled');
    } else {
        localStorage.removeItem('darkMode');
    }
}

// Load preference on page load
window.onload = function () {
    if (localStorage.getItem('darkMode') === 'enabled') {
        document.body.classList.add('dark');
    }
};

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
