import { auth } from "./firebase-config.js";
import {
    GoogleAuthProvider,
    signInWithPopup,
    signOut,
    onAuthStateChanged,
    createUserWithEmailAndPassword,
    signInWithEmailAndPassword,
    sendPasswordResetEmail
} from "https://www.gstatic.com/firebasejs/10.8.0/firebase-auth.js";

const provider = new GoogleAuthProvider();

const loginBtn = document.getElementById('login-btn');
const logoutBtn = document.getElementById('logout-btn');
const loginOverlay = document.getElementById('login-overlay');
const appContent = document.getElementById('app-content');
const userNameDisplay = document.getElementById('user-name');
const userAvatar = document.getElementById('user-avatar');

// Toggle State
let isLoginMode = true;

window.toggleAuthMode = () => {
    isLoginMode = !isLoginMode;
    const title = document.getElementById('auth-title');
    const actionBtn = document.getElementById('auth-action-btn');
    const toggleText = document.getElementById('auth-toggle-text');
    const toggleLink = document.getElementById('auth-toggle-link');
    const errorMsg = document.getElementById('auth-error-msg');

    errorMsg.textContent = ""; // Clear errors

    if (isLoginMode) {
        title.textContent = "Welcome Back";
        actionBtn.textContent = "Login";
        actionBtn.onclick = window.loginWithEmail;
        toggleText.textContent = "Don't have an account?";
        toggleLink.textContent = "Create one";
    } else {
        title.textContent = "Create Account";
        actionBtn.textContent = "Sign Up";
        actionBtn.onclick = window.signupWithEmail;
        toggleText.textContent = "Already have an account?";
        toggleLink.textContent = "Login";
    }
};

// Email/Password Login
window.loginWithEmail = async () => {
    const email = document.getElementById('email-input').value;
    const password = document.getElementById('password-input').value;
    const errorMsg = document.getElementById('auth-error-msg');

    try {
        await signInWithEmailAndPassword(auth, email, password);
        errorMsg.textContent = "";
    } catch (error) {
        console.error("Login Failed:", error);
        errorMsg.textContent = `Error (${error.code}): ${error.message}`;
    }
};

// Email/Password Signup
window.signupWithEmail = async () => {
    const email = document.getElementById('email-input').value;
    const password = document.getElementById('password-input').value;
    const errorMsg = document.getElementById('auth-error-msg');

    try {
        await createUserWithEmailAndPassword(auth, email, password);
        errorMsg.textContent = "";
    } catch (error) {
        console.error("Signup Failed:", error);
        errorMsg.textContent = `Error (${error.code}): ${error.message}`;
    }
};

// Password Reset
window.resetPassword = async () => {
    const email = document.getElementById('email-input').value;
    const errorMsg = document.getElementById('auth-error-msg');

    if (!email) {
        errorMsg.textContent = "Please enter your email to reset password.";
        return;
    }

    try {
        await sendPasswordResetEmail(auth, email);
        alert("Password reset email sent!");
        errorMsg.textContent = "";
    } catch (error) {
        console.error("Reset Failed:", error);
        errorMsg.textContent = error.message;
    }
};

// Google Login
window.loginWithGoogle = async () => {
    try {
        await signInWithPopup(auth, provider);
    } catch (error) {
        console.error("Login Failed:", error);
    }
};

// Logout Function
window.logout = async () => {
    try {
        await signOut(auth);
    } catch (error) {
        console.error("Logout Failed:", error);
    }
};

// Auth State Monitor
// Auth State Monitor
onAuthStateChanged(auth, (user) => {
    const landingView = document.getElementById('landing-view');
    const contactView = document.getElementById('contact-view');
    const dashboardView = document.getElementById('dashboard-view');
    const loginOverlay = document.getElementById('login-overlay');
    const userNameDisplay = document.getElementById('user-name');
    const userAvatar = document.getElementById('user-avatar');

    if (user) {
        // User is signed in
        console.log("User Logged In:", user.email);

        // Show Dashboard, Hide others
        const mainNav = document.getElementById('main-nav');

        // Show Dashboard, Hide others
        if (landingView) landingView.style.display = 'none';
        if (contactView) contactView.style.display = 'none';
        if (mainNav) mainNav.style.display = 'none'; // Hide Landing Nav
        if (dashboardView) {
            dashboardView.style.display = 'grid';
            dashboardView.style.zIndex = '1'; // Reset z-index
            dashboardView.classList.remove('blur-sm'); // REMOVE BLUR
        }
        if (loginOverlay) loginOverlay.style.display = 'none';

        if (userNameDisplay) userNameDisplay.textContent = user.displayName || user.email;
        if (user.photoURL && userAvatar) {
            userAvatar.src = user.photoURL;
        }
    } else {
        // User is signed out
        console.log("User Signed Out");

        // Show Landing, Hide Dashboard
        const mainNav = document.getElementById('main-nav');

        // Show Landing, Hide Dashboard
        if (dashboardView) dashboardView.style.display = 'none';
        if (landingView) landingView.style.display = 'block';
        if (mainNav) mainNav.style.display = 'flex'; // Restore Landing Nav
        // We don't auto-show login overlay anymore, user must click 'Login'
    }
});
