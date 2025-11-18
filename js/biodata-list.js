// Biodata List JavaScript

async function loadBiodataList() {
  const loading = document.getElementById("loading");
  const error = document.getElementById("error");
  const empty = document.getElementById("empty");
  const container = document.getElementById("biodata-container");

  try {
    const data = await api.getBiodataList();

    const biodataList = data.results || data;

    loading.classList.add("hidden");

    if (biodataList.length === 0) {
      empty.classList.remove("hidden");
    } else {
      container.classList.remove("hidden");
      renderBiodataList(biodataList);
    }
  } catch (err) {
    loading.classList.add("hidden");
    error.classList.remove("hidden");
    error.textContent = "Error: " + err.message;
  }
}

function renderBiodataList(list) {
  const container = document.getElementById("biodata-container");

  list.forEach((item) => {
    const card = document.createElement("div");
    card.className = "border rounded-lg p-4 bg-white shadow-sm mb-4";

    card.innerHTML = `
            <div class="flex flex-col md:flex-row gap-4">
                <!-- Profile Image -->
                ${
                  item.profile_image
                    ? `
                    <div class="flex-shrink-0">
                        <img 
                            src="http://127.0.0.1:8000${item.profile_image}" 
                            alt="${item.name}" 
                            class="w-24 h-24 object-cover rounded-md"
                        >
                    </div>
                `
                    : ""
                }
                
                <!-- Details -->
                <div class="flex-1">
                    <h3 class="text-xl font-semibold text-gray-800 mb-2">${
                      item.name || "N/A"
                    }</h3>
                    
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
                        ${renderField("Date of Birth", item.date_of_birth)}
                        ${renderField("Place of Birth", item.place_of_birth)}
                        ${renderField("Time of Birth", item.time_of_birth)}
                        ${renderField("Height", item.height)}
                        ${renderField("Education", item.education)}
                        ${renderField("Occupation", item.occupation)}
                        ${renderField("Father's Name", item.father_name)}
                        ${renderField("Mother's Name", item.mother_name)}
                        ${renderField("Contact Number", item.contact_number)}
                        ${renderField("Email", item.email_id)}
                    </div>
                    
                    ${
                      item.created_at
                        ? `
                        <p class="mt-2 text-xs text-gray-500">
                            Created: ${formatDate(item.created_at)}
                        </p>
                    `
                        : ""
                    }
                </div>
            </div>
        `;

    container.appendChild(card);
  });
}

function renderField(label, value) {
  if (!value || value === "N/A") return "";

  return `
        <div>
            <span class="font-medium text-gray-700">${label}:</span>
            <span class="text-gray-600">${value}</span>
        </div>
    `;
}

// Load on page load
window.addEventListener("DOMContentLoaded", loadBiodataList);
