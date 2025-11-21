// Biodata Form JavaScript

// Initial form data structure
const initialFormData = {
  PersonalDetails: {
    name: { label: "Name", value: "" },
    date_of_birth: { label: "Birth Date", value: "" },
    place_of_birth: { label: "Birth Place", value: "" },
    time_of_birth: { label: "Birth Time", value: "" },
    height: { label: "Height", value: "" },
    education: { label: "Education", value: "" },
    residency_city: { label: "Residency City", value: "" },
    visa_status: { label: "Visa Status", value: "" },
    marriage_status: { label: "Marriage Status", value: "" },
    any_disability: { label: "Any Disability", value: "" },
  },
  FamilyDetails: {
    father_name: { label: "Father Name", value: "" },
    father_occupation: { label: "Father Occupation", value: "" },
    father_contact: { label: "Father Contact No.", value: "" },
    mother_name: { label: "Mother Name", value: "" },
    mother_occupation: { label: "Mother Occupation", value: "" },
    mother_contact: { label: "Mother Contact No.", value: "" },
    siblings: { label: "Any Sibling", value: "" },
    parents_residency: { label: "Parents Residency", value: "" },
    type_of_brahmin: { label: "Type Of Brahmin", value: "" },
    gotra: { label: "Gotra", value: "" },
    kuldevi: { label: "Kuldevi", value: "" },
    father_vatan: { label: "Father Vatan", value: "" },
    mother_vatan: { label: "Mother Vatan", value: "" },
  },
  HabitsDeclaration: {
    eating_habits: { label: "Eating Habits (Pure Veg?)", value: "" },
    alcoholic_drinks: { label: "Alcoholic Drinks (Yes/No)?", value: "" },
    smoke: { label: "Smoke? (Yes/No)", value: "" },
    other_habbit: { label: "Any Other Habit?", value: "" },
    legal_or_police_case: { label: "Any Legal or Police Case?", value: "" },
    choice_and_expectations: { label: "Choice and Expectations", value: "" },
  },
};

// Mandatory fields that cannot be edited or deleted
const mandatoryFields = {
  PersonalDetails: ["name", "date_of_birth", "place_of_birth"],
  FamilyDetails: ["father_name", "mother_name"],
  HabitsDeclaration: [],
};

// Field order for each section
const fieldOrder = {
  PersonalDetails: Object.keys(initialFormData.PersonalDetails),
  FamilyDetails: Object.keys(initialFormData.FamilyDetails),
  HabitsDeclaration: Object.keys(initialFormData.HabitsDeclaration),
};

// Helper to get default field order for a section
function getDefaultFieldOrder(section) {
  return initialFormData[section] ? Object.keys(initialFormData[section]) : [];
}

// Helper to ensure field order is valid
function ensureValidFieldOrder(section) {
  if (!Array.isArray(fieldOrder[section])) {
    console.warn(`Invalid fieldOrder for ${section}, resetting to defaults`);
    fieldOrder[section] = getDefaultFieldOrder(section);
  }
}

// Current form data
let formData = JSON.parse(JSON.stringify(initialFormData));
let imageFile = null;
let imagePreview = null;

// Currently expanded section
let expandedSection = "PersonalDetails";

// Initialize form
function initForm() {
  console.debug && console.debug("initForm start");
  console.log("[Debug] Initial formData:", JSON.stringify(formData, null, 2));
  console.log(
    "[Debug] Initial fieldOrder:",
    JSON.stringify(fieldOrder, null, 2)
  );

  // Load saved data from localStorage
  const saved = localStorage.getItem("biodataForm");
  if (saved) {
    try {
      const parsed = JSON.parse(saved);
      // Merge saved data into the initial structure so missing keys don't
      // cause sections to render empty. This keeps default fields intact
      // while restoring user-entered values.
      if (parsed.formData) {
        // iterate sections and fields, copy values where present
        Object.keys(initialFormData).forEach((section) => {
          // ensure section exists
          if (!parsed.formData[section]) return;
          Object.keys(initialFormData[section]).forEach((fieldKey) => {
            if (
              parsed.formData[section] &&
              Object.prototype.hasOwnProperty.call(
                parsed.formData[section],
                fieldKey
              )
            ) {
              // keep the original label, but restore the saved value
              formData[section][fieldKey].value =
                parsed.formData[section][fieldKey].value || "";
              if (parsed.formData[section][fieldKey].label) {
                formData[section][fieldKey].label =
                  parsed.formData[section][fieldKey].label;
              }
            }
          });
          // also restore any custom fields that the user added previously
          if (parsed.formData[section]) {
            Object.keys(parsed.formData[section]).forEach((k) => {
              if (!Object.prototype.hasOwnProperty.call(formData[section], k)) {
                formData[section][k] = parsed.formData[section][k];
              }
            });
          }
        });
      }

      // Restore ordering if present, otherwise use defaults
      if (parsed.fieldOrder) {
        // Validate each section's field order
        Object.keys(initialFormData).forEach((section) => {
          if (!Array.isArray(parsed.fieldOrder[section])) {
            console.warn(
              `Invalid saved fieldOrder for ${section}, will use defaults`
            );
            parsed.fieldOrder[section] = getDefaultFieldOrder(section);
          }
        });
        Object.assign(fieldOrder, parsed.fieldOrder);
      }

      if (parsed.imagePreview) {
        imagePreview = parsed.imagePreview;
        showImagePreview(imagePreview);
      }
    } catch (e) {
      console.error("Error loading saved data:", e);
    }
  }

  // Render all sections
  renderSection("PersonalDetails");
  console.debug && console.debug("rendered section", "PersonalDetails");
  renderSection("FamilyDetails");
  console.debug && console.debug("rendered section", "FamilyDetails");
  renderSection("HabitsDeclaration");
  console.debug && console.debug("rendered section", "HabitsDeclaration");

  // Setup section headers
  setupSectionHeaders();

  // Setup image upload
  setupImageUpload();

  // Setup form submission
  setupFormSubmission();

  // Setup add field buttons
  setupAddFieldButtons();

  // Auto-save on changes
  setupAutoSave();

  // Setup reset button
  setupResetButton();
}

// Setup reset button functionality
function setupResetButton() {
  const resetBtn = document.getElementById("reset-form-btn");
  if (!resetBtn) return;

  resetBtn.addEventListener("click", () => {
    // Clear local storage
    localStorage.removeItem("biodataForm");

    // Reset form data to initial state
    formData = JSON.parse(JSON.stringify(initialFormData));
    fieldOrder.PersonalDetails = Object.keys(initialFormData.PersonalDetails);
    fieldOrder.FamilyDetails = Object.keys(initialFormData.FamilyDetails);
    fieldOrder.HabitsDeclaration = Object.keys(
      initialFormData.HabitsDeclaration
    );

    // Clear image preview
    imageFile = null;
    imagePreview = null;
    const preview = document.getElementById("image-preview");
    const icon = document.querySelector(".camera-icon");
    if (preview && icon) {
      preview.classList.add("hidden");
      icon.classList.remove("hidden");
      preview.src = "";
    }

    // Re-render all sections
    renderSection("PersonalDetails");
    renderSection("FamilyDetails");
    renderSection("HabitsDeclaration");

    // Expand first section
    expandSection("PersonalDetails");
  });
}

// Setup section headers (collapse/expand)
function setupSectionHeaders() {
  document.querySelectorAll(".section-header").forEach((header) => {
    header.addEventListener("click", () => {
      const section = header.dataset.section;
      toggleSection(section);
    });
  });

  // Expand first section by default
  expandSection("PersonalDetails");
}

// Toggle section
function toggleSection(section) {
  if (expandedSection === section) {
    collapseSection(section);
    expandedSection = null;
  } else {
    if (expandedSection) {
      collapseSection(expandedSection);
    }
    expandSection(section);
    expandedSection = section;
  }
}

// Expand section
function expandSection(section) {
  const header = document.querySelector(
    `.section-header[data-section="${section}"]`
  );
  const content = document.getElementById(`${section}-content`);

  if (header && content) {
    header.classList.add("expanded");
    content.classList.remove("hidden");
  }
}

// Collapse section
function collapseSection(section) {
  const header = document.querySelector(
    `.section-header[data-section="${section}"]`
  );
  const content = document.getElementById(`${section}-content`);

  if (header && content) {
    header.classList.remove("expanded");
    content.classList.add("hidden");
  }
}

// Render section fields
function renderSection(section) {
  const container = document.getElementById(`${section}-fields`);
  if (!container) return;

  container.innerHTML = "";

  // Ensure we have valid field order
  ensureValidFieldOrder(section);

  // Debug section data before rendering
  console.log(`[Debug] Rendering section ${section}:`, {
    fieldOrder: fieldOrder[section],
    formDataSection: formData[section],
  });

  // Render fields in order
  fieldOrder[section].forEach((fieldKey) => {
    const field = formData[section][fieldKey];
    if (!field) {
      console.warn(`[Debug] Missing field data for ${section}.${fieldKey}`);
      return;
    }

    const fieldElement = createFieldElement(section, fieldKey, field);
    container.appendChild(fieldElement);
  });

  // Note: Drag and drop functionality removed
}

// Create field element
function createFieldElement(section, fieldKey, field) {
  const isMandatory = mandatoryFields[section]?.includes(fieldKey);

  const div = document.createElement("div");
  div.className = "field-item";
  div.dataset.fieldKey = fieldKey;

    div.innerHTML = `
      <div class="flex items-start gap-2">
        <!-- Field Content -->
        <div class="field-label-container">
          <div class="field-label-display">
            <label class="field-label ${isMandatory ? "mandatory" : ""}">
              ${field.label}
            </label>
          </div>

          <!-- Field Input -->
          <div class="field-input-container">
            ${renderFieldInput(section, fieldKey, field)}
          </div>
        </div>
      </div>
    `;

  return div;
}

// Render field input based on type
function renderFieldInput(section, fieldKey, field) {
  if (fieldKey === "date_of_birth") {
    return `<input type="date" class="form-input" value="${field.value}" onchange="updateFieldValue('${section}', '${fieldKey}', this.value)">`;
  } else if (fieldKey === "height") {
    const heights = generateHeightOptions();
    return `
            <select class="form-select" onchange="updateFieldValue('${section}', '${fieldKey}', this.value)">
                <option value="">Select Height</option>
                ${heights
                  .map(
                    (h) =>
                      `<option value="${h}" ${
                        field.value === h ? "selected" : ""
                      }>${h}</option>`
                  )
                  .join("")}
            </select>
        `;
  } else if (
    fieldKey === "time_of_birth" ||
    fieldKey.includes("address") ||
    fieldKey.includes("expectations")
  ) {
    return `<textarea class="form-textarea" placeholder="Enter ${field.label}" onchange="updateFieldValue('${section}', '${fieldKey}', this.value)">${field.value}</textarea>`;
  } else {
    return `<input type="text" class="form-input" placeholder="Enter ${field.label}" value="${field.value}" onchange="updateFieldValue('${section}', '${fieldKey}', this.value)">`;
  }
}

// Update field value
function updateFieldValue(section, fieldKey, value) {
  if (formData[section] && formData[section][fieldKey]) {
    formData[section][fieldKey].value = value;
    saveToLocalStorage();
  }
}

// Edit field label functionality removed

// Delete field function removed - fields are now permanent

// Setup drag and drop
function setupDragAndDrop(section) {
  const container = document.getElementById(`${section}-fields`);
  if (!container) return;

  // Guard: if Sortable is not available or failed to load, skip drag/drop setup
  if (typeof Sortable === "undefined") {
    console.warn &&
      console.warn(
        "Sortable library not found - drag/drop disabled for",
        section
      );
    return;
  }

  try {
    new Sortable(container, {
      animation: 150,
      handle: ".drag-handle",
      ghostClass: "sortable-ghost",
      dragClass: "sortable-drag",
      onEnd: (evt) => {
        // Update field order
        const newOrder = Array.from(container.children).map(
          (el) => el.dataset.fieldKey
        );
        fieldOrder[section] = newOrder;
        saveToLocalStorage();
      },
    });
  } catch (err) {
    console.error &&
      console.error("Error initializing Sortable for", section, err);
  }
}

// Setup add field buttons
function setupAddFieldButtons() {
  document.querySelectorAll(".add-field-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      const section = btn.dataset.section;
      addField(section);
    });
  });
}

// Add new field
function addField(section) {
  const fieldKey = `customField_${Date.now()}`;
  formData[section][fieldKey] = {
    label: "New Field",
    value: "",
  };
  fieldOrder[section].push(fieldKey);
  renderSection(section);
  saveToLocalStorage();

  // Auto-edit the new field label
  setTimeout(() => editFieldLabel(section, fieldKey), 100);
}

// Setup image upload
function setupImageUpload() {
  const input = document.getElementById("profile-image");
  if (!input) return;
  input.addEventListener("change", async (e) => {
    const file = e.target.files[0];
    if (file) {
      imageFile = file;
      imagePreview = await fileToBase64(file);
      showImagePreview(imagePreview);
      saveToLocalStorage();
    }
  });
}

// Show image preview
function showImagePreview(src) {
  const preview = document.getElementById("image-preview");
  const icon = document.querySelector(".camera-icon");

  if (preview && icon) {
    preview.src = src;
    preview.classList.remove("hidden");
    icon.classList.add("hidden");
  }
}

// Setup form submission
function setupFormSubmission() {
  const form = document.getElementById("biodata-form");
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    await submitForm();
  });
}

// Submit form
async function submitForm() {
  const submitBtn = document.querySelector('button[type="submit"]');
  submitBtn.disabled = true;
  submitBtn.textContent = "Submitting...";

  try {
    // Prepare form data
    const formDataToSend = new FormData();


    // Add all fields
    Object.entries(formData).forEach(([section, fields]) => {
      Object.entries(fields).forEach(([key, field]) => {
        if (field.value && field.value.trim()) {
          formDataToSend.append(key, field.value);
        }
      });
    });
    // Always set template_choice=1 for free biodata
    formDataToSend.append('template_choice', '1');

    // Add image if present
    if (imageFile) {
      formDataToSend.append("profile_image", imageFile);
    }

    // Submit to API
    const result = await api.createBiodata(formDataToSend);

    // Store biodata ID for download
    if (result && result.id) {
      localStorage.setItem('biodata_id', result.id);
    }

    // Clear localStorage
    localStorage.removeItem("biodataForm");

    // Redirect to template page with data
    localStorage.setItem(
      "formDataForTemplate",
      JSON.stringify({
        PersonalDetails: Object.fromEntries(
          Object.entries(formData.PersonalDetails).map(([k, v]) => [k, v.value])
        ),
        FamilyDetails: Object.fromEntries(
          Object.entries(formData.FamilyDetails).map(([k, v]) => [k, v.value])
        ),
        HabitsDeclaration: Object.fromEntries(
          Object.entries(formData.HabitsDeclaration).map(([k, v]) => [
            k,
            v.value,
          ])
        ),
        imagePreview,
      })
    );

    window.location.href = "template-page.html";
  } catch (error) {
    alert("Error submitting form: " + error.message);
    submitBtn.disabled = false;
    submitBtn.textContent = "Generate Biodata";
  }
}

// Save to localStorage
function saveToLocalStorage() {
  localStorage.setItem(
    "biodataForm",
    JSON.stringify({
      formData,
      fieldOrder,
      imagePreview,
    })
  );
}

// Setup auto-save
function setupAutoSave() {
  // Save every 5 seconds if there are changes
  setInterval(saveToLocalStorage, 5000);
}

// Initialize when DOM is ready
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initForm);
} else {
  initForm();
}
