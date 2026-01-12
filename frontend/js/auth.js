// auth.js

// Get token from localStorage
function getToken() {
    return localStorage.getItem("access_token");
}

// Decode JWT payload
function parseJwt(token) {
    try {
        return JSON.parse(atob(token.split('.')[1]));
    } catch {
        return null;
    }
}

// Get current logged-in user info
function getCurrentUser() {
    const token = getToken();
    if (!token) return null;
    return parseJwt(token);
}

// Logout
function logout() {
    localStorage.removeItem("access_token");
    window.location.href = "login.html";
}
