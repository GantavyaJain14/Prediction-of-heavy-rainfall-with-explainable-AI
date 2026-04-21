// ==========================================
// Auth Helper Functions – shared across pages
// ==========================================

/**
 * Get the stored users object from localStorage.
 * Format: { "email@example.com": { name, email, password (base64) } }
 */
function getUsers() {
    try {
        return JSON.parse(localStorage.getItem('xai_users') || '{}');
    } catch {
        return {};
    }
}

/**
 * Persist the users object to localStorage.
 */
function saveUsers(users) {
    localStorage.setItem('xai_users', JSON.stringify(users));
}

/**
 * Display an error message in the given element.
 */
function showError(el, msg) {
    el.textContent = '⚠️ ' + msg;
    el.style.display = 'block';
}

/**
 * Toggle password field visibility.
 */
function togglePw(inputId, btn) {
    const input = document.getElementById(inputId);
    if (input.type === 'password') {
        input.type = 'text';
        btn.textContent = '🙈';
    } else {
        input.type = 'password';
        btn.textContent = '👁';
    }
}
