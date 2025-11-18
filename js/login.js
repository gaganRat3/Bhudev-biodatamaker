// Login Page JavaScript

let isLogin = true;

// Check if already logged in
window.addEventListener("DOMContentLoaded", () => {
  if (isAuthenticated()) {
    document.getElementById("auth-form-container").classList.add("hidden");
    document.getElementById("logged-in-message").classList.remove("hidden");

    // Redirect after 2 seconds
    setTimeout(() => {
      window.location.href = "index.html";
    }, 2000);
  }
});

// Toggle between login and register
document.getElementById("toggle-btn").addEventListener("click", () => {
  isLogin = !isLogin;

  const formTitle = document.getElementById("form-title");
  const emailGroup = document.getElementById("email-group");
  const submitBtn = document.getElementById("submit-btn");
  const toggleBtn = document.getElementById("toggle-btn");

  if (isLogin) {
    formTitle.textContent = "Login";
    emailGroup.classList.add("hidden");
    submitBtn.textContent = "Login";
    toggleBtn.textContent = "Don't have an account? Register";
  } else {
    formTitle.textContent = "Register";
    emailGroup.classList.remove("hidden");
    submitBtn.textContent = "Register";
    toggleBtn.textContent = "Already have an account? Login";
  }
});

// Handle form submission
document.getElementById("auth-form").addEventListener("submit", async (e) => {
  e.preventDefault();

  const submitBtn = document.getElementById("submit-btn");
  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;
  const email = document.getElementById("email").value;

  // Disable button and show loading
  submitBtn.disabled = true;
  submitBtn.textContent = "Please wait...";

  try {
    let response;

    if (isLogin) {
      response = await api.login(username, password);
    } else {
      response = await api.register(username, password, email);
    }

    // Store token and username
    localStorage.setItem("token", response.token);
    localStorage.setItem("username", response.username);

    // Show success message
    showAlert(
      isLogin ? "Login successful!" : "Registration successful!",
      "success"
    );

    // Redirect to home page
    setTimeout(() => {
      window.location.href = "index.html";
    }, 1000);
  } catch (error) {
    showAlert(error.message || "Something went wrong", "error");
    submitBtn.disabled = false;
    submitBtn.textContent = isLogin ? "Login" : "Register";
  }
});
