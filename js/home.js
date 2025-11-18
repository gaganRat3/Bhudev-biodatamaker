// Home Page JavaScript

// Set current year in footer
document.getElementById("currentYear").textContent = new Date().getFullYear();

// Navigation functions
function navigateToBiodata() {
  window.location.href = "biodata-form.html";
}

function navigateToLogin() {
  window.location.href = "login.html";
}

function navigateToUpgrade() {
  window.location.href = "upgrade.html";
}

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
  anchor.addEventListener("click", function (e) {
    e.preventDefault();
    const target = document.querySelector(this.getAttribute("href"));
    if (target) {
      target.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    }
  });
});

// Add scroll animation trigger (parallax only on background, not entire hero)
window.addEventListener("scroll", () => {
  const scrolled = window.pageYOffset;
  const bg = document.querySelector(".hero-background");
  if (bg) {
    bg.style.transform = `translateY(${scrolled * 0.3}px)`; // subtle parallax
  }
});

// Initialize animations
document.addEventListener("DOMContentLoaded", () => {
  // Add fade-in animation to elements
  const observerOptions = {
    threshold: 0.1,
    rootMargin: "0px 0px -100px 0px",
  };

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.style.opacity = "1";
        entry.target.style.transform = "translateY(0)";
      }
    });
  }, observerOptions);

  // Observe all animated elements
  document.querySelectorAll(".animate-on-scroll").forEach((el) => {
    el.style.opacity = "0";
    el.style.transform = "translateY(20px)";
    el.style.transition = "opacity 0.6s ease, transform 0.6s ease";
    observer.observe(el);
  });
});
