// Upgrade Page JavaScript

let paymentStatus = null;
let isSubmitted = false;

// Check payment status on load
async function checkPaymentStatus() {
  try {
    paymentStatus = await api.getPaymentStatus();

    if (paymentStatus.payment_status === "PREMIUM") {
      showPremiumStatus();
    } else if (paymentStatus.payment_status === "PENDING") {
      showPendingStatus();
    } else {
      showPaymentForm();
    }
  } catch (error) {
    console.error("Error fetching payment status:", error);
    showPaymentForm();
  }
}

function showPremiumStatus() {
  document.getElementById("premium-status").classList.remove("hidden");
  document.getElementById("pending-status").classList.add("hidden");
  document.getElementById("payment-form-container").classList.add("hidden");
  document.getElementById("success-message").classList.add("hidden");
}

function showPendingStatus() {
  document.getElementById("premium-status").classList.add("hidden");
  document.getElementById("pending-status").classList.remove("hidden");
  document.getElementById("payment-form-container").classList.add("hidden");
  document.getElementById("success-message").classList.add("hidden");
}

function showPaymentForm() {
  document.getElementById("premium-status").classList.add("hidden");
  document.getElementById("pending-status").classList.add("hidden");
  document.getElementById("payment-form-container").classList.remove("hidden");
  document.getElementById("success-message").classList.add("hidden");
}

function showSuccessMessage() {
  document.getElementById("premium-status").classList.add("hidden");
  document.getElementById("pending-status").classList.add("hidden");
  document.getElementById("payment-form-container").classList.add("hidden");
  document.getElementById("success-message").classList.remove("hidden");
}

// Handle form submission
document
  .getElementById("upgrade-form")
  .addEventListener("submit", async (e) => {
    e.preventDefault();

    const submitBtn = document.getElementById("submit-btn");
    const transactionId = document.getElementById("transaction-id").value;
    const screenshotInput = document.getElementById("screenshot");
    const screenshot = screenshotInput.files[0];

    if (!transactionId.trim()) {
      showAlert("Please enter transaction ID", "error");
      return;
    }

    submitBtn.disabled = true;
    submitBtn.textContent = "Submitting...";

    try {
      await api.submitPaymentVerification(transactionId, screenshot);

      showSuccessMessage();

      // Refresh payment status
      setTimeout(() => {
        checkPaymentStatus();
      }, 2000);
    } catch (error) {
      showAlert(
        error.message || "Failed to submit payment verification",
        "error"
      );
      submitBtn.disabled = false;
      submitBtn.textContent = "Submit for Verification";
    }
  });

// Initialize
window.addEventListener("DOMContentLoaded", checkPaymentStatus);
