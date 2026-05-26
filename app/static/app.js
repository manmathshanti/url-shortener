const tokenKey = "url_shortener_token";
const userKey = "url_shortener_user";

const elements = {
  registerForm: document.getElementById("register-form"),
  loginForm: document.getElementById("login-form"),
  logoutButton: document.getElementById("logout-button"),
  shortenForm: document.getElementById("shorten-form"),
  analyticsForm: document.getElementById("analytics-form"),
  refreshUrlsButton: document.getElementById("refresh-urls"),
  createResult: document.getElementById("create-result"),
  urlsList: document.getElementById("urls-list"),
  urlsEmpty: document.getElementById("urls-empty"),
  analyticsResult: document.getElementById("analytics-result"),
  toast: document.getElementById("toast"),
  statusDot: document.getElementById("status-dot"),
  statusLabel: document.getElementById("status-label"),
  statusText: document.getElementById("status-text"),
  sessionState: document.getElementById("session-state"),
};

function getToken() {
  return localStorage.getItem(tokenKey);
}

function getSavedUser() {
  const raw = localStorage.getItem(userKey);
  if (!raw) {
    return null;
  }

  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

function setSession(token, user = null) {
  if (token) {
    localStorage.setItem(tokenKey, token);
  } else {
    localStorage.removeItem(tokenKey);
  }

  if (user) {
    localStorage.setItem(userKey, JSON.stringify(user));
  } else if (!token) {
    localStorage.removeItem(userKey);
  }

  updateSessionLabel();
}

function updateSessionLabel() {
  const token = getToken();
  const user = getSavedUser();

  if (!token) {
    elements.sessionState.textContent = "Signed out";
    elements.urlsEmpty.textContent = "Login to load your saved short URLs.";
    return;
  }

  elements.sessionState.textContent = user?.email || "Signed in";
}

function showToast(message, type = "success") {
  elements.toast.textContent = message;
  elements.toast.className = `toast ${type}`;
  setTimeout(() => {
    elements.toast.className = "toast hidden";
  }, 2800);
}

async function apiFetch(path, options = {}) {
  const headers = new Headers(options.headers || {});
  headers.set("Content-Type", "application/json");

  const token = getToken();
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(path, {
    ...options,
    headers,
  });

  const contentType = response.headers.get("content-type") || "";
  const body = contentType.includes("application/json") ? await response.json() : null;

  if (!response.ok) {
    const detail = body?.detail;
    const errorMessage = Array.isArray(detail)
      ? detail.map((item) => item.msg).join(", ")
      : detail || "Request failed";
    throw new Error(errorMessage);
  }

  return body;
}

function formatDate(value) {
  if (!value) {
    return "Never";
  }

  return new Date(value).toLocaleString();
}

function renderCreateResult(item) {
  elements.createResult.classList.remove("hidden");
  elements.createResult.innerHTML = `
    <div class="url-card-header">
      <div>
        <p class="eyebrow">Short URL created</p>
        <strong>${item.short_url}</strong>
      </div>
      <div class="url-card-actions">
        <a class="button button-primary" href="${item.short_url}" target="_blank" rel="noreferrer">Open</a>
        <button class="button button-secondary" type="button" data-copy="${item.short_url}">Copy</button>
      </div>
    </div>
    <p><strong>Original:</strong> ${item.original_url}</p>
    <p><strong>Short code:</strong> ${item.short_code}</p>
  `;
}

function renderUrls(items) {
  if (!items.length) {
    elements.urlsList.innerHTML = "";
    elements.urlsEmpty.textContent = getToken()
      ? "No short URLs yet. Create your first one above."
      : "Login to load your saved short URLs.";
    elements.urlsEmpty.classList.remove("hidden");
    return;
  }

  elements.urlsEmpty.classList.add("hidden");
  elements.urlsList.innerHTML = items.map((item) => `
    <article class="url-card">
      <div class="url-card-header">
        <div>
          <p class="eyebrow">${item.short_code}</p>
          <strong>${item.short_url}</strong>
        </div>
        <div class="url-card-actions">
          <a class="button button-primary" href="${item.short_url}" target="_blank" rel="noreferrer">Open</a>
          <button class="button button-secondary" type="button" data-copy="${item.short_url}">Copy</button>
          <button class="button button-secondary" type="button" data-analytics="${item.short_code}">Analytics</button>
          <button class="button button-secondary" type="button" data-delete="${item.short_code}">Delete</button>
        </div>
      </div>
      <div class="url-meta">
        <div><strong>Original:</strong> ${item.original_url}</div>
        <div><strong>Clicks:</strong> ${item.total_clicks}</div>
        <div><strong>Created:</strong> ${formatDate(item.created_at)}</div>
        <div><strong>Last accessed:</strong> ${formatDate(item.last_accessed_at)}</div>
      </div>
    </article>
  `).join("");
}

function renderAnalytics(item) {
  elements.analyticsResult.innerHTML = `
    <article class="analytics-card">
      <p class="eyebrow">Analytics</p>
      <strong>${item.short_url}</strong>
      <p><strong>Original:</strong> ${item.original_url}</p>
      <div class="metric-grid">
        <div class="metric">
          <span>Total Clicks</span>
          <strong>${item.total_clicks}</strong>
        </div>
        <div class="metric">
          <span>Created At</span>
          <strong>${formatDate(item.created_at)}</strong>
        </div>
        <div class="metric">
          <span>Last Accessed</span>
          <strong>${formatDate(item.last_accessed_at)}</strong>
        </div>
        <div class="metric">
          <span>Short Code</span>
          <strong>${item.short_code}</strong>
        </div>
      </div>
    </article>
  `;
}

async function checkHealth() {
  try {
    const response = await fetch("/health");
    const data = await response.json();
    elements.statusDot.classList.add("online");
    elements.statusLabel.textContent = "API is healthy";
    elements.statusText.textContent = `${data.service} is responding normally.`;
  } catch {
    elements.statusDot.classList.add("offline");
    elements.statusLabel.textContent = "API unreachable";
    elements.statusText.textContent = "The backend health check failed.";
  }
}

async function loadUrls() {
  if (!getToken()) {
    renderUrls([]);
    return;
  }

  try {
    const items = await apiFetch("/urls", { method: "GET" });
    renderUrls(items);
  } catch (error) {
    if (error.message.toLowerCase().includes("validate credentials")) {
      setSession(null);
    }
    renderUrls([]);
    showToast(error.message, "error");
  }
}

async function loadAnalytics(shortCode) {
  try {
    const item = await apiFetch(`/urls/${encodeURIComponent(shortCode)}/analytics`, { method: "GET" });
    renderAnalytics(item);
    elements.analyticsForm.elements.short_code.value = shortCode;
  } catch (error) {
    showToast(error.message, "error");
  }
}

async function handleRegister(event) {
  event.preventDefault();
  const form = new FormData(event.currentTarget);

  try {
    const user = await apiFetch("/auth/register", {
      method: "POST",
      body: JSON.stringify({
        email: form.get("email"),
        username: form.get("username"),
        password: form.get("password"),
      }),
    });
    localStorage.setItem(userKey, JSON.stringify(user));
    showToast("Registration successful. You can log in now.");
    event.currentTarget.reset();
    updateSessionLabel();
  } catch (error) {
    showToast(error.message, "error");
  }
}

async function handleLogin(event) {
  event.preventDefault();
  const form = new FormData(event.currentTarget);

  try {
    const result = await apiFetch("/auth/login", {
      method: "POST",
      body: JSON.stringify({
        email: form.get("email"),
        password: form.get("password"),
      }),
    });
    setSession(result.access_token, { email: form.get("email") });
    showToast("Logged in successfully.");
    await loadUrls();
  } catch (error) {
    showToast(error.message, "error");
  }
}

function handleLogout() {
  setSession(null);
  elements.urlsList.innerHTML = "";
  elements.analyticsResult.innerHTML = '<div class="analytics-placeholder">No analytics loaded yet.</div>';
  elements.createResult.classList.add("hidden");
  showToast("Logged out.");
}

async function handleShorten(event) {
  event.preventDefault();

  if (!getToken()) {
    showToast("Login required to create short URLs.", "error");
    return;
  }

  const form = new FormData(event.currentTarget);
  const payload = {
    original_url: form.get("original_url"),
  };
  const customAlias = String(form.get("custom_alias") || "").trim();
  if (customAlias) {
    payload.custom_alias = customAlias;
  }

  try {
    const item = await apiFetch("/urls", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    renderCreateResult(item);
    showToast("Short URL created.");
    event.currentTarget.reset();
    await loadUrls();
  } catch (error) {
    showToast(error.message, "error");
  }
}

async function handleAnalyticsSubmit(event) {
  event.preventDefault();
  const shortCode = event.currentTarget.elements.short_code.value.trim();
  if (!shortCode) {
    return;
  }
  await loadAnalytics(shortCode);
}

async function handleDelete(shortCode) {
  try {
    await apiFetch(`/urls/${encodeURIComponent(shortCode)}`, {
      method: "DELETE",
      headers: {},
    });
    showToast("URL deleted.");
    await loadUrls();
  } catch (error) {
    showToast(error.message, "error");
  }
}

async function handleListClick(event) {
  const copyValue = event.target.dataset.copy;
  const analyticsCode = event.target.dataset.analytics;
  const deleteCode = event.target.dataset.delete;

  if (copyValue) {
    await navigator.clipboard.writeText(copyValue);
    showToast("Copied to clipboard.");
    return;
  }

  if (analyticsCode) {
    await loadAnalytics(analyticsCode);
    return;
  }

  if (deleteCode) {
    await handleDelete(deleteCode);
  }
}

function bindEvents() {
  elements.registerForm.addEventListener("submit", handleRegister);
  elements.loginForm.addEventListener("submit", handleLogin);
  elements.logoutButton.addEventListener("click", handleLogout);
  elements.shortenForm.addEventListener("submit", handleShorten);
  elements.analyticsForm.addEventListener("submit", handleAnalyticsSubmit);
  elements.refreshUrlsButton.addEventListener("click", loadUrls);
  elements.urlsList.addEventListener("click", handleListClick);
  elements.createResult.addEventListener("click", handleListClick);
}

async function init() {
  bindEvents();
  updateSessionLabel();
  await checkHealth();
  await loadUrls();
}

init();
