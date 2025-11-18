// API Configuration and HTTP Client
// Prefer same-origin calls when the page is served over HTTP(S),
// fall back to localhost in file:// or unknown cases.
const API_BASE_URL =
  typeof window !== "undefined" &&
  window.location &&
  window.location.origin &&
  !String(window.location.origin).startsWith("file")
    ? window.location.origin
    : "http://127.0.0.1:8000";

class APIClient {
  constructor() {
    this.baseURL = API_BASE_URL;
  }

  // Read a cookie value by name (used to get csrftoken)
  getCookie(name) {
    if (typeof document === 'undefined' || !document.cookie) return null;
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.startsWith(name + '=')) {
        return decodeURIComponent(cookie.substring(name.length + 1));
      }
    }
    return null;
  }
  getToken() {
    return localStorage.getItem("token");
  }

  getHeaders(includeAuth = true) {
    const headers = {
      Accept: "application/json",
    };

    if (includeAuth) {
      const token = this.getToken();
      if (token) {
        headers["Authorization"] = `Token ${token}`;
      }
    }

    return headers;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const headers = this.getHeaders(options.includeAuth !== false);

    // Don't set Content-Type for FormData
    if (!(options.body instanceof FormData)) {
      headers["Content-Type"] = "application/json";
    }

    // Merge headers from defaults and caller
    const mergedHeaders = {
      ...headers,
      ...options.headers,
    };

    // If this is a state-changing request (POST/PUT/PATCH/DELETE) and
    // no CSRF header was provided, try to read the csrftoken cookie and
    // add the X-CSRFToken header so Django accepts the request.
    const method = (options.method || 'GET').toUpperCase();
    if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(method) && !mergedHeaders['X-CSRFToken']) {
      const csrftoken = this.getCookie('csrftoken');
      if (csrftoken) mergedHeaders['X-CSRFToken'] = csrftoken;
    }

    const config = {
      ...options,
      headers: mergedHeaders,
      // Ensure same-origin credentials so cookies (including csrftoken) are sent
      credentials: options.credentials || 'same-origin',
    };

    try {
      const response = await fetch(url, config);

      // Handle 401 Unauthorized
      if (response.status === 401) {
        localStorage.removeItem("token");
        localStorage.removeItem("username");
        window.location.href = "login.html";
        throw new Error("Unauthorized");
      }

      if (!response.ok) {
        // Try to parse JSON error details, fall back to text then status
        let message = `HTTP error! status: ${response.status}`;
        try {
          const errorData = await response.json();
          if (typeof errorData === "string") {
            message = errorData;
          } else if (errorData.detail || errorData.error) {
            message = errorData.detail || errorData.error;
          } else {
            // Flatten first field error if present
            const firstKey = Object.keys(errorData)[0];
            const firstVal = firstKey ? errorData[firstKey] : null;
            if (Array.isArray(firstVal) && firstVal.length) {
              message = `${firstKey}: ${firstVal[0]}`;
            }
          }
        } catch (_) {
          try {
            const text = await response.text();
            if (text) message = text;
          } catch (_) {}
        }
        throw new Error(message);
      }

      return await response.json();
    } catch (error) {
      // Enhance diagnostics for common network/CORS problems
      const isNetworkError =
        error instanceof TypeError &&
        /Failed to fetch/i.test(error.message || "");
      if (isNetworkError) {
        const hints = [];
        hints.push(`Cannot reach: ${url}`);
        if (
          /^https:/i.test(window.location.href) &&
          /^http:/i.test(this.baseURL)
        ) {
          hints.push(
            "Possible mixed content: calling HTTP from an HTTPS page will be blocked by the browser."
          );
        }
        if (
          typeof window !== "undefined" &&
          String(window.location.origin || "").startsWith("file")
        ) {
          hints.push(
            "The page is opened via file://. Use a local web server or serve via the backend to avoid CORS issues."
          );
        }
        if (/127\.0\.0\.1|localhost/.test(this.baseURL)) {
          hints.push(
            "Make sure your backend is running on this address and port."
          );
        }
        console.error(
          "API Error (network/CORS):",
          error,
          "\nHints:",
          hints.join(" ")
        );
      } else {
        console.error("API Error:", error);
      }
      throw error;
    }
  }

  // GET request
  async get(endpoint, options = {}) {
    return this.request(endpoint, {
      ...options,
      method: "GET",
    });
  }

  // POST request
  async post(endpoint, data, options = {}) {
    const body = data instanceof FormData ? data : JSON.stringify(data);

    return this.request(endpoint, {
      ...options,
      method: "POST",
      body,
    });
  }

  // PUT request
  async put(endpoint, data, options = {}) {
    return this.request(endpoint, {
      ...options,
      method: "PUT",
      body: JSON.stringify(data),
    });
  }

  // DELETE request
  async delete(endpoint, options = {}) {
    return this.request(endpoint, {
      ...options,
      method: "DELETE",
    });
  }

  // Auth endpoints
  async login(username, password) {
    return this.post(
      "/api/auth/login/",
      { username, password },
      { includeAuth: false }
    );
  }

  async register(username, password, email = "") {
    return this.post(
      "/api/auth/register/",
      { username, password, email },
      { includeAuth: false }
    );
  }

  // Biodata endpoints
  async createBiodata(formData) {
    return this.post("/api/biodata/", formData);
  }

  async getBiodataList() {
    return this.get("/api/biodata/");
  }

  // Payment endpoints
  async getPaymentStatus() {
    return this.get("/api/payment/status/");
  }

  async submitPaymentVerification(transactionId, screenshot) {
    const formData = new FormData();
    formData.append("transaction_id", transactionId);
    if (screenshot) {
      formData.append("screenshot", screenshot);
    }
    return this.post("/api/payment/verify/", formData);
  }
}

// Export singleton instance
const api = new APIClient();
