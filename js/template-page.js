// Send free template to email
async function sendFreeTemplateToEmail() {
  const emailInput = document.getElementById("free-email-input");
  const email = emailInput ? emailInput.value.trim() : "";
  if (!email) {
    alert("Please enter a valid email address.");
    return;
  }
  // Get biodata id
  let biodataId = localStorage.getItem("biodata_id");
  if (!biodataId && formData && formData.id) {
    biodataId = formData.id;
  }
  if (!biodataId) {
    alert("Biodata ID not found. Please save your biodata first.");
    return;
  }
  // Call backend endpoint to send email
  try {
    const resp = await fetch(`/api/biodata/${biodataId}/send_free_email/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email }),
    });
    const data = await resp.json();
    if (resp.ok && data.success) {
      alert("The free template PDF has been sent to your email!");
    } else {
      alert("Failed to send email: " + (data.error || resp.statusText));
    }
  } catch (err) {
    alert("Error sending email: " + err.message);
  }
}

// Helper: Generate direct PDF download link for a given biodata ID
function getDirectPDFDownloadLink(biodataId) {
  if (!biodataId) return "#";
  return `${window.location.origin}/api/biodata/${biodataId}/download/`;
}
// Template Page JavaScript
// Responsibilities:
// 1. Load previously prepared biodata (from localStorage 'formDataForTemplate').
// 2. Allow user to preview 5 different templates (ID 1 = free, 2-5 = premium, with 5 having a special layout).
// 3. Free template -> immediate print style download; Premium templates -> registration modal & backend persistence.
// 4. Provide print-friendly PDF generation (window.print) with proper border image mapping.

let formData = null;
let selectedTemplate = null;

// Border mapping aligned with backend template_choice definitions used in admin action.
// Note: Template 1 (free) uses the White.png minimalist frame.
const TEMPLATE_BORDER_IMAGES = {
  1: "assets/border/White.png",
  2: "assets/border/bg0.png",
  3: "assets/border/bg3.jpg", // matches CSS border-style-3 requirement
  4: "assets/border/bg8.jpg",
  5: "assets/border/bg9.jpg", // red frame style for premium template 5 (special layout)
  // If backend adds choice 6 later, it would be bg10.jpg (not currently selectable here)
};

// Load form data from localStorage
function loadFormData() {
  const saved = localStorage.getItem("formDataForTemplate");
  if (!saved) {
    alert("No biodata data found. Please create a biodata first.");
    window.location.href = "biodata-form.html";
    return;
  }
  try {
    formData = JSON.parse(saved) || {};
  } catch (e) {
    console.error("Error loading form data:", e);
    alert("Error loading biodata data. Please create a new biodata.");
    window.location.href = "biodata-form.html";
  }
}

// Select template
function selectTemplate(templateId) {
  if (!formData) {
    alert("Biodata not loaded yet. Please return and regenerate.");
    return;
  }
  selectedTemplate = templateId;
  document.getElementById("template-gallery").classList.add("hidden");
  document.getElementById("template-view").classList.remove("hidden");
  renderTemplate(templateId);
  updateDownloadButton(templateId);
}

// Update download button for premium templates
function updateDownloadButton(templateId) {
  const downloadBtn = document.getElementById("download-btn");

  const exportBtn = document.getElementById("export-pdf-btn");
  if (templateId === 1) {
    // Free template: show export button and set up both buttons
    downloadBtn.className = "btn btn-primary";
    downloadBtn.disabled = false;
    downloadBtn.style.display = "";
    downloadBtn.innerHTML = `<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\" width=\"20\" height=\"20\"><path d=\"M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4\" /><polyline points=\"7 10 12 15 17 10\" /><line x1=\"12\" y1=\"15\" x2=\"12\" y2=\"3\" /></svg>Download PDF`;
    downloadBtn.onclick = function () {
      const element = document.getElementById("template-content");
      if (!element) {
        alert("Preview not found.");
        return;
      }
      const opt = {
        margin: 0,
        filename: "biodata.pdf",
        image: { type: "jpeg", quality: 0.98 },
        html2canvas: { scale: 2, useCORS: true },
        jsPDF: { unit: "pt", format: "a4", orientation: "portrait" },
      };
      html2pdf().set(opt).from(element).save();
    };
    if (exportBtn) {
      exportBtn.style.display = "";
      exportBtn.onclick = function () {
        const element = document.getElementById("template-content");
        if (!element) {
          alert("Preview not found.");
          return;
        }
        // Mobile detection
        const isMobile =
          /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(
            navigator.userAgent
          );
        const opt = {
          margin: 0,
          filename: "biodata_export.pdf",
          image: { type: "jpeg", quality: 0.98 },
          html2canvas: { scale: 2, useCORS: true },
          jsPDF: { unit: "pt", format: "a4", orientation: "portrait" },
        };
        if (isMobile) {
          // Always force download on mobile
          html2pdf().set(opt).from(element).save();
        } else {
          // On desktop, default to download as well (can be customized if needed)
          html2pdf().set(opt).from(element).save();
        }
      };
    }
  } else {
    // Premium template: hide export button
    if (exportBtn) exportBtn.style.display = "none";
    downloadBtn.className = "btn download-premium";
    downloadBtn.innerHTML =
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg>Register to Download';
    downloadBtn.removeAttribute("href");
    downloadBtn.onclick = handleDownload;
  }
}

// Handle download based on template type
async function handleDownload() {
  if (selectedTemplate === 1) {
    // Free template - download PDF from backend endpoint
    // Try to get biodata id from localStorage (if available)
    const saved = localStorage.getItem("biodata_id");
    let biodataId = null;
    if (saved) {
      biodataId = saved;
    } else if (formData && formData.id) {
      biodataId = formData.id;
    }
    if (!biodataId) {
      alert("Biodata ID not found. Please save your biodata first.");
      return;
    }
    // Compose backend endpoint URL
    const url = `${window.location.origin}/api/biodata/${biodataId}/download/`;
    // Try fetching PDF (backend may return 501 if server cannot generate PDF)
    try {
      const resp = await fetch(url);
      if (!resp.ok) {
        // If server returned 501 or other error, fall back to opening HTML view
        window.open(
          `${window.location.origin}/api/download/${biodataId}/`,
          "_blank"
        );
        return;
      }
      const blob = await resp.blob();
      const contentType = resp.headers.get("Content-Type") || "";
      if (contentType.indexOf("application/pdf") === -1) {
        // Not a PDF — open HTML fallback
        window.open(
          `${window.location.origin}/api/download/${biodataId}/`,
          "_blank"
        );
        return;
      }
      const link = document.createElement("a");
      link.href = window.URL.createObjectURL(blob);
      link.download = `biodata_${biodataId}.pdf`;
      document.body.appendChild(link);
      link.click();
      setTimeout(() => {
        window.URL.revokeObjectURL(link.href);
        document.body.removeChild(link);
      }, 100);
    } catch (err) {
      // Network/fetch error - open HTML fallback so user can still save via print
      window.open(
        `${window.location.origin}/api/download/${biodataId}/`,
        "_blank"
      );
    }
  } else {
    // Premium template - require registration
    showRegistrationModal();
  }
}

// Show registration modal for premium downloads
function showRegistrationModal() {
  // Populate modal fields (if any saved) and show modal
  const saved = localStorage.getItem("templateRegistration");
  if (saved) {
    try {
      const parsed = JSON.parse(saved);
      document.getElementById("reg-name").value = parsed.name || "";
      document.getElementById("reg-email").value = parsed.email || "";
      document.getElementById("reg-phone").value = parsed.phone || "";
    } catch (e) {
      console.warn("Could not parse saved registration:", e);
    }
  }

  // Show modal
  document.getElementById("reg-modal").classList.remove("hidden");
  document.getElementById("reg-modal").focus();
}

// Hide registration modal
function hideRegistrationModal() {
  document.getElementById("reg-modal").classList.add("hidden");
}

// Submit registration and create pending biodata record
async function submitRegistration(event) {
  event.preventDefault();

  const name = document.getElementById("reg-name").value.trim();
  const email = document.getElementById("reg-email").value.trim();
  const phone = document.getElementById("reg-phone").value.trim();

  if (!name || !email) {
    alert("Please enter your name and email.");
    return;
  }

  // Save quick copy locally
  localStorage.setItem(
    "templateRegistration",
    JSON.stringify({ name, email, phone })
  );

  // Build payload from existing local formDataForTemplate
  const saved = localStorage.getItem("formDataForTemplate");
  if (!saved) {
    alert("No biodata found in your browser. Please create biodata first.");
    hideRegistrationModal();
    window.location.href = "biodata-form.html";
    return;
  }

  let parsed = {};
  try {
    parsed = JSON.parse(saved);
  } catch (e) {
    alert("Error reading biodata data. Please recreate your biodata.");
    hideRegistrationModal();
    return;
  }

  // Prepare FormData for API (serializer expects 'data' JSON string)
  const fd = new FormData();
  const payloadData = {
    PersonalDetails: parsed.PersonalDetails || {},
    FamilyDetails: parsed.FamilyDetails || {},
    HabitsDeclaration: parsed.HabitsDeclaration || {},
  };

  const title = payloadData.PersonalDetails.name || "";
  if (title) fd.append("title", title);

  fd.append("data", JSON.stringify(payloadData));
  fd.append("template_choice", String(selectedTemplate));
  fd.append("user_name", name);
  fd.append("user_email", email);
  fd.append("user_phone", phone);

  // If imagePreview exists, try to convert base64 to blob and append as profile_image
  if (parsed.imagePreview && parsed.imagePreview.startsWith("data:")) {
    try {
      const res = await fetch(parsed.imagePreview);
      const blob = await res.blob();
      fd.append("profile_image", blob, "profile.png");
    } catch (e) {
      console.warn("Could not attach image preview:", e);
    }
  }

  // Attach payment screenshot if provided
  const paymentScreenshotInput = document.getElementById(
    "reg-payment-screenshot"
  );
  if (
    paymentScreenshotInput &&
    paymentScreenshotInput.files &&
    paymentScreenshotInput.files[0]
  ) {
    fd.append("payment_screenshot", paymentScreenshotInput.files[0]);
  }

  // Disable UI while submitting
  const submitBtn = document.getElementById("reg-submit");
  submitBtn.disabled = true;
  submitBtn.textContent = "Submitting...";

  try {
    // Create biodata record (will be is_approved=false by default)
    const resp = await api.createBiodata(fd);

    // Hide registration modal and show confirmation container
    hideRegistrationModal();
    document.getElementById("template-gallery").classList.add("hidden");
    document.getElementById("template-view").classList.add("hidden");
    const confirmation = document.getElementById("confirmation-container");
    if (confirmation) confirmation.classList.remove("hidden");

    // Optionally update UI: mark download as pending
    const downloadBtn = document.getElementById("download-btn");
    if (downloadBtn) {
      downloadBtn.disabled = true;
      downloadBtn.textContent = "Awaiting Approval";
    }
  } catch (err) {
    console.error(err);
    alert("Error saving registration: " + (err.message || err));
  } finally {
    submitBtn.disabled = false;
    submitBtn.textContent = "Submit & Request Download";
  }
}

// Back to gallery
function backToGallery() {
  document.getElementById("template-gallery").classList.remove("hidden");
  document.getElementById("template-view").classList.add("hidden");
}

// Render template
function renderTemplate(templateId) {
  const container = document.getElementById("template-content");
  if (!container) return;

  // Template 5 has a bespoke right-side layout.
  if (templateId === 5) {
    renderTemplate5(container);
    return;
  }

  // Assign CSS class so existing stylesheet sets background image.
  let borderClass = "border-style-" + (templateId === 1 ? "1" : templateId);
  if (templateId === 1) borderClass = "free-border"; // override for free
  container.className = borderClass;

  // Build main biodata content wrapper.
  const biodataContent = document.createElement("div");
  biodataContent.className = "biodata-template";

  // Profile Image.
  if (formData.imagePreview) {
    const img = document.createElement("img");
    img.src = formData.imagePreview;
    img.alt = "Profile";
    img.className = "biodata-profile-image";
    biodataContent.appendChild(img);
  }

  // Name.
  const name = formData?.PersonalDetails?.name || "";
  if (name) {
    const h2 = document.createElement("h2");
    h2.className = "biodata-name";
    h2.textContent = name;
    biodataContent.appendChild(h2);
  }

  // Helper: produce section element with two-column split.
  function buildSection(title, obj) {
    const entries = Object.entries(obj || {}).filter(
      ([, v]) => v && String(v).trim()
    );
    if (!entries.length) return null;
    const sectionEl = document.createElement("div");
    sectionEl.className = "biodata-section";

    const pill = document.createElement("div");
    pill.className = "section-pill";
    pill.textContent = title;
    sectionEl.appendChild(pill);

    const mid = Math.ceil(entries.length / 2);
    const leftEntries = entries.slice(0, mid);
    const rightEntries = entries.slice(mid);

    const columnsWrapper = document.createElement("div");
    columnsWrapper.className = "detail-columns"; // styled in template-page.html

    const leftCol = document.createElement("div");
    leftCol.style.display = "flex";
    leftCol.style.flexDirection = "column";
    const rightCol = document.createElement("div");
    rightCol.style.display = "flex";
    rightCol.style.flexDirection = "column";

    leftEntries.forEach(([k, v]) => {
      leftCol.appendChild(makeDetailItem(k, v));
    });
    rightEntries.forEach(([k, v]) => {
      rightCol.appendChild(makeDetailItem(k, v));
    });

    columnsWrapper.appendChild(leftCol);
    columnsWrapper.appendChild(rightCol);
    sectionEl.appendChild(columnsWrapper);
    return sectionEl;
  }

  function makeDetailItem(key, value) {
    const item = document.createElement("div");
    item.className = "detail-item";
    const label = document.createElement("div");
    label.className = "detail-label";
    label.textContent = toTitleCase(key) + ":";
    const val = document.createElement("div");
    val.className = "detail-value";
    val.textContent = value;
    item.appendChild(label);
    item.appendChild(val);
    return item;
  }

  const personal = buildSection("Personal Details", formData.PersonalDetails);
  if (personal) biodataContent.appendChild(personal);
  const family = buildSection("Family Details", formData.FamilyDetails);
  if (family) biodataContent.appendChild(family);
  const habits = buildSection(
    "Habits & Declaration",
    formData.HabitsDeclaration
  );
  if (habits) biodataContent.appendChild(habits);

  // Render.
  container.innerHTML = "";
  if (templateId !== 1 && templateId !== 5) {
    const watermark = document.createElement("div");
    watermark.className = "premium-watermark";
    watermark.textContent = "BhudevNetworkvivha";
    container.appendChild(watermark);
  }
  container.appendChild(biodataContent);
}

// Download PDF
function downloadPDF() {
  const element = document.getElementById("template-content");
  if (!element) {
    alert("No template to download. Please select a template first.");
    return;
  }

  if (!selectedTemplate) {
    alert("Template not selected.");
    return;
  }

  // Special case template 5
  if (selectedTemplate === 5) {
    downloadTemplate5PDF(element);
    return;
  }

  // Use mapping (fallback to element computed style if missing).
  const borderImagePath =
    TEMPLATE_BORDER_IMAGES[selectedTemplate] ||
    (() => {
      const bg = window.getComputedStyle(element).backgroundImage;
      const match = bg && bg.match(/url\(["']?([^"']+)["']?\)/);
      return match ? match[1] : TEMPLATE_BORDER_IMAGES[1];
    })();

  const pdfWindow = window.open("", "_blank");
  if (!pdfWindow) {
    alert("Popup blocked. Allow popups to download the PDF.");
    return;
  }

  pdfWindow.document.write(`
    <!DOCTYPE html>
    <html>
    <head>
      <title>Biodata Template - ${selectedTemplate}</title>
      <style>
        * {
          margin: 0;
          padding: 0;
          box-sizing: border-box;
        }
        
        body { 
          margin: 0; 
          padding: 0; 
          font-family: "Times New Roman", serif;
          background: white;
        }
        
        /* Force border image to display */
        #template-content {
          background-image: url("${borderImagePath}") !important;
          background-size: 100% 100% !important;
          background-position: center !important;
          background-repeat: no-repeat !important;
          padding: 50px 70px !important;
          min-height: auto !important;
          height: auto !important;
          width: 600px !important;
          max-width: 600px !important;
          margin: 0 auto !important;
          position: relative !important;
          -webkit-print-color-adjust: exact !important;
          color-adjust: exact !important;
          print-color-adjust: exact !important;
          page-break-inside: avoid !important;
        }
        
        /* Biodata content styling matching screenshot */
        .biodata-template {
          max-width: 100%;
          margin: 0;
          background: transparent;
          padding: 0;
          border: none;
          position: relative;
          z-index: 1;
          font-family: "Times New Roman", serif;
          color: #2c3e50;
          page-break-inside: avoid;
        }
        
        .biodata-name {
          text-align: center;
          font-size: 1.25rem;
          font-weight: bold;
          color: #2c3e50;
          margin: 0 0 18px 0;
          letter-spacing: 1px;
          font-family: "Times New Roman", serif;
        }
        
        .section-pill {
          background: linear-gradient(135deg, #e67e22, #d35400);
          color: white;
          padding: 7px 18px;
          border-radius: 20px;
          font-weight: 600;
          margin: 0 auto 14px;
          display: block;
          width: fit-content;
          font-size: 0.82rem;
          text-transform: uppercase;
          letter-spacing: 0.5px;
          box-shadow: 0 2px 6px rgba(230, 126, 34, 0.4);
          font-family: "Times New Roman", serif;
        }
        
        .biodata-section {
          margin-bottom: 18px;
          page-break-inside: avoid;
        }
        
        .detail-columns {
          display: grid;
          grid-template-columns: 1fr 1fr;
          column-gap: 22px;
          row-gap: 4px;
          margin-top: 8px;
          padding: 0;
          position: relative;
        }
        
        .detail-columns::before {
          content: '';
          position: absolute;
          left: 50%;
          top: 0;
          bottom: 0;
          width: 1px;
          background-color: #bdc3c7;
          transform: translateX(-50%);
        }
        
        .detail-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 2px 0;
          margin-bottom: 2px;
        }
        
        .detail-label {
          color: #2c3e50;
          font-weight: 600;
          font-size: 0.85rem;
          width: 48%;
          font-family: "Times New Roman", serif;
          line-height: 1.4;
        }
        
        .detail-value {
          color: #34495e;
          font-size: 0.85rem;
          width: 48%;
          text-align: right;
          font-weight: 500;
          font-family: "Times New Roman", serif;
          line-height: 1.4;
        }
        
        .biodata-profile-image {
          width: 110px;
          height: 110px;
          border-radius: 50%;
          object-fit: cover;
          margin: 0 auto 14px;
          display: block;
          border: 3px solid #8b4513;
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        }
        
        .premium-watermark {
          position: absolute;
          top: 50%;
          left: 50%;
          transform: translate(-50%, -50%) rotate(-45deg);
          font-size: 3rem;
          font-weight: bold;
          color: rgba(245, 158, 11, 0.3);
          pointer-events: none;
          z-index: 15;
          white-space: nowrap;
          text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
          letter-spacing: 3px;
          font-family: Arial, sans-serif;
        }
        
        @media print {
          * {
            -webkit-print-color-adjust: exact !important;
            color-adjust: exact !important;
            print-color-adjust: exact !important;
          }
          
          body { 
            margin: 0 !important; 
            padding: 0 !important; 
          }
          
          #template-content { 
            margin: 0 auto !important;
            padding: 50px 70px !important;
            page-break-inside: avoid !important;
            page-break-after: avoid !important;
            width: 600px !important;
            max-width: 600px !important;
            min-height: auto !important;
            height: auto !important;
            background-image: url("${borderImagePath}") !important;
            background-size: 100% 100% !important;
            background-position: center !important;
            background-repeat: no-repeat !important;
            -webkit-print-color-adjust: exact !important;
            color-adjust: exact !important;
            print-color-adjust: exact !important;
          }
          
          .biodata-section {
            page-break-inside: avoid !important;
          }
        }
        
        @page {
          size: A4 portrait;
          margin: 10mm;
        }
      </style>
    </head>
    <body>
      <div id="template-content">${element.innerHTML}</div>
      <script>
        window.onload = function() {
          setTimeout(function() {
            window.print();
            setTimeout(function(){ window.close(); }, 750);
          }, 300);
        };
      <\/script>
    </body>
    </html>
  `);
  pdfWindow.document.close();
}

// Helper: reset container to a clean base before building Template 5
function resetTemplateContainer(container) {
  container.innerHTML = "";
  container.className = "";
  container.style.cssText = "";
}

// Special rendering function for Template 5 (Right Side Image Layout)
function renderTemplate5(container) {
  resetTemplateContainer(container);
  container.style.cssText = `padding:0;width:700px;max-width:700px;background:#fff;border:8px solid #dc143c;box-sizing:border-box;margin:20px auto;min-height:800px;position:relative;`;

  const watermark = document.createElement("div");
  watermark.className = "premium-watermark";
  watermark.textContent = "BhudevNetworkvivha";
  container.appendChild(watermark);

  const header = document.createElement("div");
  header.style.cssText = `position:absolute;top:20px;left:50%;transform:translateX(-50%);text-align:center;z-index:10;`;
  header.innerHTML = `<div style="font-size:24px;color:#dc143c;margin-bottom:5px;font-weight:bold">🕉</div><div style="font-size:18px;color:#dc143c;font-weight:bold;letter-spacing:1px;">BIO DATA</div>`;

  const inner = document.createElement("div");
  inner.style.cssText = `position:relative;z-index:1;background:#fff;width:100%;min-height:800px;display:flex;box-sizing:border-box;padding:80px 20px 30px 20px;`;
  const left = document.createElement("div");
  left.style.cssText = `flex:1;padding:0 10px;`;
  const right = document.createElement("div");
  right.style.cssText = `width:200px;display:flex;flex-direction:column;align-items:center;`;

  if (formData?.imagePreview) {
    const img = document.createElement("img");
    img.src = formData.imagePreview;
    img.alt = "Profile";
    img.style.cssText = `width:150px;height:180px;object-fit:cover;border:2px solid #000;margin-bottom:20px;`;
    right.appendChild(img);
  } else {
    const ph = document.createElement("div");
    ph.style.cssText = `width:150px;height:180px;background:#f0f0f0;border:2px solid #000;display:flex;align-items:center;justify-content:center;color:#666;font-size:12px;text-align:center;margin-bottom:20px;`;
    ph.innerHTML = "Profile<br>Photo";
    right.appendChild(ph);
  }

  function section5(titleText, obj) {
    const entries = Object.entries(obj || {}).filter(
      ([, v]) => v && String(v).trim()
    );
    if (!entries.length) return;
    const title = document.createElement("div");
    title.textContent = titleText.toUpperCase();
    title.style.cssText = `background:#4169e1;color:#fff;padding:8px 15px;font-weight:bold;font-size:14px;margin:20px 0 10px;width:fit-content;`;
    left.appendChild(title);
    const grid = document.createElement("div");
    grid.style.cssText = `display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-bottom:15px;`;
    const c1 = document.createElement("div");
    const c2 = document.createElement("div");
    entries.forEach(([k, v], i) => {
      const item = document.createElement("div");
      item.style.cssText = `margin-bottom:8px;font-size:12px;line-height:1.4;`;
      const lab = document.createElement("div");
      lab.textContent = toTitleCase(k);
      lab.style.cssText = `color:#4169e1;margin-bottom:2px;`;
      const val = document.createElement("div");
      val.textContent = v;
      val.style.cssText = `color:#000;`;
      item.appendChild(lab);
      item.appendChild(val);
      (i % 2 === 0 ? c1 : c2).appendChild(item);
    });
    grid.appendChild(c1);
    grid.appendChild(c2);
    left.appendChild(grid);
  }

  section5("Personal Details", formData?.PersonalDetails);
  section5("Family Details", formData?.FamilyDetails);
  // Removed non-existent ContactDetails section to prevent empty header.
  section5("Habits & Declaration", formData?.HabitsDeclaration);

  inner.appendChild(left);
  inner.appendChild(right);

  const footer = document.createElement("div");
  footer.style.cssText = `position:absolute;bottom:15px;left:50%;transform:translateX(-50%);text-align:center;font-size:10px;color:#666;width:90%;border-top:1px dashed #ccc;padding-top:10px;`;
  footer.innerHTML = `This is a preview, and some data are hidden 🔒<br>But, the <span style="color:#dc143c;font-weight:bold;">downloaded biodata will contain complete details</span>`;
  const site = document.createElement("div");
  site.textContent = "www.CreateMyBiodata.com";
  site.style.cssText = `position:absolute;bottom:5px;right:15px;font-size:10px;color:#4169e1;font-weight:bold;`;

  container.appendChild(header);
  container.appendChild(inner);
  container.appendChild(footer);
  container.appendChild(site);
}

// Special PDF for Template 5
function downloadTemplate5PDF(element) {
  const pdfWindow = window.open("", "_blank");
  pdfWindow.document.write(`
    <!DOCTYPE html>
    <html>
    <head>
      <title>Biodata Template 5 - Right Side Image</title>
      <style>
        *{margin:0;padding:0;box-sizing:border-box}
        body{font-family:Arial, sans-serif;background:#fff;color:#000}
        #template-content{position:relative;padding:0;min-height:100vh;width:700px;margin:40px auto;background:#fff;border:8px solid #dc143c;box-sizing:border-box;-webkit-print-color-adjust:exact;color-adjust:exact;print-color-adjust:exact}
        @media print{*{-webkit-print-color-adjust:exact!important;color-adjust:exact!important;print-color-adjust:exact!important} #template-content{border:8px solid #dc143c !important;width:700px !important;max-width:700px !important;margin:0 auto !important}}
      </style>
    </head>
    <body>
      <div id="template-content">
        ${element.innerHTML}
      </div>
      <script>
        window.onload = function(){setTimeout(function(){window.print();setTimeout(function(){window.close();},1000);},500)};
      <\/script>
    </body>
    </html>
  `);
  pdfWindow.document.close();
}

// Show upgrade modal for premium templates
function showUpgradeModal() {
  alert(
    "🚀 Upgrade to Premium!\n\nUnlock access to all premium templates and advanced features.\n\nClick OK to go to the upgrade page."
  );
  window.location.href = "upgrade.html";
}

// Make functions globally accessible
window.selectTemplate = selectTemplate;
window.handleDownload = handleDownload;
window.backToGallery = backToGallery;
window.hideRegistrationModal = hideRegistrationModal;
window.submitRegistration = submitRegistration;

window.sendFreeTemplateToEmail = sendFreeTemplateToEmail;

// Initialize
window.addEventListener("DOMContentLoaded", () => {
  loadFormData();
});
