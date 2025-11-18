// Utility Functions

// Convert snake_case or camelCase to Title Case
function toTitleCase(str) {
  return str
    .replace(/_/g, " ")
    .replace(/([a-z])([A-Z])/g, "$1 $2")
    .replace(/\s+/g, " ")
    .trim()
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

// Check if user is authenticated
function isAuthenticated() {
  return !!localStorage.getItem("token");
}

// Redirect to login if not authenticated
function requireAuth() {
  if (!isAuthenticated()) {
    window.location.href = "login.html";
    return false;
  }
  return true;
}

// Get username from localStorage
function getUsername() {
  return localStorage.getItem("username") || "User";
}

// Logout user
function logout() {
  localStorage.removeItem("token");
  localStorage.removeItem("username");
  window.location.href = "login.html";
}

// Show loading spinner
function showLoading(elementId) {
  const element = document.getElementById(elementId);
  if (element) {
    element.innerHTML = '<div class="spinner"></div>';
  }
}

// Hide loading spinner
function hideLoading(elementId) {
  const element = document.getElementById(elementId);
  if (element) {
    element.innerHTML = "";
  }
}

// Show alert message
function showAlert(message, type = "info", containerId = "alert-container") {
  const container = document.getElementById(containerId);
  if (!container) return;

  const alert = document.createElement("div");
  alert.className = `alert alert-${type} fade-in`;
  alert.textContent = message;

  container.appendChild(alert);

  // Auto-remove after 5 seconds
  setTimeout(() => {
    alert.remove();
  }, 5000);
}

// Debounce function
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

// File to Base64
function fileToBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => resolve(reader.result);
    reader.onerror = (error) => reject(error);
  });
}

// Format date
function formatDate(dateString) {
  if (!dateString) return "N/A";
  const date = new Date(dateString);
  return date.toLocaleDateString();
}

// Generate height options
function generateHeightOptions() {
  const options = [];
  for (let ft = 3; ft <= 8; ft++) {
    for (let inch = 0; inch <= 11; inch++) {
      options.push(`${ft}' ${inch}"`);
      if (ft === 8 && inch === 0) break;
    }
  }
  return options;
}

// Create element with classes
function createElement(tag, classes = [], attributes = {}) {
  const element = document.createElement(tag);
  if (classes.length) {
    element.className = classes.join(" ");
  }
  Object.entries(attributes).forEach(([key, value]) => {
    element.setAttribute(key, value);
  });
  return element;
}

// Simple animation on scroll
function animateOnScroll() {
  const elements = document.querySelectorAll(".animate-on-scroll");
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("fade-in");
        observer.unobserve(entry.target);
      }
    });
  });

  elements.forEach((el) => observer.observe(el));
}

// Initialize on page load
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", animateOnScroll);
} else {
  animateOnScroll();
}
