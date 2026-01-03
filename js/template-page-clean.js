// Template Page JavaScript - Clean Version

let formData = null;
let selectedTemplate = null;

// Load form data from localStorage or sessionStorage
function loadFormData() {
  let saved = localStorage.getItem("formDataForTemplate");
  if (!saved) {
    saved = sessionStorage.getItem("formDataForTemplate");
  }
  if (saved) {
    try {
      formData = JSON.parse(saved);
    } catch (e) {
      console.error("Error loading form data:", e);
      alert("Error loading biodata data. Please create a new biodata.");
      window.location.href = "biodata-form.html";
    }
  } else {
    alert("No biodata data found. Please create a biodata first.");
    window.location.href = "biodata-form.html";
  }
}

// Select template
function selectTemplate(templateId) {
  try {
    selectedTemplate = templateId;
    const gallery = document.getElementById("template-gallery");
    const view = document.getElementById("template-view");
    
    if (gallery && view) {
      gallery.classList.add("hidden");
      view.classList.remove("hidden");
      renderTemplate(templateId);
      updateDownloadButton(templateId);
    } else {
      console.error("Required DOM elements not found");
    }
  } catch (error) {
    console.error("Error in selectTemplate:", error);
    alert("Error loading template. Please refresh the page and try again.");
  }
}

// Update download button for premium templates
function updateDownloadButton(templateId) {
  const downloadBtn = document.getElementById("download-btn");
  
  if (!downloadBtn) {
    console.error("Download button not found");
    return;
  }

  if (templateId === 1) {
    // Free template
    downloadBtn.className = "btn btn-primary";
    downloadBtn.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" /><polyline points="7 10 12 15 17 10" /><line x1="12" y1="15" x2="12" y2="3" /></svg>Download PDF';
  } else {
    // Premium template
    downloadBtn.className = "btn download-premium";
    downloadBtn.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg>Register to Download';
  }
}

// Handle download based on template type
function handleDownload() {
  if (selectedTemplate === 1) {
    // Free template - allow direct download
    downloadPDF();
  } else {
    // Premium template - require registration
    showRegistrationModal();
  }
}

// Show registration modal for premium downloads
function showRegistrationModal() {
  try {
    // Populate modal fields (if any saved) and show modal
    const saved = localStorage.getItem("templateRegistration");
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        const nameField = document.getElementById("reg-name");
        const emailField = document.getElementById("reg-email");
        const phoneField = document.getElementById("reg-phone");
        
        if (nameField) nameField.value = parsed.name || "";
        if (emailField) emailField.value = parsed.email || "";
        if (phoneField) phoneField.value = parsed.phone || "";
      } catch (e) {
        console.warn("Could not parse saved registration:", e);
      }
    }

    // Show modal
    const modal = document.getElementById("reg-modal");
    if (modal) {
      modal.classList.remove("hidden");
      modal.focus();
    } else {
      console.error("Registration modal not found");
    }
  } catch (error) {
    console.error("Error showing registration modal:", error);
  }
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
  localStorage.setItem("templateRegistration", JSON.stringify({ name, email, phone }));

  // Build payload from existing local formDataForTemplate
  let saved = localStorage.getItem("formDataForTemplate");
  if (!saved) {
    saved = sessionStorage.getItem("formDataForTemplate");
  }
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

  // Disable UI while submitting
  const submitBtn = document.getElementById("reg-submit");
  submitBtn.disabled = true;
  submitBtn.textContent = "Submitting...";

  try {
    // Create biodata record (will be is_approved=false by default)
    const resp = await api.createBiodata(fd);

    // Show confirmation message to user
    alert("Your biodata has been saved! Please wait for admin approval. You'll receive an email when it's ready for download.");

    // Optionally update UI: mark download as pending
    const downloadBtn = document.getElementById("download-btn");
    downloadBtn.disabled = true;
    downloadBtn.textContent = "Awaiting Approval";

    hideRegistrationModal();
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

// Reset template container to default state
function resetTemplateContainer(container) {
  // Clear content
  container.innerHTML = "";
  
  // Reset any inline styles applied by Template 5
  container.style.cssText = "";
  
  // Reset to default template-content styles
  container.style.cssText = 'background-size: 100% 100%; background-position: center; background-repeat: no-repeat; padding: 60px 80px; position: relative; box-shadow: 0 15px 40px rgba(0, 0, 0, 0.15); border-radius: 0; min-height: 800px; width: 600px; max-width: 600px; margin: 20px auto;';
}

// Render template
function renderTemplate(templateId) {
  const container = document.getElementById("template-content");

  // Reset container to default state first
  resetTemplateContainer(container);

  // Apply different border styles based on template ID
  const borderStyles = [
    "border-style-1", // bg0.png
    "border-style-2", // bg3.jpg
    "border-style-3", // bg6.png
    "border-style-4", // bg8.jpg
    "border-style-5", // bg9.jpg
    "border-style-6", // bg10.jpg
  ];

  // Cycle through border styles based on template ID
  let borderClass = borderStyles[(templateId - 1) % borderStyles.length];

  // For FREE template, force White.png border background
  if (templateId === 1) {
    borderClass = "free-border";
  }

  // Apply border style directly to template-content container
  container.className = borderClass;

  // For Template 5 (Right Side Image), use special rendering
  if (templateId === 5) {
    renderTemplate5(container);
    return;
  }

  // Create biodata content directly without wrapper
  const biodataContent = document.createElement("div");
  biodataContent.className = "biodata-template";
  
  // Profile
  if (formData.imagePreview) {
    const img = document.createElement("img");
    img.src = formData.imagePreview;
    img.alt = "Profile";
    img.className = "biodata-profile-image";
    biodataContent.appendChild(img);
  }

  // Name centered
  const name = (formData.PersonalDetails && formData.PersonalDetails.name) || "";
  if (name) {
    const h2 = document.createElement("h2");
    h2.className = "biodata-name";
    h2.textContent = name;
    biodataContent.appendChild(h2);
  }

  // Helper to build section with exact layout matching screenshot
  function buildSection(title, obj) {
    const sec = document.createElement("div");
    sec.className = "biodata-section";
    const pill = document.createElement("div");
    pill.className = "section-pill";
    pill.textContent = title;
    sec.appendChild(pill);

    // Create two-column layout exactly as shown in screenshot
    const entries = Object.entries(obj || {}).filter(([, value]) => value && value.toString().trim());

    // Split entries into two balanced columns
    const mid = Math.ceil(entries.length / 2);
    const leftEntries = entries.slice(0, mid);
    const rightEntries = entries.slice(mid);

    const columns = document.createElement("div");
    columns.className = "detail-columns";

    // Create left column
    leftEntries.forEach(([key, value]) => {
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
      columns.appendChild(item);
    });

    // Create right column
    rightEntries.forEach(([key, value]) => {
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
      columns.appendChild(item);
    });

    sec.appendChild(columns);
    return sec;
  }

  if (formData.PersonalDetails) {
    biodataContent.appendChild(buildSection("Personal Details", formData.PersonalDetails));
  }
  if (formData.FamilyDetails) {
    biodataContent.appendChild(buildSection("Family Details", formData.FamilyDetails));
  }
  if (formData.HabitsDeclaration) {
    biodataContent.appendChild(buildSection("Habits & Declaration", formData.HabitsDeclaration));
  }

  // Clear container and add content
  container.innerHTML = "";

  // Add watermark for premium templates (template 2, 3, and 4, but not 5 and 6 since they have their own)
  if (templateId !== 1 && templateId !== 5 && templateId !== 6) {
    const watermark = document.createElement("div");
    watermark.className = "premium-watermark";
    watermark.textContent = "BhudevNetworkvivha";
    container.appendChild(watermark);
  }

  container.appendChild(biodataContent);
}

// Special rendering function for Template 5 (Right Side Image Layout)
function renderTemplate5(container) {
  // Clear container and apply red border styling to match the image
  container.innerHTML = "";
  
  // Remove any existing classes and apply Template 5 specific styling
  container.className = "";
  container.style.cssText = 'padding: 0; width: 700px; max-width: 700px; background: white; border: 8px solid #dc143c; box-sizing: border-box; margin: 20px auto; min-height: 800px;';

  // Add watermark for premium template
  const watermark = document.createElement("div");
  watermark.className = "premium-watermark";
  watermark.textContent = "BhudevNetworkvivha";
  container.appendChild(watermark);

  // Create main layout structure
  const templateInner = document.createElement("div");
  templateInner.style.cssText = 'position: relative; z-index: 1; background: white; width: 100%; height: 100%; display: flex; box-sizing: border-box; min-height: 800px;';

  // Header with logo and title
  const biodataHeader = document.createElement("div");
  biodataHeader.style.cssText = 'position: absolute; top: 20px; left: 50%; transform: translateX(-50%); text-align: center; z-index: 10;';
  
  const logo = document.createElement("div");
  logo.textContent = "🕉";
  logo.style.cssText = 'font-size: 24px; color: #dc143c; margin-bottom: 5px; font-weight: bold;';
  
  const title = document.createElement("div");
  title.textContent = "BIO DATA";
  title.style.cssText = 'font-size: 18px; color: #dc143c; font-weight: bold; letter-spacing: 1px;';
  
  biodataHeader.appendChild(logo);
  biodataHeader.appendChild(title);

  // Left content area
  const contentLeft = document.createElement("div");
  contentLeft.style.cssText = 'flex: 1; padding: 80px 30px 30px 30px; background: white;';

  // Right image area
  const contentRight = document.createElement("div");
  contentRight.style.cssText = 'width: 200px; background: white; display: flex; flex-direction: column; align-items: center; justify-content: flex-start; padding: 80px 20px 30px 20px; position: relative;';

  // Helper function to build sections for Template 5
  function buildSection5(title, obj) {
    const sectionTitle = document.createElement("div");
    sectionTitle.textContent = title.toUpperCase();
    sectionTitle.style.cssText = 'background: #4169e1; color: white; padding: 8px 15px; font-weight: bold; font-size: 14px; margin: 20px 0 10px 0; text-transform: uppercase; width: fit-content; font-family: Arial, sans-serif;';
    if (title === "Personal Details") {
      sectionTitle.style.marginTop = "0";
    }
    
    contentLeft.appendChild(sectionTitle);

    const detailColumns = document.createElement("div");
    detailColumns.style.cssText = 'display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 15px;';

    const leftColumn = document.createElement("div");
    const rightColumn = document.createElement("div");

    const entries = Object.entries(obj || {}).filter(([key, value]) => value && value.toString().trim());

    entries.forEach(([key, value], index) => {
      const item = document.createElement("div");
      item.style.cssText = 'margin-bottom: 8px; font-size: 12px; line-height: 1.4; font-family: Arial, sans-serif;';

      const label = document.createElement("div");
      label.textContent = toTitleCase(key);
      label.style.cssText = 'color: #4169e1; font-weight: normal; margin-bottom: 2px;';

      const val = document.createElement("div");
      val.textContent = value;
      val.style.cssText = 'color: #000; font-weight: normal;';

      item.appendChild(label);
      item.appendChild(val);

      // Alternate between left and right columns
      if (index % 2 === 0) {
        leftColumn.appendChild(item);
      } else {
        rightColumn.appendChild(item);
      }
    });

    detailColumns.appendChild(leftColumn);
    detailColumns.appendChild(rightColumn);
    contentLeft.appendChild(detailColumns);
  }

  // Add sections to left content
  if (formData.PersonalDetails) {
    buildSection5("Personal Details", formData.PersonalDetails);
  }
  if (formData.FamilyDetails) {
    buildSection5("Family Details", formData.FamilyDetails);
  }
  if (formData.ContactDetails) {
    buildSection5("Contact Details", formData.ContactDetails);
  }
  if (formData.HabitsDeclaration) {
    buildSection5("Habits & Declaration", formData.HabitsDeclaration);
  }

  // Add profile image to right side
  if (formData.imagePreview) {
    const img = document.createElement("img");
    img.src = formData.imagePreview;
    img.alt = "Profile";
    img.style.cssText = 'width: 150px; height: 180px; object-fit: cover; border: 2px solid #000; margin-bottom: 20px;';
    contentRight.appendChild(img);
  } else {
    const placeholder = document.createElement("div");
    placeholder.style.cssText = 'width: 150px; height: 180px; background: #f0f0f0; border: 2px solid #000; display: flex; align-items: center; justify-content: center; color: #666; font-size: 12px; text-align: center; margin-bottom: 20px; font-family: Arial, sans-serif;';
    placeholder.innerHTML = "Profile<br>Photo";
    contentRight.appendChild(placeholder);
  }

  // Footer disclaimer
  const footerDisclaimer = document.createElement("div");
  footerDisclaimer.style.cssText = 'position: absolute; bottom: 15px; left: 50%; transform: translateX(-50%); text-align: center; font-size: 10px; color: #666; width: 90%; border-top: 1px dashed #ccc; padding-top: 10px; font-family: Arial, sans-serif;';
  footerDisclaimer.innerHTML = 'This is a preview, and some data are hidden 🔒<br>But, the <span style="color: #dc143c; font-weight: bold;">downloaded biodata will contain complete details</span>';

  // Footer website
  const footerWebsite = document.createElement("div");
  footerWebsite.textContent = "www.CreateMyBiodata.com";
  footerWebsite.style.cssText = 'position: absolute; bottom: 5px; right: 15px; font-size: 10px; color: #4169e1; font-weight: bold; font-family: Arial, sans-serif;';

  // Assemble the layout
  templateInner.appendChild(contentLeft);
  templateInner.appendChild(contentRight);
  
  container.appendChild(biodataHeader);
  container.appendChild(templateInner);
  container.appendChild(footerDisclaimer);
  container.appendChild(footerWebsite);
}

// Download PDF
function downloadPDF() {
  const element = document.getElementById("template-content");
  if (!element) {
    alert("No template to download. Please select a template first.");
    return;
  }

  // Special handling for Template 5
  if (selectedTemplate === 5) {
    downloadTemplate5PDF(element);
    return;
  }

  // Get the current border class and extract the border image URL
  const borderClass = element.className;
  const computedStyle = window.getComputedStyle(element);
  const backgroundImage = computedStyle.backgroundImage;

  // Extract the URL from background-image property
  const imageUrl = backgroundImage.match(/url\(["']?([^"']*)["']?\)/);
  const borderImagePath = imageUrl ? imageUrl[1] : "assets/border/bg0.png";

  // Create a new window for PDF generation
  const pdfWindow = window.open("", "_blank");

  const htmlContent = '<!DOCTYPE html><html><head><title>Biodata Template - ' + selectedTemplate + '</title><style>* { margin: 0; padding: 0; box-sizing: border-box; } body { margin: 0; padding: 0; font-family: "Times New Roman", serif; background: white; } #template-content { background-image: url("' + borderImagePath + '") !important; background-size: 100% 100% !important; background-position: center !important; background-repeat: no-repeat !important; padding: 50px 70px !important; min-height: auto !important; height: auto !important; width: 600px !important; max-width: 600px !important; margin: 0 auto !important; position: relative !important; -webkit-print-color-adjust: exact !important; color-adjust: exact !important; print-color-adjust: exact !important; page-break-inside: avoid !important; } .biodata-template { max-width: 100%; margin: 0; background: transparent; padding: 0; border: none; position: relative; z-index: 1; font-family: "Times New Roman", serif; color: #2c3e50; page-break-inside: avoid; } .biodata-name { text-align: center; font-size: 1.25rem; font-weight: bold; color: #2c3e50; margin: 0 0 18px 0; letter-spacing: 1px; font-family: "Times New Roman", serif; } .section-pill { background: linear-gradient(135deg, #e67e22, #d35400); color: white; padding: 7px 18px; border-radius: 20px; font-weight: 600; margin: 0 auto 14px; display: block; width: fit-content; font-size: 0.82rem; text-transform: uppercase; letter-spacing: 0.5px; box-shadow: 0 2px 6px rgba(230, 126, 34, 0.4); font-family: "Times New Roman", serif; } .biodata-section { margin-bottom: 18px; page-break-inside: avoid; } .detail-columns { display: grid; grid-template-columns: 1fr 1fr; column-gap: 22px; row-gap: 4px; margin-top: 8px; padding: 0; position: relative; } .detail-columns::before { content: ""; position: absolute; left: 50%; top: 0; bottom: 0; width: 1px; background-color: #bdc3c7; transform: translateX(-50%); } .detail-item { display: flex; justify-content: space-between; align-items: center; padding: 2px 0; margin-bottom: 2px; } .detail-label { color: #2c3e50; font-weight: 600; font-size: 0.85rem; width: 48%; font-family: "Times New Roman", serif; line-height: 1.4; } .detail-value { color: #34495e; font-size: 0.85rem; width: 48%; text-align: right; font-weight: 500; font-family: "Times New Roman", serif; line-height: 1.4; } .biodata-profile-image { width: 110px; height: 110px; border-radius: 50%; object-fit: cover; margin: 0 auto 14px; display: block; border: 3px solid #8b4513; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2); } .premium-watermark { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%) rotate(-45deg); font-size: 3rem; font-weight: bold; color: rgba(245, 158, 11, 0.3); pointer-events: none; z-index: 15; white-space: nowrap; text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1); letter-spacing: 3px; font-family: Arial, sans-serif; } @media print { * { -webkit-print-color-adjust: exact !important; color-adjust: exact !important; print-color-adjust: exact !important; } body { margin: 0 !important; padding: 0 !important; } #template-content { margin: 0 auto !important; padding: 50px 70px !important; page-break-inside: avoid !important; page-break-after: avoid !important; width: 600px !important; max-width: 600px !important; min-height: auto !important; height: auto !important; background-image: url("' + borderImagePath + '") !important; background-size: 100% 100% !important; background-position: center !important; background-repeat: no-repeat !important; -webkit-print-color-adjust: exact !important; color-adjust: exact !important; print-color-adjust: exact !important; } .biodata-section { page-break-inside: avoid !important; } } @page { size: A4 portrait; margin: 10mm; } </style></head><body><div id="template-content">' + element.innerHTML + '</div><script>window.onload = function() { setTimeout(function() { window.print(); setTimeout(function() { window.close(); }, 1000); }, 500); };</script></body></html>';

  pdfWindow.document.write(htmlContent);
  pdfWindow.document.close();
}

// Special PDF download for Template 5
function downloadTemplate5PDF(element) {
  const pdfWindow = window.open("", "_blank");

  const htmlContent = '<!DOCTYPE html><html><head><title>Biodata Template 5 - Right Side Image</title><style>* { margin: 0; padding: 0; box-sizing: border-box; } body { margin: 0; padding: 0; font-family: Arial, sans-serif; background: white; color: #000; } #template-content { position: relative; padding: 0; min-height: 100vh; width: 700px; margin: 40px auto; background: white; border: 8px solid #dc143c; box-sizing: border-box; -webkit-print-color-adjust: exact; color-adjust: exact; print-color-adjust: exact; } .template-inner { position: relative; z-index: 1; background: white; width: 100%; height: 100%; display: flex; box-sizing: border-box; min-height: 800px; } .biodata-header { position: absolute; top: 20px; left: 50%; transform: translateX(-50%); text-align: center; z-index: 10; } .biodata-logo { font-size: 24px; color: #dc143c; margin-bottom: 5px; font-weight: bold; } .biodata-title { font-size: 18px; color: #dc143c; font-weight: bold; letter-spacing: 1px; } .content-left { flex: 1; padding: 80px 30px 30px 30px; background: white; } .content-right { width: 200px; background: white; display: flex; flex-direction: column; align-items: center; justify-content: flex-start; padding: 80px 20px 30px 20px; position: relative; } .biodata-profile-image { width: 150px; height: 180px; object-fit: cover; border: 2px solid #000; margin-bottom: 20px; } .section-title { background: #4169e1; color: white; padding: 8px 15px; font-weight: bold; font-size: 14px; margin: 20px 0 10px 0; text-transform: uppercase; width: fit-content; } .section-title:first-of-type { margin-top: 0; } .detail-columns { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 15px; } .detail-column { display: block; } .detail-item { margin-bottom: 8px; font-size: 12px; line-height: 1.4; } .detail-label { color: #4169e1; font-weight: normal; margin-bottom: 2px; } .detail-value { color: #000; font-weight: normal; } .footer-disclaimer { position: absolute; bottom: 15px; left: 50%; transform: translateX(-50%); text-align: center; font-size: 10px; color: #666; width: 90%; border-top: 1px dashed #ccc; padding-top: 10px; } .footer-disclaimer .highlight { color: #dc143c; font-weight: bold; } .footer-website { position: absolute; bottom: 5px; right: 15px; font-size: 10px; color: #4169e1; font-weight: bold; } .premium-watermark { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%) rotate(-45deg); font-size: 3rem; font-weight: bold; color: rgba(245, 158, 11, 0.3); pointer-events: none; z-index: 15; white-space: nowrap; text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1); letter-spacing: 3px; font-family: Arial, sans-serif; } @media print { * { -webkit-print-color-adjust: exact !important; color-adjust: exact !important; print-color-adjust: exact !important; } body { margin: 0 !important; padding: 0 !important; } #template-content { margin: 0 auto !important; border: 8px solid #dc143c !important; page-break-inside: avoid !important; page-break-after: avoid !important; width: 700px !important; max-width: 700px !important; min-height: auto !important; height: auto !important; } } @page { size: A4 portrait; margin: 10mm; } </style></head><body><div id="template-content">' + element.innerHTML + '</div><script>window.onload = function() { setTimeout(function() { window.print(); setTimeout(function() { window.close(); }, 1000); }, 500); };</script></body></html>';

  pdfWindow.document.write(htmlContent);
  pdfWindow.document.close();
}

// Show upgrade modal for premium templates
function showUpgradeModal() {
  alert("🚀 Upgrade to Premium!\n\nUnlock access to all premium templates and advanced features.\n\nClick OK to go to the upgrade page.");
  window.location.href = "upgrade.html";
}

// Make functions globally accessible
window.selectTemplate = selectTemplate;
window.handleDownload = handleDownload;
window.backToGallery = backToGallery;
window.hideRegistrationModal = hideRegistrationModal;
window.submitRegistration = submitRegistration;

// Initialize
window.addEventListener("DOMContentLoaded", () => {
  loadFormData();
});